import telebot
from telebot import types
import requests


API_TOKEN = 'YOUR_TOKEN'

GROUPS = {
    'python': {'chat_id': YOUR_CHAT_ID, 'topic_id': TOPIC_ID},
    'sql': {'chat_id': YOUR_CHAT_ID, 'topic_id':  TOPIC_ID},
    'java': {'chat_id': YOUR_CHAT_ID, 'topic_id':  TOPIC_ID},
    'helpful': {'chat_id': YOUR_CHAT_ID, 'topic_id':  TOPIC_ID},
    'c#': {'chat_id': YOUR_CHAT_ID, 'topic_id':  TOPIC_ID},
}


bot = telebot.TeleBot(API_TOKEN)

user_data = {}

class MyBot:
    def __init__(self, bot):
        self.bot = bot
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.reply_to(message, "Привет! Напиши 'Привет' и я отвечу.")

        @self.bot.message_handler(func=lambda message: message.chat.type == 'private' and message.text.lower() == 'привет')
        def handle_greeting(message):
            self.bot.reply_to(message, "Привет!")

        @self.bot.message_handler(func=lambda message: message.chat.type == 'private' and 'http' in message.text)
        def handle_link(message):
            user_data[message.from_user.id] = {'original_message': message.text}
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Python', 'SQL', 'Java', 'Helpful')
            msg = self.bot.send_message(message.chat.id, "Что это за информация?", reply_markup=markup)
            self.bot.register_next_step_handler(msg, ask_data_type)

        def ask_data_type(message):
            user_data[message.from_user.id]['data_info'] = message.text
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('course', 'article', 'tips', 'guide', 'video', 'book', 'trainer')
            msg = self.bot.send_message(message.chat.id, "К какому типу данных относится информация?", reply_markup=markup)
            self.bot.register_next_step_handler(msg, ask_language)

        def ask_language(message):
            user_data[message.from_user.id]['data_type'] = message.text
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('russian', 'english', 'spanish')
            msg = self.bot.send_message(message.chat.id, "На каком языке написана данная информация?", reply_markup=markup)
            self.bot.register_next_step_handler(msg, final_response)

        def final_response(message):
            user_data[message.from_user.id]['language'] = message.text
            original_message_text = user_data[message.from_user.id]['original_message']
            data_info = user_data[message.from_user.id]['data_info']
            data_type = user_data[message.from_user.id]['data_type']
            language = user_data[message.from_user.id]['language']
            hashtags = f"#{data_info.lower()} #{data_type.lower()} #{language.lower()}"
            new_message_text = f"{original_message_text}\n\n{hashtags}"

            first_hashtag = data_info.lower()
            group = GROUPS.get(first_hashtag)
            if group:
                chat_id = group['chat_id']
                topic_id = group['topic_id']
                self.send_message_to_topic(chat_id, topic_id, new_message_text)
            else:
                self.bot.send_message(message.chat.id, "Не удалось найти группу для указанного хэштега.")

    def send_message_to_topic(self, chat_id, topic_id, message_text):
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'message_thread_id': topic_id,
            'text': message_text
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send message: {response.content}")

    def run(self):
        self.bot.polling()

if __name__ == '__main__':
    my_bot = MyBot(bot)
    my_bot.run()
