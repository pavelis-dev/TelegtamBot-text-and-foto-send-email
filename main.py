import telebot
import settings  # отдельный файл settings.py с токеном, почтовыми адресами и паролем
from telebot import types

from os.path import basename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

mail = ''
user_message = ''
bot = telebot.TeleBot(settings.API_TOKEN)


def send_email(user_message, downloaded_file, name_photo):
    email_sender = settings.MAIL_sender  # почтовый адрес отправителя сообщения
    password = settings.password_sender  # пароль от почты отправителя
    email_getter = mail

    smtp_server = smtplib.SMTP('smtp.mail.ru', 587)  # или 465 (smtp.название почтового сервера.ru/com)
    smtp_server.starttls()

    mgs = MIMEMultipart()
    mgs.attach(MIMEText(user_message))

    file = MIMEApplication(downloaded_file, Name=basename(name_photo))
    mgs.attach(file)

    smtp_server.login(email_sender, password)
    smtp_server.sendmail(email_sender, email_getter, mgs.as_string())

    smtp_server.quit()


@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    if message.from_user.last_name is None:
        mess = f'Здравствуйте, <b>{message.from_user.first_name}</b>! Необходимо выбрать электронную почту' \
               f' для отправки сообщения.'
    else:
        mess = f'Здравствуйте, <b>{message.from_user.first_name} {message.from_user.last_name}</b>! Необходимо' \
               f' выбрать электронную почту для отправки сообщения.'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton(settings.MAIL1)  # получатель почта 1
    btn2 = types.KeyboardButton(settings.MAIL2)  # получатель почта 2
    btn3 = types.KeyboardButton(settings.MAIL3)  # получатель почта 3
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_user_text(message):
    global mail
    global user_message
    if message.chat.type == 'private':
        if message.text == settings.MAIL1:
            mail = settings.MAIL1
            bot.send_message(message.chat.id, 'Напишите текстовое сообщение для отправки')
        elif message.text == settings.MAIL2:
            mail = settings.MAIL2
            bot.send_message(message.chat.id, 'Напишите текстовое сообщение для отправки')
        elif message.text == settings.MAIL3:
            mail = settings.MAIL3
            bot.send_message(message.chat.id, 'Напишите текстовое сообщение для отправки')
        else:
            if mail == '':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                btn1 = types.KeyboardButton(settings.MAIL1)
                btn2 = types.KeyboardButton(settings.MAIL2)
                btn3 = types.KeyboardButton(settings.MAIL3)
                markup.add(btn1, btn2, btn3)
                bot.send_message(message.chat.id, 'Необходимо выбрать почту для отправки'
                                                  ' сообщения', reply_markup=markup)

            else:
                user_message = message.text
                bot.send_message(message.chat.id, 'Далее прикрепите фото')


@bot.message_handler(content_types=['photo'])
def get_user_photo(message):
    global mail
    if mail != '' and user_message != '':
        user_photo = message.json['photo'][-1]
        file_id = user_photo['file_id']
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        name_photo = file_info.file_path[7:]

        send_email(user_message, downloaded_file, name_photo)
        mail = ''
        bot.send_message(message.chat.id, 'Сообщение отправлено!')
    else:
        bot.send_message(message.chat.id, 'Необходимо выбрать электронную почту и/или написать текстовое сообщение')


if __name__ == '__main__':
    bot.infinity_polling()
