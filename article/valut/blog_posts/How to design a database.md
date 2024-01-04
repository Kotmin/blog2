at least how to try

## Database Modeling: An Art and Science

Today, I'd like to present to you one of the databases my friends and I have modeled. The subject was an online store.

### Many Paths, One Goal

Some believe that creating a database should start with one massive table containing everything necessary. Only later should we divide it into smaller entities. Personally, I prefer the approach of "let's build a story and create a schema in harmony with it."

### No Panacea, but...

Granted, it's nearly impossible to design a one-size-fits-all database that perfectly suits every purpose. Nevertheless, our topic is quite broad, as our store could be anything from an online candy shop to a specialized bike screw retailer, so we'll begin with a product.

As a computer scientist, I'll try to theorize a bit. What exactly is a product? Is it something you can hold in your hand? Not necessarily. We sell digital audiobooks, so we must consider:

- How many audiobooks can a storekeeper handle at once?
- I'm not sure, but I can guess.

PLACEHOLDER FOR PRODUCT


Nevertheless, information about the quantity we possess might come in handy. We'd also like to know the price of a product, a general name, and perhaps a description. And what if, for instance, we were selling cell phones? Even if they share the same name, they might come in different colors or with varying specifications. So, we introduce two more tables: Model and Attribute. Model is straightforward, but why Attribute? Attributes become handy when a model can't accommodate the necessary details. This division also makes searching easier. When combined with categories, attribute-based searches can significantly improve our work.

### A Touch of Humanity

Now that we have our product, to fulfill our main goal - making MONEY - we need someone to supply this raw material. We need a HUMAN. Well, at least their digital representation. These "humans" can also be quite lazy. They might want easy access to their order history without manually inputting their data. We, on the other hand, might want to know whether they are individual or corporate clients and to which country we should send their purchases. Why do we need all this? Partly for statistics, partly to increase profits, maybe out of curiosity, and certainly because the law demands it.

PLACEHOLDER FOR USER

Almost "accidentally," we've also modeled a simple permission assignment system. The table "AdminRank" has a slightly misfitting name. In hindsight, "Ranks" would have been a much better choice. Well, the system is inspired by the UNIX solution. After all, we don't want just any employee to have administrator permissions, right?

### The Most Crucial Part: Building Bridges

We have a product and a user. Now, it would be nice to let them meet. Let's give them a digital shopping cart and set them on their way. Let them spend money with us. There remain a few implementation questions, such as "how often should these virtual shopping carts be cleared?" and the same goes for the expiration time of permissions. I'm aware of these questions, but let's find the answers another time.

PLACEHOLDER FOR ORDER HEADER

Let's return to the case at hand. In this context, we have three tables: "OrderStatus," "DeliveryMethod," and "PaymentMethod." Someone might suggest, "Why not use a simple enum for this?" What if we didn't support pigeon post deliveries for a certain country? This division allows for greater flexibility. Every order can be unique, and we must store it at a specific point in time, independent of the state of other tables. This ensures that a change, say in the price of those bike screws, won't affect orders already completed in the past.

## In Conclusion

I hope that the unwritten part of this story is softly whispered by the schema itself. There's no need to explain everything in painstaking detail when the code is clean. Do you have doubts? Ideas on how to improve it? Did I make a mistake? Feel free to reach out! 😸

Please feel free to share any additional details or changes you'd like to see!

![https://user-images.githubusercontent.com/70173732/152618901-9c4ab1cb-c885-4361-a1a3-3f34ce8a3d0a.png](https://user-images.githubusercontent.com/70173732/152618901-9c4ab1cb-c885-4361-a1a3-3f34ce8a3d0a.png)

Link to GitHub Project: LINK

https://github.com/Kotmin/A_ShopDB
