import json
import requests
from flask import Flask, request, abort
import hashlib
import hmac
import base64


app = Flask(__name__)

# 配置 Channel Access Token 和 Channel Secret
CHANNEL_ACCESS_TOKEN = "ZRwseNM8SMXvhUoDCanH43TzbX2fEDwSsR6P+CqDHMpP8CD3hj6J+IFVvXgDe1yHVF6//LVcALDT/pcFyFINQheq0idZHQ3VENJE950eAl2z9eLOFnld5thr3k2TNGtipbYh2ItyZqJgKF/22c0PMwdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "83572036e69a1f0540515f774ec6f8d8"

# Line Bot 回應設定 
@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 Line Bot 發送的訊息
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']

    # 驗證訊息是否來自 Line
    if not verify_signature(body, signature, CHANNEL_SECRET):
        abort(400)

    # 解析訊息內容
    events = json.loads(body)['events']

    # 遍歷每個事件
    for event in events:
        if event['type'] == 'message':
            handle_message(event)

    return 'OK'

# 處理接收到的訊息
def handle_message(event):
    # 從 event 中獲取使用者的訊息內容
    user_message = event['message']['text']

    # 當收到訊息時開始遊戲
    if user_message.lower() == '開始遊戲':
        reply_start_game_button(event)
    elif user_message.lower() == '哄哄她':
        reply_game1_button(event)
    elif user_message.lower() == '再哄一次':
        reply_gameA1_button(event)
    elif user_message.lower() == '女人去洗碗':
        reply_game4_button(event)

    elif user_message.lower() == '我真是個小菜雞':
        reply_gameover_button(event)
    elif user_message.lower() == '重新挑戰':
        reply_start_game_button(event)
    elif user_message.lower() == '不玩了':
        reply_message(event, "掰掰菜雞")
    elif user_message.lower() == '不哄了啦':
        reply_gameover_button(event)
    
    else:
        reply_message(event, "請傳送「開始遊戲」以啟動遊戲")


# 回覆訊息給使用者 不需再用
def reply_message(event, message):
    reply_token = event['replyToken']
    payload = {'replyToken': reply_token, 'messages': [{'type': 'text', 'text': message}]}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN
    }
    requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=payload)


# 回覆遊戲開始按鈕給使用者 n
def reply_start_game_button(event):
    reply_token = event['replyToken']
    payload = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'template',
                'altText': '遊戲開始按鈕',
                'template': {
                    'type': 'buttons',
                    'title': '女友生氣時，您會怎麼應對？',
                    'text': '請選擇',
                    'actions': [
                        {'type': 'message', 'label': '哄哄她', 'text': '哄哄她'},
                        {'type': 'message', 'label': '道歉n', 'text': '道歉'},
                        {'type': 'message', 'label': '買禮物n', 'text': '買禮物'},
                        {'type': 'message', 'label': '女人去洗碗', 'text': '女人去洗碗'}
                    ]
                }
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN
    }
    requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=payload)

# 女友說不需要你哄她 n
def reply_game1_button(event):
    reply_token = event['replyToken']
    payload = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'template',
                'altText': '遊戲開始按鈕',
                'template': {
                    'type': 'buttons',
                    'title': '女友說不需要你哄她',
                    'text': '請問閣下該如何應對？',
                    'actions': [
                        {'type': 'message', 'label': '再哄一次', 'text': '再哄一次'},
                        {'type': 'message', 'label': '道歉n', 'text': '道歉'},
                        {'type': 'message', 'label': '買禮物n', 'text': '買禮物'}
                    ]
                }
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN
    }
    requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=payload)

# 女人直接摔門而出 
def reply_game4_button(event):
    reply_token = event['replyToken']
    payload = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'template',
                'altText': '遊戲開始按鈕',
                'template': {
                    'type': 'buttons',
                    'title': '女人直接摔門而出',
                    'text': '請問閣下該如何應對？',
                    'actions': [
                        {'type': 'message', 'label': '恭喜單身', 'text': '我真是個小菜雞'}
                    ]
                }
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN
    }
    requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=payload)
# 你失敗了！！
def reply_gameover_button(event):
    reply_token = event['replyToken']
    payload = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'template',
                'altText': '遊戲開始按鈕',
                'template': {
                    'type': 'buttons',
                    'title': '你失敗了！！',
                    'text': '請選擇',
                    'actions': [
                        {'type': 'message', 'label': '重新挑戰', 'text': '重新挑戰'},
                        {'type': 'message', 'label': '不玩了！！', 'text': '不玩了'}
                    ]
                }
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN
    }
    requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=payload)
# 臉色稍微好一點了，但依舊不接受！n
def reply_gameA1_button(event):
    reply_token = event['replyToken']
    payload = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'template',
                'altText': '遊戲開始按鈕',
                'template': {
                    'type': 'buttons',
                    'title': '臉色稍微好一點了，但依舊不接受！',
                    'text': '請選擇',
                    'actions': [
                        {'type': 'message', 'label': '再哄一次', 'text': '再哄一次'},
                        {'type': 'message', 'label': '道歉n', 'text': '道歉'},
                        {'type': 'message', 'label': '送禮物n', 'text': '送禮物'},
                        {'type': 'message', 'label': '不哄了啦', 'text': '不哄了啦'}
                    ]
                }
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN
    }
    requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=payload)


def verify_signature(body, signature, channel_secret):
    hash = hmac.new(channel_secret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    hash_signature = base64.b64encode(hash).decode('utf-8')
    return hash_signature == signature


if __name__ == "__main__":
    app.run(port=1234)
