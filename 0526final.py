from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import datetime
import requests
import random

app = Flask(__name__)

line_bot_api = LineBotApi('Z2IMYwzBofGN+CNSbo1hcQrGLn7gq6fwZaUWm5PsIp/ZERlLnWoGJQJbUDj8oTvBfzPnuYqqCpWzaMUKmG2c77wjzhWg8kFDTetccjw/KcbpwK5m6lizBxMKd+Mr54nFoX2J1RJtjiLNvHFA2kKBQAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7e0540c52487405b09ea8ae3a64e7181')

user_location = None
user_meal_type = None
recommendation_mode = None
selected_restaurant = None

def get_restaurants(location, meal_type, number):
    api_key = 'AIzaSyBBynoB6iXHrxM6V_oc__aeKgUUC5gMi0c'
    endpoint = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    params = {
        'query': f'{meal_type} restaurants in {location}',
        'key': api_key
    }

    response = requests.get(endpoint, params=params)
    results = response.json().get('results', [])

    if results:
        if number == 1:
            restaurant = random.choice(results)
            name = restaurant['name']
            address = restaurant['formatted_address']
            rating = restaurant.get('rating', '暫無評分')
            message = f"以下是 {location} 的隨機推薦餐廳:\n{name} - 評分: {rating}, 地址: {address}"
            if 'opening_hours' in restaurant and 'weekday_text' in restaurant['opening_hours']:
                opening_hours = restaurant['opening_hours']['weekday_text']
                current_day = datetime.datetime.now().weekday()
                today_opening_hours = opening_hours[current_day] if current_day < len(opening_hours) else '未提供'
                message += f"\n今日營業時間：{today_opening_hours}"
            else:
                detailed_response = requests.get(f"https://maps.googleapis.com/maps/api/place/details/json?place_id={restaurant['place_id']}&fields=opening_hours&key={api_key}")
                detailed_result = detailed_response.json().get('result', {})
                if 'opening_hours' in detailed_result and 'weekday_text' in detailed_result['opening_hours']:
                    opening_hours = detailed_result['opening_hours']['weekday_text']
                    current_day = datetime.datetime.now().weekday()
                    today_opening_hours = opening_hours[current_day] if current_day < len(opening_hours) else '未提供'
                    message += f"\n今日營業時間：{today_opening_hours}"
                else:
                    message += "\n營業時間未提供"
        else:
            random_restaurants = random.sample(results, 10)
            message = f"以下是 {location} 的隨機推薦餐廳:\n"
            for i, restaurant in enumerate(random_restaurants, 1):
                name = restaurant['name']
                address = restaurant['formatted_address']
                rating = restaurant.get('rating', '暫無評分')
                message += f"{i}. {name} - 評分: {rating}, 地址: {address}\n"
                if 'opening_hours' in restaurant and 'weekday_text' in restaurant['opening_hours']:
                    opening_hours = restaurant['opening_hours']['weekday_text']
                    current_day = datetime.datetime.now().weekday()
                    today_opening_hours = opening_hours[current_day] if current_day < len(opening_hours) else '未提供'
                    message += f"今日營業時間：{today_opening_hours}\n"
                else:
                    detailed_response = requests.get(f"https://maps.googleapis.com/maps/api/place/details/json?place_id={restaurant['place_id']}&fields=opening_hours&key={api_key}")
                    detailed_result = detailed_response.json().get('result', {})
                    if 'opening_hours' in detailed_result and 'weekday_text' in detailed_result['opening_hours']:
                        opening_hours = detailed_result['opening_hours']['weekday_text']
                        current_day = datetime.datetime.now().weekday()
                        today_opening_hours = opening_hours[current_day] if current_day < len(opening_hours) else '未提供'
                        message += f"今日營業時間：{today_opening_hours}\n"
                    else:
                        message += "營業時間未提供\n"
    else:
        message = f"在 {location} 沒有找到 {meal_type} 餐廳."

    return message

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global user_location
    global user_meal_type
    global recommendation_mode
    global selected_restaurant

    if user_location is None and user_meal_type is None:
        user_location = event.message.text
        quick_reply = QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="早餐", text="早餐")),
                QuickReplyButton(action=MessageAction(label="午餐", text="午餐")),
                QuickReplyButton(action=MessageAction(label="晚餐", text="晚餐"))
            ]
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請選擇您想要的餐點類型：", quick_reply=quick_reply)
        )
    elif user_meal_type is None:
        user_meal_type = event.message.text
        selected_restaurant = get_restaurants(user_location, user_meal_type, 1)
        

        # 建立 QuickReply 來提供選擇
        quick_reply = QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="我自己去", text="我自己去")),
                QuickReplyButton(action=MessageAction(label="帶我去", text="帶我去"))
            ]   
        )

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=selected_restaurant.replace('\n', '\n\n'), quick_reply=quick_reply)
        )

    elif event.message.text == "我自己去":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="要吃飽窩🥰")
        )
        user_location = None
        user_meal_type = None
        recommendation_mode = None

    elif event.message.text == "帶我去":
        quick_reply = QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="重新推薦一間", text="重新推薦一間")),
                QuickReplyButton(action=MessageAction(label="結束", text="結束"))
            ]
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="這是餐廳的位置：\nhttps://www.google.com/maps/search/?api=1&query=" + selected_restaurant.split('\n')[1], quick_reply=quick_reply)
    )

    elif event.message.text == "重新推薦一間":
        selected_restaurant = get_restaurants(user_location, user_meal_type, 1)
        

        # 建立 QuickReply 來提供選擇
        quick_reply = QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="我自己去", text="我自己去")),
                QuickReplyButton(action=MessageAction(label="帶我去", text="帶我去"))
            ]   
        )

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=selected_restaurant.replace('\n', '\n\n'), quick_reply=quick_reply)
        )

    elif event.message.text == "結束":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="掰掰囉🥰")
        )
        user_location = None
        user_meal_type = None
        recommendation_mode = None
        

if __name__ == "__main__":
    app.run(port=5269)