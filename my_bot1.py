import telebot
import requests
from telebot import types 

TELEGRAM_BOT_TOKEN = '8976035335:AAHoXsU3Yksz_YA0fzDF1Jb1wxS4hs_FQy4'
WEATHER_API_KEY = 'a69581083dda457cb92151421262306'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def get_weather(city):
    try:
        url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no'
        response = requests.get(url)
        data = response.json()

        if 'error' not in data:
            location = data['location']['name']
            country = data['location']['country']
            current = data['current']
            weather_desc = current['condition']['text']
            temp = current['temp_c']
            humidity = current['humidity']
            wind_speed = current['wind_kph']
            weather_report = (
                f'Погода в {location}, {country}:\n'
                f'Описание: {weather_desc}\n'
                f'Температура: {temp}°C\n'
                f'Влажность: {humidity}%\n'
                f'Скорость ветра: {wind_speed} км/ч'
            )
        else:
            if data["error"]["code"] == 1006:
                weather_report = '❌ Город не найден. Пожалуйста, проверьте правильность написания.'
            else:
                weather_report = f'Ошибка: {data["error"]["message"]}'
    except requests.exceptions.RequestException:
        weather_report = 'Ошибка при подключении к API погоды.'
    return weather_report


def get_forecast(city):
    try:
        url = f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=3&aqi=no&alerts=no'
        response = requests.get(url)
        data = response.json()

        if 'error' not in data:
            location = data['location']['name']
            country = data['location']['country']
            forecast_days = data['forecast']['forecastday']
            
            report = f'📅 Прогноз погоды в {location}, {country} на 3 дня:\n\n'
            
            for day in forecast_days:
                date = day['date']
                max_temp = day['day']['maxtemp_c']
                min_temp = day['day']['mintemp_c']
                condition = day['day']['condition']['text']
                
                report += (
                    f'🔹 Дата: {date}\n'
                    f'Состояние: {condition}\n'
                    f'Температура: от {min_temp}°C до {max_temp}°C\n'
                    f'-----------------------\n'
                )
            return report
        else:
            if data["error"]["code"] == 1006:
                return '❌ Город не найден для прогноза. Попробуйте еще раз.'
            return f'Ошибка: {data["error"]["message"]}'
    except requests.exceptions.RequestException:
        return 'Ошибка при подключении к API погоды.'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('Москва')
    btn2 = types.KeyboardButton('Санкт-Петербург')
    btn3 = types.KeyboardButton('Новосибирск')
    btn4 = types.KeyboardButton('Прогноз на 3 дня 📅')
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(
        message.chat.id, 
        'Привет! Я бот для получения погоды. Выберите город из меню, введите свой или нажмите кнопку прогноза!', 
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == 'Прогноз на 3 дня 📅')
def ask_city_for_forecast(message):
    msg = bot.send_message(message.chat.id, 'Введите название города, для которого хотите узнать прогноз на 3 дня:')
    bot.register_next_step_handler(msg, process_forecast_step)


def process_forecast_step(message):
    city = message.text.strip()
    forecast_report = get_forecast(city)
    bot.reply_to(message, forecast_report, parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def send_weather(message):
    city = message.text.strip()
    weather_report = get_weather(city)
    bot.reply_to(message, weather_report)


bot.infinity_polling()                     