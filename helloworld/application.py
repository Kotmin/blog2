#!flask/bin/python
import json
from flask import Flask, Response
import optparse


from flask import Flask, render_template, abort, url_for, redirect, flash,send_from_directory
from pathlib import Path
import os
import logging

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField,DateField,IntegerField
from wtforms.validators import DataRequired, URL,NumberRange, Email,InputRequired
from flask_ckeditor import CKEditor, CKEditorField


from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_login import LoginManager


from wtforms import DecimalField


from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required

from functools import wraps



from datetime import datetime
from sqlalchemy.orm import relationship

import json

from wtforms.widgets import PasswordInput
from wtforms import PasswordField

# Get the path of the directory containing the current script
script_dir = Path(__file__).resolve().parent

# Path for files to download
# html_file_path = script_dir / "static/files/cheat_sheet.pdf"
# if __name__ == '__main__':
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY',os.urandom(32)) # added def value pref replace to .env solution

## pass for dummy acc: SQwd221eadx21 
# l" Paul
Bootstrap5(app)

login_manager = LoginManager()

login_manager.init_app(app)


#CKE Editor
ckeditor = CKEditor(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts_renewed2.db")
db = SQLAlchemy()
db.init_app(app)



# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    posts = db.relationship("BlogPost", back_populates="author")

# Rank model
class Rank(db.Model):
    id_rank = db.Column(db.Integer, primary_key=True)
    rank_name = db.Column(db.String(60), unique=True, nullable=False)
    users = db.relationship('UserRank', backref='rank')

# UserRank model (Many-to-Many relationship between User and Rank)
class UserRank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rank_id = db.Column(db.Integer, db.ForeignKey('rank.id_rank'), nullable=False)

# Permissions model (One-to-One relationship with Rank)
class Permissions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank_id = db.Column(db.Integer, db.ForeignKey('rank.id_rank'), unique=True, nullable=False)
    create_post = db.Column(db.Boolean, default=False)
    read_all_posts = db.Column(db.Boolean, default=False)
    update_posts = db.Column(db.Boolean, default=False)
    delete_posts = db.Column(db.Boolean, default=False)
    all_posts = db.Column(db.Boolean, default=False)
    add_user = db.Column(db.Boolean, default=False)
    user_edit = db.Column(db.Boolean, default=False)

# BlogPost model
class BlogPost(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    release_date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="posts")
    state_id = db.Column(db.Integer, db.ForeignKey("post_states.id"))
    state = db.relationship("BlogPostState", back_populates="posts")
    estimated_time_to_read = db.Column(db.Integer, nullable=True)
    last_modification = db.Column(db.String(250), nullable=False)
    attributes = db.relationship("Attribute", backref="post", lazy=True, cascade="all, delete-orphan")
    features = db.relationship("PostFeature", backref="post", lazy=True)


    def to_dict(self):
        return {column.name: getattr(self,column.name) for column in self.__table__.columns }

# Attribute model
class Attribute(db.Model):
    __tablename__ = "attributes"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    name = db.Column(db.Text, nullable=False)
    value = db.Column(db.JSON, nullable=False)  # Storing JSON data

# BlobType model
class BlobType(db.Model):
    __tablename__ = "blob_types"
    id = db.Column(db.Integer, primary_key=True)
    related_post_ids = db.Column(db.JSON)  # JSON array of post IDs if related to multiple posts
    data = db.Column(db.LargeBinary, nullable=False)  # Storing the binary data

# BlogPostState model
class BlogPostState(db.Model):
    __tablename__ = "post_states"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=False)
    posts = db.relationship("BlogPost", back_populates="state")

# PostFeature model
class PostFeature(db.Model):
    __tablename__ = "post_features"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # e.g., active, disabled, removed
    tags = db.Column(db.String(250))  # For SEO purposes
    unique_url = db.Column(db.String(250), unique=True, nullable=False)
    site_title = db.Column(db.String(250), unique=True, nullable=False)
    site_desc = db.Column(db.String(250), unique=True, nullable=False)

# Category model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    url_for_bg_img = StringField('URL', validators=[DataRequired()])
    body = CKEditorField('Body')

    release_date = DateField(
        "Release Date",
        format="%Y-%m-%d",  # Specify the format you want to display to users
        validators=[
              # To make the field required
        ],
        default= datetime.now()# Set the default value
    )

    estimated_time_to_read = IntegerField(r"Time needed for read",
                                validators=[DataRequired(),
                                            NumberRange(min=0,
                                                        max=360,
                                    message="Number must be in range(0,360)"),
                                                    ])

    category = SelectField(u"Category",choices=lambda: Category.query.all(),)
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    name =StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(),Email()])
    password = StringField('Password', widget=PasswordInput())
    submit = SubmitField("Submit")




class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')
    submit = SubmitField('Submit')



class DonationForm(FlaskForm):
    # Donation amount, with default value 0.00 and non-negative validation
    amount = DecimalField('Donation Amount', default=0.00, validators=[
        InputRequired(message='Donation amount is required.'),
        NumberRange(min=0, message='Donation amount must be non-negative.')
    ])


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if not current_user.is_authenticated or current_user.id != 1 : return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)        
    return decorated_function


@app.route('/')
def home():
    current_year = datetime.now().year
    posts = []

    posts = [post.to_dict() for post in BlogPost.query.all()]

    all_posts_json = json.dumps(posts)

    return render_template("index.html", all_posts=posts,curr_year = current_year,)



@app.route('/robots.txt')
def serve_robots_txt():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/category/<category>',methods = ['GET','POST'])
@admin_only
def add_category(category:str):
    new_category = Category(
        name = category.capitalize()
    )
    db.session.add(new_category)
    db.session.commit()

    return redirect(url_for('home'))


# User handle part



# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register',methods = ['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        
        new_user = User(

        name = form.name.data,
        email = form.email.data,
        password = generate_password_hash(str(form.password.data),
                                          method='pbkdf2:sha256',
                                          salt_length=8),)
        

        db.session.add(new_user)

        db.session.commit()

        login_user(new_user)
        return redirect(url_for('home'))#name=request.form.get('name')))
    
    return render_template("register.html",form=form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login',methods=['GET', 'POST'])
def login():
    form=LoginForm()
    
    if form.validate_on_submit():
        password = form.password.data

        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()

        if not user:
            flash('There is not such email addres corelated with account')

        else:
            # Check stored password hash against entered password hashed.
            if check_password_hash(user.password, password):
                login_user(user)

                # flash('Logged in successfully.')

    
                return redirect(url_for('home'))
            else:
                flash('Password incorrect, please try again.')
            
    return render_template("login.html",form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/new-post',methods=["GET","POST"])
@admin_only
def add_new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            date = datetime.now().strftime("%B %d, %Y"),
            title = form.title.data,
            subtitle = form.subtitle.data,
            img_url = form.url_for_bg_img.data,
            author_id = current_user.id, # here we have issue
            body = form.body.data,
            release_date = form.release_date.data.strftime("%B %d, %Y"),
            category = form.category.data,
            estimated_time_to_read = form.estimated_time_to_read.data,
            last_modification = datetime.now().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("make-post.html",form=form, default_mode='source')


@app.route('/<int:post_id>')
def show_post(post_id:int):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)

@app.route("/edit-post/<post_id>",methods = ['GET','POST'])
@admin_only
def edit_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = PostForm(
        title = requested_post.title,
        subtitle = requested_post.subtitle,
        url_for_bg_img = requested_post.img_url,
        # author = requested_post.author,
        body = requested_post.body,
        category = requested_post.category,
        estimated_time_to_read = requested_post.estimated_time_to_read,


    )

    if form.validate_on_submit():
        requested_post.title = form.title.data
        requested_post.subtitle = form.subtitle.data
        requested_post.img_url = form.url_for_bg_img.data
        requested_post.body = form.body.data    
        requested_post.category = form.category.data
        requested_post.estimated_time_to_read = form.estimated_time_to_read.data
        requested_post.last_modification = datetime.now().strftime("%B %d, %Y")
        db.session.commit()
        return redirect(url_for("home", post_id=requested_post.id))
    
    return render_template("make-post.html",form= form ,requested_post = requested_post, default_mode='source')

# @app.route('/add-feature/<int:post_id>')
# @admin_only
# def add_new_feature(post_id):
#     requested_post = db.get_or_404(BlogPost, post_id)
#     form = FeatureForm()
#     if form.validate_on_submit():
#         new_feature = BlogPostFeature(
#             last_modification = datetime.now().strftime("%B %d, %Y"),
#             estimated_time_to_read = form.estimated_time_to_read.data,
#             post_id = requested_post.id,
#             author = requested_post.author.id,
#         )
#         db.session.add(new_feature)
#         db.session.commit()

#         return redirect(url_for('show_post',post_id))

#     return render_template("make-post.html",form=form)

# @app.route('/edit-feature/<int:post_id>')
# @admin_only
# def edit_feature(post_id):
#     requested_post = db.get_or_404(BlogPostFeature, post_id)
#     form = FeatureForm(
#         estimated_time_to_read = requested_post.features.estimated_time_to_read
#     )

#     if form.validate_on_submit():
#         requested_post.last_modification = datetime.now().strftime("%B %d, %Y")
#         requested_post.estimated_time_to_read = form.estimated_time_to_read.data
#         db.session.commit()
#         return redirect(url_for("post-feature",post_id))


#     return render_template("make-post.html",form = form ,requested_post = requested_post)



@app.route('/delete/<post_id>')
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
            
    return redirect(url_for("home"))


from flask import request,jsonify

@app.route('/donate')
def donate_site():
    current_year = datetime.now().year
    pp_app_id = "ASEqoEQAojwZY0_oCFj6v9FJ_IltbwW_OwmXFNAvq_CtyykxI490PiiWXJpCSA-utBXazxJeqvsO-eQ7"
    return render_template("donate.html",curr_year = current_year,pay_pal_clientID=pp_app_id)

@app.errorhandler(404)
def err_not_found(e):
    return render_template('err_404.html')

import requests
import os

import base64
import uuid


# Auth stuff
default_value = ""

# Def PP route

PAYPAL_DEFAULT_ENDPOINT = "https://api-m.sandbox.paypal.com"

PP_ID = os.environ.get('PayPal_Client_ID',default_value)
PP_SECRET = os.environ.get('PayPal_Client_SECRET',default_value)

PP_CANCEL_URL = "https://example.com/cancelUrl"
PP_RETURN_URL = "https://example.com/returnUrl"


def get_access_token():
    endpoint = f"{PAYPAL_DEFAULT_ENDPOINT}/v1/oauth2/token"

    # Combine the client ID and client secret with a colon
    credentials = f'{PP_ID}:{PP_SECRET}'

    print(f"Client id:{PP_ID}")

    # Encode the credentials in Base64
    credentials_base64 = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')



    # Define the data to send
    data = {
        'grant_type': 'client_credentials',
    }

    # Define the headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
         "Authorization": f"Basic {credentials_base64}",
    }

    response = requests.post(endpoint,headers=headers,data=data)


    # Check the response
    if 200 <= response.status_code < 300:
        # Access token obtained successfully
        access_token = response.json()["access_token"]
        # print("Access token:", access_token)
        os.environ['PP_ACCES_T'] = access_token
        return access_token
    else:
        # Handle any errors
        print("Error obtaining access token:", response.status_code, response.text)
        logging.error(f"Error obtaining access token: {response.status_code} {response.text}")





@app.route('/my-server/create-paypal-order', methods=['POST'])
def create_paypal_order():



    try:
        data = request.get_json()


        amount = data['cart'][0]['quantity']
        amount = amount.replace(',','.')

        print(f"First val: {amount}")

        amount = float(amount)

        if amount is not None:
            if not (isinstance(amount, (float, int)) and 1 < amount <= 9999999999999):
                raise ValueError("Invalid amount value")
        else:
            raise ValueError("Amount field is missing")

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred"}), 500

## Regular API CALL working

    url = f"{PAYPAL_DEFAULT_ENDPOINT}/v2/checkout/orders"

    accessToken = os.environ.get('PP_ACCES_T',default_value)

    pp_request_id = str(uuid.uuid4())

    print(f"Request id: {pp_request_id}")

    headers = {
    'Content-Type': 'application/json',
    'PayPal-Request-Id': pp_request_id,
    'Authorization': f'Bearer {accessToken}',
    }

    #working datapayload
    # data = '{ "intent": "CAPTURE", "purchase_units": [ { "reference_id": "d9f80740-38f0-11e8-b467-0ed5f89f718b", "amount": { "currency_code": "PLN", "value": "'+str(round(amount,2))+'" } } ], "payment_source": { "paypal": { "experience_context": { "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED", "brand_name": "EXAMPLE INC", "locale": "en-US", "landing_page": "LOGIN", "user_action": "PAY_NOW", "return_url": "https://example.com/returnUrl", "cancel_url": "https://example.com/cancelUrl" } } } }'
    # data = '{ "intent": "CAPTURE", "purchase_units": [ { "reference_id": "d9f80740-38f0-11e8-b467-0ed5f89f718b", "amount": { "currency_code": "PLN", "value": "100.01" } } ], "payment_source": { "paypal": { "experience_context": { "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED", "brand_name": "EXAMPLE INC", "locale": "en-US", "landing_page": "LOGIN", "user_action": "PAY_NOW", "return_url": "https://example.com/returnUrl", "cancel_url": "https://example.com/cancelUrl" } } } }'

    # dot is nessesary

    # Test prompt
    amount = str(amount)
    data = '{ "intent": "CAPTURE", "purchase_units": [ {"amount": { "currency_code": "PLN", "value": "' + amount +'" } } ] }'
    response = requests.post(f'{PAYPAL_DEFAULT_ENDPOINT}/v2/checkout/orders', headers=headers, data=data)


    if 200 <= response.status_code < 300:
# Order successfully captured
        print("Order created successfully.")
    else:
        # Handle any errors
        print("Error capturing the order:", response.status_code, response.text)


    data = response.json()


    return {'id': data['id'],
            'request_id':pp_request_id,
            }

@app.route('/my-server/capture-paypal-order', methods=['POST'])
def capture_paypal_order():
    data = request.get_json()
    order_id = data['orderID'] # probably .get would be better
    print(f'In capture{data}')

    # print(f'In capture order_id {order_id}')
    # New approach
    accessToken = os.environ.get('PP_ACCES_T',default_value)
    url =f"{PAYPAL_DEFAULT_ENDPOINT}/v2/checkout/orders/{order_id}/capture"

    headers = {
        'Content-Type': 'application/json',
         "Authorization": f"Bearer {accessToken}",
    }

    print(f'\nCaptured:\n{order_id}')


# Make the POST request to capture the order
    response = requests.post(url, headers=headers)

# Check the response
    if response.status_code == 201:
    # Order successfully captured
        print("Order captured successfully.")
        return response.json()
    else:
        # Handle any errors
        print("Error capturing the order:", response.status_code, response.text)






if __name__ == '__main__':
    default_port = "5000"
    default_host = "0.0.0.0"
    parser = optparse.OptionParser()
    parser.add_option("-H", "--host",
                      help=f"Hostname of Flask app {default_host}.",
                      default=default_host)

    parser.add_option("-P", "--port",
                      help=f"Port for Flask app {default_port}.",
                      default=default_port)

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()

    app.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )
