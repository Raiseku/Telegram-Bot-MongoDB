### Importing necessary libraries

import configparser # pip install configparser
from telethon import TelegramClient, events # pip install telethon
from datetime import datetime
from pymongo import MongoClient # pip install pymongo[srv]
from bson.objectid import ObjectId # pip install bson

### Initializing Configuration
print("Initializing configuration...")
config = configparser.ConfigParser()
config.read('config.ini')

# Read values for Telethon and set session name
API_ID = config.get('default','api_id') 
API_HASH = config.get('default','api_hash')
BOT_TOKEN = config.get('default','bot_token')
session_name = "sessions/Bot"

# Read values for MySQLdb
USERNAME = config.get('default', 'username')
PASSWORD = config.get('default', 'password')
DATABASE_NAME = config.get('default', "db_name")
COLLECTION_NAME = config.get('default', "collection_name")

# Start the Client (telethon)
client = TelegramClient(session_name, API_ID, API_HASH).start(bot_token=BOT_TOKEN)



# Start the Client (MongoDB)
url = # Put your link of MongoDB cluster here!
cluster = MongoClient(url)


### START COMMAND
@client.on(events.NewMessage(pattern="(?i)/start"))
async def start(event):
    # Get sender
    sender = await event.get_sender()
    SENDER = sender.id

    # send notification message
    text = "Hello i am a bot that can do CRUD operations inside MongoDB!"
    await client.send_message(SENDER, text)


### Insert command
#/insert [product_name] [quantity] [status]
@client.on(events.NewMessage(pattern="(?i)/insert"))
async def insert(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")

    name = list_of_words[1] # the second (1) item is the product
    quantity = int(list_of_words[2]) # the third (2) item is the quantity
    status = list_of_words[3] # the fourth (3) item is the status: "P" for Production, "S" for Selling, "R" for Recycle
    dt_string = datetime.now().strftime("%d-%m-%y") # Use the datetime library to the get the date (and format it as DAY/MONTH/YEAR)
    post_dict = {"product_name": name, "quantity": quantity, "status": status, "LAST_UPDATE": dt_string}

    # Execute insert query
    products.insert_one(post_dict)
    
    # send notification message
    text = "Order correctly inserted!"
    await client.send_message(SENDER, text, parse_mode='html')
        

### SELECT COMMAND
# Print function
def create_message_select_query(ans):
    text = ""
    for res in ans:
        if(res != []):
            id = res["_id"]
            name = res["product_name"]
            quantity = res["quantity"]
            status = res["status"]
            creation_date = res["LAST_UPDATE"]
            text += "<b>"+ str(id) +"</b> | " + "<b>"+ str(name) +"</b> | " + "<b>"+ str(quantity)+"</b> | " + "<b>"+ str(status)+"</b> | " + "<b>"+ str(creation_date)+"</b>\n"
    message = "<b>Received 📖 </b> Information about products:\n\n"+text
    return message


# Command
@client.on(events.NewMessage(pattern="(?i)/select"))
async def select(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")

    if(len(list_of_words) > 1):
        name = list_of_words[1] # the second (1) item is the product

        # Execute find query
        results = products.find({"product_name":name})

        # send notification message
        text = create_message_select_query(results)
        await client.send_message(SENDER, text, parse_mode='html')
        
    else:
        # Execute find query
        results = products.find({})

        # send notification message
        text = create_message_select_query(results)
        await client.send_message(SENDER, text, parse_mode='html')



### UPDATE COMMAND
# /update [_id] [new_product_name] [new_quantity] [new_status]
@client.on(events.NewMessage(pattern="(?i)/update"))
async def update(event):
    # Get the sender
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")

    _id = ObjectId(list_of_words[1]) # The second (1) item is the _id.  We must cast the string to ObjectId 
    name = list_of_words[2] # the third (2) item is the product name
    quantity = int(list_of_words[3]) # the fourth (3) item is the quantity
    status = list_of_words[4] # the fourth (3) item is the status: "P" for Production, "S" for Selling, "R" for Recycle
    dt_string = datetime.now().strftime("%d-%m-%y") # Use the datetime library to the get the date (and format it as DAY/MONTH/YEAR )
    new_post_dict = {"product_name": name, "quantity": quantity, "status": status, "LAST_UPDATE": dt_string}
    
    # Execute update query
    products.update_one({"_id":_id}, {"$set": new_post_dict})

    # send notification message
    text = "Product with _id {} correctly updated".format(_id)
    await client.send_message(SENDER, text, parse_mode='html')


### DELETE COMMAND
@client.on(events.NewMessage(pattern="(?i)/delete"))
async def delete(event):

    # Get the sender
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")
    _id = ObjectId(list_of_words[1]) # The second (1) item is the _id. We must cast the string to ObjectId 

    # Execute delete query
    products.delete_one({"_id": _id})

    # send notification message
    text = "Product with _id {} correctly deleted".format(_id)
    await client.send_message(SENDER, text, parse_mode='html')




# Command

# /selectIn state P S
@client.on(events.NewMessage(pattern="(?i)/in"))
async def select(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")

    if(len(list_of_words) > 1):
        field = list_of_words[1] # the second (1) item is the product
        values_to_check = list_of_words[2:]
        
        params = {field: {"$in": values_to_check}}
        results = products.find(params)
        print(results)

        # send notification message
        text = create_message_select_query(results)
        await client.send_message(SENDER, text, parse_mode='html')







##### MAIN
if __name__ == '__main__':
    try:
        print("Initializing Database...")
        # Define the Database using Database name
        db = cluster[DATABASE_NAME]
        # Define collection
        products = db[COLLECTION_NAME]

        print("Bot Started...")
        client.run_until_disconnected()

    except Exception as error:
        print('Cause: {}'.format(error))