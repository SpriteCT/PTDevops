import logging
import re
import paramiko
import psycopg2
import os

from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

TOKEN = os.environ["TOKEN"]
host = os.environ["RM_HOST"]
port = os.environ["RM_PORT"]
username = os.environ["RM_USER"]
password = os.environ["RM_PASSWORD"]

db_name = os.environ["DB_DATABASE"]
db_user = os.environ["DB_USER"]
db_password =os.environ["DB_PASSWORD"]
db_port = os.environ["DB_PORT"]
db_host = os.environ["DB_HOST"]

Emails = []
Phones = []


# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text

    phoneNumRegex = re.compile(r"(\+7|8)(\s\(|[\s\-\(])?(\d{3})(\)\s|[\s\-\)])?(\d{3})([\s\-])?(\d{2})([\s\-])?(\d{2})")

    phoneNumberList = phoneNumRegex.findall(user_input)
    context.chat_data['phones'] = []
    for i in phoneNumberList:
        context.chat_data['phones'].append(''.join(i))

    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    phoneNumbers = ''
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {"".join(phoneNumberList[i])}\n'

    update.message.reply_text(phoneNumbers)
    update.message.reply_text('Вы хотите добавить данные номера в БД? (Да/Нет)')
    return 'addPhoneNumbers'
def addPhoneNumbers(update: Update, context):
    user_input = update.message.text
    if 'Нет' in user_input:
        update.message.reply_text('Номера не будут добавлены')
        return ConversationHandler.END
    elif 'Да' in user_input:
        try:
            connection = psycopg2.connect(user=db_user,
                                          password=db_password,
                                          host=db_host,
                                          port=db_port,
                                          database=db_name)

            cursor = connection.cursor()
            for i in context.chat_data['phones']:
                cursor.execute("INSERT INTO phones (phone) VALUES ('" + i + "')")
            connection.commit()
            update.message.reply_text('Номера добавлены')
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
                return ConversationHandler.END
    

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для адресов почты: ')

    return 'findEmail'


def findEmail(update: Update, context):
    user_input = update.message.text

    emailsRegex = re.compile(r"[\w]+@[\w]+\.\w{1,4}")

    emailsList = emailsRegex.findall(user_input)
    context.chat_data['emails'] = emailsList

    if not emailsList:
        update.message.reply_text('Адреса почты не найдены')
        return ConversationHandler.END

    emailAdresses = ''
    for i in range(len(emailsList)):
        emailAdresses += f'{i + 1}. {"".join(emailsList[i])}\n'

    update.message.reply_text(emailAdresses)
    update.message.reply_text('Вы хотите добавить данные адреса в БД? (Да/Нет)')
    return 'addEmail'

def addEmail(update: Update, context):
    user_input = update.message.text
    if 'Нет' in user_input:
        update.message.reply_text('Адреса не будут добавлены')
        return ConversationHandler.END
    elif 'Да' in user_input:
        try:
            connection = psycopg2.connect(user=db_user,
                                          password=db_password,
                                          host=db_host,
                                          port=db_port,
                                          database=db_name)

            cursor = connection.cursor()
            for i in context.chat_data['emails']:
                cursor.execute("INSERT INTO emails (email) VALUES ('" + i + "')")
            connection.commit()
            update.message.reply_text('Адреса добавлены')
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Соединение с PostgreSQL закрыто")
                return ConversationHandler.END


def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль на проверку: ')

    return 'verifyPassword'


def verifyPassword(update: Update, context):
    user_input = update.message.text

    reg_expression = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%^&*\(\)]).{8,}$')
    password_check = reg_expression.search(user_input)
    if password_check:
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    return ConversationHandler.END



def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}! Введи /help , чтобы увидеть список команд')


def helpCommand(update: Update, context):
    update.message.reply_text('''Проверка почты
Команда: '/find_email'

Проверка телефона
Команда: '/find_phone_number'

Проверка пароля
Команда: '/verify_password'

О релизе.
Команда: `/get_release`

Об архитектуры процессора, имени хоста системы и версии ядра.
Команда: `/get_uname`

О времени работы.
Команда: `/get_uptime`

Сбор информации о состоянии файловой системы.
Команда: `/get_df`

Сбор информации о состоянии оперативной памяти.
Команда: `/get_free`

Сбор информации о производительности системы.
Команда: `/get_mpstat`

Сбор информации о работающих в данной системе пользователях.
Команда: `/get_w`

Последние 10 входов в систему.
Команда: `/get_auths`

Последние 5 критических события.
Команда: `/get_critical`

Сбор информации о запущенных процессах.
Команда: `/get_ps`

Сбор информации об используемых портах.
Команда: `/get_ss`

Сбор информации об установленных пакетах.
Команда: `/get_apt_list`

Сбор информации о запущенных сервисах.
Команда: `/get_services`

Команда: /get_apt_list

Команда: /get_repl_logs

Команда: /get_emails

Команда: /get_phones''')
def execCommand(command):
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        return data[:4095]

def getRelease(update: Update, context):
    update.message.reply_text(execCommand('cat /etc/os-release'))
def getUname(update: Update, context):
    update.message.reply_text(execCommand('uname -a'))
def getUptime(update: Update, context):
    update.message.reply_text(execCommand('uptime'))
def getDf(update: Update, context):
    update.message.reply_text(execCommand('df'))

def getFree(update: Update, context):
    update.message.reply_text(execCommand('free'))
def getMpstat(update: Update, context):
    update.message.reply_text(execCommand('mpstat'))

def getDf(update: Update, context):
    update.message.reply_text(execCommand('df'))
def getW(update: Update, context):
    update.message.reply_text(execCommand('w'))

def getAuths(update: Update, context):
    update.message.reply_text(execCommand('cat /var/log/auth.log'))

def getCritical(update: Update, context):
    update.message.reply_text(execCommand('cat /var/log/syslog'))

def getPs(update: Update, context):
    update.message.reply_text(execCommand('ps'))

def getSs(update: Update, context):
    update.message.reply_text(execCommand('ss'))

def getService(update: Update, context):
    update.message.reply_text(execCommand('service --status-all'))

def getAptList(update: Update, context):
    update.message.reply_text(execCommand('apt list --installed'))

def getReplLogs(update: Update, context):
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=db_host, username='root', password='root123', port=port)
        stdin, stdout, stderr = client.exec_command("cat /var/lib/postgresql/data/log/main.log | grep replic")
        data = stdout.read() + stderr.read()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data)

def getEmails(update: Update, context):
    try:
        connection = psycopg2.connect(user=db_user,
                                          password=db_password,
                                          host=db_host,
                                          port=db_port,
                                          database=db_name)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails")
        data = cursor.fetchall()
        emails = []
        for row in data:
            emails.append(str(row[0]) + '. ' + row[1])
        update.message.reply_text('\n'.join(emails))
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")
def getPhones(update: Update, context):
    try:
        connection = psycopg2.connect(user=db_user,
                                          password=db_password,
                                          host=db_host,
                                          port=db_port,
                                          database=db_name)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phones")
        data = cursor.fetchall()
        emails = []
        for row in data:
            emails.append(str(row[0]) + '. ' + row[1])
        update.message.reply_text('\n'.join(emails))
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'addPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, addPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'addEmail': [MessageHandler(Filters.text & ~Filters.command, addEmail)],
        },
        fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(CommandHandler("get_services", getService))
    dp.add_handler(CommandHandler("get_apt_list", getAptList))
    dp.add_handler(CommandHandler("get_repl_logs", getReplLogs))
    dp.add_handler(CommandHandler("get_emails", getEmails))
    dp.add_handler(CommandHandler("get_phones", getPhones))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
