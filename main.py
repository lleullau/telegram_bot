import requests
from datetime import datetime
import telebot
from auth_data import token, weather_api_token
import datetime

#add comment

def telegram_bot():
    bot = telebot.TeleBot(token)
    user_states = {}

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет! Для того чтобы ознакомиться с доступными командами наберите /menu")

    @bot.message_handler(commands=["menu"])
    def menu(message):
        bot.send_message(message.chat.id,
                         "/weather - просмотреть текущую погоду по выбранному городу\n/price - курс BTC на данный момент")

    @bot.message_handler(commands=["price"])
    def get_btc_price(message):
        try:
            req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
            responce = req.json()
            sell_price = responce["btc_usd"]["sell"]

            bot.send_message(
                message.chat.id,
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\nBTC sell price: {sell_price}"
            )

        except Exception as ex:
            print(ex)
            bot.send_message(
                message.chat.id,
                f"Upppss... Something went wrong... "
            )

    @bot.message_handler(commands=["weather"])
    def send_message(message):
        bot.send_message(message.chat.id, "Введите название города на английском языке:")
        user_states[message.chat.id] = "waiting_for_city"

    @bot.message_handler(content_types=["text"])
    def send_message(message):
        text = message.text.lower()

        # Проверяем текущее состояние пользователя
        user_state = user_states.get(message.chat.id, None)

        if user_state == "waiting_for_city":
            # Если пользователь ожидает ввода города после команды "weather"
            send_weather(message, message.text, weather_api_token)
            # Сбрасываем состояние после ввода города
            user_states[message.chat.id] = None


    def send_weather(message, city, token):
        try:
            weather_api_link = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={token}&units=metric"
            r = requests.get(weather_api_link)
            data = r.json()

            city = data['name']
            country = data['sys']['country']
            current_temp = data['main']['temp']
            feels_like_temp = data['main']['feels_like']
            humidity = data['main']['humidity']
            sunrise_time = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
            sunset_time = datetime.datetime.fromtimestamp(data['sys']['sunset'])
            lenght_day_time = sunset_time - sunrise_time
            wind = data['wind']['speed']

            bot.send_message(message.chat.id,
                             f"*** {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')} ***")
            bot.send_message(message.chat.id,
            f"Город: {city}\nТемпература: {current_temp}°C\nОщущается как: {feels_like_temp}°C\n"
                f"Влажность: {humidity}%\nВосход солнца: {sunrise_time}\nЗаход солнца: {sunset_time}\n"
                f"Продолжительность дня: {lenght_day_time}")

        except Exception as ex:
            bot.send_message(message.chat.id,"Проверьте название города")
            bot.send_message(message.chat.id, "/weather")

    bot.polling()


if __name__ == "__main__":
    telegram_bot()