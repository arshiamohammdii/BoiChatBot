from click import command
from telebot import TeleBot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                        ReplyKeyboardRemove)
from database import Message, engine, User
from sqlalchemy.orm import sessionmaker


API_TOKEN = '5160093648:AAF02pSKyg_lpd97PeXp-KrxGKFfIUK0C2E'
bot = TeleBot(API_TOKEN)

Session = sessionmaker(bind=engine)
session = Session()
pending_message = False
user = None
"""
start handler:
    
    -check for query parameter
    -extract the query parameter
    -check for the user in database
    -if user exists -> welcome message and ...
    -if user not exists -> create one and reply them with +
        the default welcome message
    -and show them the keyboard

"""
def extract_parameter(text):
    value = text
    try:
        value = text.text.split()[1]
    except IndexError:
        value = None

    return value

def cancel_markup(text="انصراف"):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton(text))
    return markup
    
def query_user(user, session, uuid):
    user = session.query(user).filter(user.uuid == uuid).first()
    return user

def save_user(message, session):
    user = User(name=message.chat.first_name, username=message.chat.username,\
                chat_id=message.chat.id)
    session.add(user)
    session.commit()
    session.close()

def save_message(message, user_id, session):
    message_sent = Message(content_id=message.id, sender_username=message.chat.username, user_id=user_id)
    session.add(message_sent)
    session.commit()
    session.close()

def query_message(user, session, message):
    message_user = session.query(message).filter(message.user.id == user.id, message.read == False).all()


@bot.message_handler(commands=["start", "help"])
def start(message):
    global user, pending_message
    parameter = extract_parameter(message)
    # save_user(message, session)
    user = query_user(User, session, parameter)
    bot.copy_message(user.chat_id, message.chat.id, 283)
    if user is None:
        bot.send_message(message.chat.id, "user you are trying to reach\
        is not reachable")
    else:
        #to-do: send message to the user (copy message)
        pending_message = True
        bot.send_message(message.chat.id, "☝️ در حال پاسخ دادن به فرستنده این\
                         پیام هستی ... ؛ منتظریم بفرستی :)",\
                         reply_markup=cancel_markup())
              
@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def send_anonymous_message(message):
    global user
    global pending_message
    
    if pending_message:
        print("is this working?")
        save_message(message, user.id, session)
        # bot.copy_message(user.chat_id, message.chat.id, message.id)
        bot.send_message(user.chat_id, "شما یک پیام ناشناس دارید!!")
    if message.text == "انصراف":
        markup = ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "حاه! \n چه کاری برات انجام\
                         بدم؟", reply_markup=markup)
        pending_message = False


@bot.message_handler(commands=['new_mesg']):
def new_mesg(message):
    pass


bot.infinity_polling()







