import telebot
from telebot import types
import os

token = os.environ["TOKEN"]

bot = telebot.TeleBot(token)

room_spectators = []
guest_id = None
host_id = None

activity_first_q = False
activity_second_q = False
activity_interview_started = False

class Question:
    def __init__(self, id, question, answer=None):
        self.id = id
        self.text = question
        self.answer = answer

class User:
    def __init__(self, id, first_name, last_name, first_q=None, second_q=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.first_q = first_q
        self.second_q = second_q

questions = [
    Question(1, "Как бы ты коротко описал себя?"),
    Question(2, "Кем ты мечтал стать в детстве?"),
    Question(3, "Есть ли у тебя талант или навык, которым ты гордишься?"),
    Question(4, "Какие у тебя есть сильные стороны по твоему мнению?"),
    Question(5, "Что бы ты хотел улучшить в себе?"),
    Question(6, "Как ты справляешься со стрессом в напряжённых ситуациях?"),
    Question(7, "Как ты обычно проводишь свободное время?"),
    Question(8, "Что тебе нравится в людях?"),
    Question(9, "Какие качества в своих друзьях ты ценишь?"),
    Question(10, "Нравится ли тебе учёба в университете?"),
    Question(11, "Как ты относишься к соседям в общежитии?"),
    Question(12, "К кому из друзей ты испытываешь наибольшее уважение?"),
    Question(13, "Что тебя вдохновляет в твоей девушке?"),
    Question(14, "Как ты думаешь, кто оказал на тебя наибольшее влияние?"),
    Question(15, "На каком музыкальном инструменте тебе больше всего нравится играть?"),
    Question(16, "На каком музыкальном инструменте ты лучше всего играешь по твоему мнению?"),
    Question(17, "Если бы ты мог изменить что-то в своей жизни в прошлом, что бы это было?"),
    Question(18, "В какой компании ты бы хотел работать?"),
    Question(19, "Что для тебя важнее всего в жизни?"),
    Question(20, "Какие планы у тебя на ближайшее будущее?")
]


@bot.message_handler(commands=['start'])
def handle_start(message):
    if check_user(message.chat.id) == 4:
        print(f"{message.chat.first_name} вошёл в бот (/start)")
        bot.send_message(message.chat.id, f"Привет, {message.chat.first_name}! Введи номер комнаты (узнай его у Юры):")


@bot.message_handler(commands=['log_ok_log'])
def handle_log(message):
   global guest_id, host_id, room_spectators
   room_spec_str = "room_spectators:\n"
   count = 0
   for i in room_spectators:
       count += 1
       room_spec_str += f"{count}. {i.first_name} {i.last_name} ({i.id})\n"
   bot.send_message(message.chat.id, room_spec_str)
   bot.send_message(message.chat.id, f"guest_id: {guest_id}")
   bot.send_message(message.chat.id, f"host_id: {host_id}")


@bot.message_handler(commands=['thanks']) 
def handle_thanks(message):
    global guest_id, host_id, room_spectators
    if check_user(message.chat.id) == 3:
        for i in room_spectators:
            bot.send_message(i.id, f"Спасибо тебе большое за участие в активности, {i.first_name}!")
            bot.send_message(i.id, f"Бот разработан @nippyfox при помощи 💻, ✋🏻 и 💖")
        if host_id is not None:
            bot.send_message(host_id, f"Спасибо тебе большое за участие в активности, шонич!")
            bot.send_message(host_id, f"Бот разработан @nippyfox при помощи 💻, ✋🏻 и 💖")
        if guest_id is not None:
            bot.send_message(guest_id, f"Спасибо тебе большое за участие в активности, {message.chat.first_name}!")
            bot.send_message(guest_id, f"Бот разработан @nippyfox при помощи 💻, ✋🏻 и 💖")


@bot.message_handler(content_types="text")
def answer_for_msg(message):
    global guest_id, host_id, room_spectators, activity_first_q, activity_second_q, activity_interview_started
    if activity_first_q == False and activity_second_q == False and activity_interview_started == False:
        # Присоединение к комнате, пользователя нет ни в одной из комнат
        if check_user(message.chat.id) == 4 and message.text == "54321":
            print(f"Присоединился {message.chat.first_name} {message.chat.last_name}")
            bot.send_message(message.chat.id, "Ура, добро пожаловать! Расслабься и жди дальнейших указаний!😉")
            room_spectators.append(User(message.chat.id, message.chat.first_name, message.chat.last_name))
            print(f"В spectators {len(room_spectators)} человек")
            
        # Присоединение отвечающего на вопросы интервью
        if check_user(message.chat.id) == 4 and message.text == "nippyfox-admin":
            print("Присоединился гость")
            start_guest_keyboard = types.InlineKeyboardMarkup(row_width=2)
            start_1st_button = types.InlineKeyboardButton("Запустить", callback_data="start_first")
            info_button = types.InlineKeyboardButton("Информация", callback_data="check_roommates")
            start_guest_keyboard.add(start_1st_button, info_button)
            bot.send_message(message.chat.id, "Добро пожаловать, готовься отвечать на вопросики!", reply_markup=start_guest_keyboard)
            guest_id = message.chat.id
            
        # Присоединение задающего вопросы интервью
        if check_user(message.chat.id) == 4 and message.text == "host-room":
            print("Присоединился ведущий")
            bot.send_message(message.chat.id, "Добро пожаловать, готовься задавать вопросики!")
            host_id = message.chat.id
    elif activity_first_q == True:
        if check_user(message.chat.id) == 1:
            new_answer_from_user = message.text
            user_id = message.chat.id
            for user in room_spectators:
                if user.id == user_id:
                    user.first_q.answer = new_answer_from_user
                    with open("log.txt", "a") as file:
                        file.write(f"\n\n{user.first_name} {user.last_name}\n{user.first_q.text}\n{new_answer_from_user}\n")
            bot.send_message(message.chat.id, "Твой ответ на первый вопрос принят!😊")
            print(f"Был получен ответ от {message.chat.first_name} {message.chat.last_name}!")
        elif check_user(message.chat.id) == 3:
            count_first_q_not_none = 0
            for user in room_spectators:
                if user.first_q.answer is None:
                    count_first_q_not_none += 1
            bot.send_message(message.chat.id, f"Мы не получили ответ от {count_first_q_not_none} зрителей")
    elif activity_second_q == True:
        if check_user(message.chat.id) == 1:
            new_answer_from_user = message.text
            user_id = message.chat.id
            for user in room_spectators:
                if user.id == user_id:
                    user.second_q.answer = new_answer_from_user
                    with open("log.txt", "a") as file:
                        file.write(f"\n\n{user.first_name} {user.last_name}\n{user.second_q.text}\n{new_answer_from_user}\n")
            bot.send_message(message.chat.id, "Твои ответы приняты! Спасибо большое🥰")
            print(f"Был получен ответ от {message.chat.first_name} {message.chat.last_name}!")
        elif check_user(message.chat.id) == 3:
            count_second_q_not_none = 0
            for user in room_spectators:
                if user.second_q.answer is None:
                    count_second_q_not_none += 1
            bot.send_message(message.chat.id, f"Мы не получили ответ от {count_second_q_not_none} зрителей")
    elif activity_interview_started == True:
        if check_user(message.chat.id) == 3:
            if message.text in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                index = int(message.text) - 1
                bot.send_message(host_id, room_spectators[index].first_q.text)
                bot.send_message(guest_id, room_spectators[index].first_q.text)
                bot.send_message(guest_id, room_spectators[index].first_q.answer)
            elif message.text in ["11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]:
                index = int(message.text) - 11
                bot.send_message(host_id, room_spectators[index].second_q.text)
                bot.send_message(guest_id, room_spectators[index].second_q.text)
                bot.send_message(guest_id, room_spectators[index].second_q.answer)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global guest_id, room_spectators, questions, activity_first_q, activity_second_q, activity_interview_started

    if call.data == "start_first":
        activity_first_q = True
        count = 0

        for i in room_spectators:
            question = questions[count]
            bot.send_message(i.id, question.text)
            i.first_q = question
            count += 1

        start_2nd_guest_keyboard = types.InlineKeyboardMarkup()
        start_2nd_button = types.InlineKeyboardButton("Запустить второй", callback_data="start_second")
        start_2nd_guest_keyboard.add(start_2nd_button)
        bot.send_message(guest_id, "Первая часть вопросов отправлена на устройства!", reply_markup=start_2nd_guest_keyboard)

    elif call.data == "start_second":
        count_1st_q_not_none = 0
        for user in room_spectators:
            if user.first_q.answer is None:
                count_1st_q_not_none += 1

        if count_1st_q_not_none == 0:
            activity_first_q = False
            activity_second_q = True

            count = 10

            for i in room_spectators:
                question = questions[count]
                bot.send_message(i.id, question.text)
                i.second_q = question
                count += 1

            start_pre_view_guest_keyboard = types.InlineKeyboardMarkup()
            start_view_button = types.InlineKeyboardButton("Запустить интервью", callback_data="start_interview")
            start_pre_view_guest_keyboard.add(start_view_button)
            bot.send_message(guest_id, "Вторая часть вопросов отправлена на устройства!", reply_markup=start_pre_view_guest_keyboard)
        else:
            bot.send_message(guest_id, "Не все ответили на вопрос!")
        
    elif call.data == "start_interview":
        count_2nd_q_not_none = 0
        for user in room_spectators:
            if user.second_q.answer is None:
                count_2nd_q_not_none += 1

        if count_2nd_q_not_none == 0:
            activity_second_q = False
            activity_interview_started = True

            print("Приём ответов завешён. Интервью начинается!")
            if host_id is not None:
                bot.send_message(host_id, f"Интервью начинается! Теперь ты задаёшь вопросы!")
            if guest_id is not None:
                bot.send_message(guest_id, f"Интервью начинается! Теперь ты отвечаешь на вопросы!")
        else:
            bot.send_message(guest_id, "Не все ответили на вопрос!")

    elif call.data == "check_roommates":
        res = "В комнате:\n"
        count = 0
        for i in room_spectators:
            count += 1
            res += f"{count}. {i.first_name} {i.last_name} ({i.id})\n"
        bot.send_message(guest_id, res)
    

def check_user(user_id):
    if any(user.id == user_id for user in room_spectators):
        return 1
    elif user_id == host_id:
        return 2
    elif user_id == guest_id:
        return 3
    else:
        return 4


if __name__=="__main__":
    bot.polling(none_stop=True)
