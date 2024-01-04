import markdown


from bs4 import BeautifulSoup
from flask import Flask, render_template,render_template_string

from pathlib import Path

import re
import shutil




script_dir = Path(__file__).resolve().parent

FROM_FILE = script_dir / 'article/valut/blog_posts/The 6 Greatest Games Ever.md'
T0_FILE = script_dir / 'article/games-of-all-time.html'


VALUT_RESOURCES = script_dir / 'article/valut/blog_posts'

STATIC_FILE_STORAGE = script_dir / 'static/res'

# Regular expression to find image names
image_pattern = r"!\[Pasted image (.*?)\]"






with open(FROM_FILE, 'r') as f:
    tempMd= f.read()
    # print(tempMd)


def extract_code_snippets_from_md(md_file):
    # Read the content of the Markdown file
    with open(FROM_FILE, 'r') as f:
        md_content = f.read()

    # Regular expression to match code blocks
    code_pattern = r"```([a-zA-Z]+)\n(.*?)```"

    # Find all code blocks in the Markdown content
    code_snippets = re.finditer(code_pattern, md_content, re.DOTALL)

    # Initialize a list to store code snippet information
    code_list = []

    for i, code_snippet in enumerate(code_snippets, start=1):
        # Extract code information from the match
        code_language = code_snippet.group(1)
        code_content = code_snippet.group(2).strip()
        code_name = "Script"  # Default name if no previous line
        # Look for the name of the code snippet in the previous line
        previous_line = code_snippet.start() - 1
        match = re.search(r"^(.*[^ ])?```", md_content[:previous_line][::-1])
        if match:
            code_name = match.group(1)[::-1].strip()

        # Add code snippet information to the list
        code_list.append({
            "script_name": code_name,
            "code_language": code_language.lower(),
            "code_content": code_content
        })

        # Replace the code block with a placeholder
        md_content = md_content[:code_snippet.start()] + f"code_snippet{i}" + md_content[code_snippet.end():]

    return code_list, md_content




# def replace_code_snippets_in_html(html_content, rendered_snippets):
#     soup = BeautifulSoup(html_content, 'html.parser')

#     # Find all <p> tags with placeholders
#     placeholder_tags = soup.find_all('p',re.compile(r"code_snippet"))

#     for p_tag in placeholder_tags:
#         # Extract the placeholder value (e.g., code_snippet1, code_snippet2)
#         placeholder_value = p_tag.text.strip()
#         snippet_number = int(placeholder_value.split('code_snippet')[1])
#         # Find the corresponding rendered HTML snippet by index
#         if 0 < snippet_number <= len(rendered_snippets):
#             rendered_snippet = rendered_snippets[snippet_number - 1]

#             print(f"\n Snippet: \n{rendered_snippet}\n")
#             # Replace the <p> tag with the rendered HTML snippet
#             p_tag.replace_with(BeautifulSoup(rendered_snippet, 'html.parser'))

#     # Get the updated HTML content
#     updated_html_content = str(soup)

#     return updated_html_content


def replace_code_snippets_placeholders(html_content, rendered_snippets):
    # Replace placeholders with rendered snippets
    for i, snippet in enumerate(rendered_snippets, 1):
        pattern = re.compile(fr'<p>code_snippet{i}</p>')
        html_content = re.sub(pattern, snippet, html_content)

    return html_content

code_snippets, updated_md_content = extract_code_snippets_from_md(FROM_FILE)


def find_all_images_in_html(html_content):
    # Regular expression to find image names
    # image_pattern = r"!\[\[Pasted image (.*?)\]\]" # working

    image_pattern = r"!\[\[Pasted image (.*?)\]\]"

    # Find all image names in the HTML string
    all_local_images = re.findall(image_pattern, html_content)
    print(len(all_local_images)) # 0?

    print(all_local_images)

    return all_local_images

def import_all_images(html_content,image_list):

    # Process each image
    for image_name in image_list:
        image_name = 'Pasted image '+image_name

        source_image = VALUT_RESOURCES / image_name
        destination_image = STATIC_FILE_STORAGE / image_name

        # Check if the image already exists in STATIC_FILE_STORAGE
        if destination_image.is_file():
            print(f"Copy failed, image with name {image_name} already exists in PATH_B")
        else:
            # Copy the image from VALUT_RESOURCES to STATIC_FILE_STORAGE
            shutil.copy(source_image, destination_image)

    # Replace image references in the HTML string
    for image_name in image_list:
        image_name = 'Pasted image '+image_name
        image_tag = f"""
        <div class="image-container centered-img">
            <img src="{'static/res/' + image_name}" alt="" class="centered-img">
             <!-- <p class="image-text">Image Caption</p> -->
        </div>
        """
        html_content = re.sub(r"!\[\[" + re.escape(image_name) + r"\]\]", image_tag, html_content)


                                # r"!\[\[Pasted image (.*?)\]\]"
    return html_content


# Convert the input to HTML
tempHtml = markdown.markdown(updated_md_content)

print(tempHtml)





app = Flask(__name__)

@app.route('/')
def index():
    script_name = "My Python Script2"
    code_language = "python"
    code_content = "print('Hello, World!')"

    template_content = render_template('programmer-container.html', script_name=script_name, language=code_language, code_content=code_content)
    rendered_content = render_template_string(template_content)


    rendered_snippets = []

    for snippet in code_snippets:
        template_content = render_template('programmer-container.html', script_name=snippet["script_name"], language=snippet["code_language"], code_content=snippet["code_content"])
        rendered_content = render_template_string(template_content)
        rendered_snippets.append(rendered_content)

    # Working zone
  

    updated_html_content = replace_code_snippets_placeholders(tempHtml, rendered_snippets)

    updated_html_content = import_all_images(updated_html_content,find_all_images_in_html(updated_html_content))



    with open(T0_FILE, 'w', encoding='utf-8') as file:
        file.write(updated_html_content)

    return render_template('programmer-container.html', script_name=script_name, language=code_language, code_content=code_content)
     


app.run()