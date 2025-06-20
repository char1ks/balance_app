import os
import redis
from flask import Flask, make_response, request
import json
from datetime import datetime
import pytz  # Импортируем модуль для работы с часовыми поясами

app = Flask(__name__)
instance_id = os.getenv('INSTANCE_ID', '1')
r = redis.Redis(host='redis', port=6379, db=0)

# Указываем московский часовой пояс
moscow_tz = pytz.timezone('Europe/Moscow')

@app.route('/')
@app.route('/instance1')
@app.route('/instance2')
def hello():
    # Получаем куку из запроса
    cookie_value = request.cookies.get('user_cookie')
    if not cookie_value:
        # Если куки нет, создаем новую
        cookie_value = str(os.urandom(16).hex())
        response = make_response(f"Кука создана. Ответ от инстанца {instance_id}")
        response.set_cookie('user_cookie', cookie_value)
        # Сохраняем данные в Redis
        current_time = datetime.now(moscow_tz).strftime('%d/%m/%Y : %H:%M:%S МСК')  # Время в МСК
        data = {
            "id": instance_id,
            "ts": current_time
        }
        r.lpush(cookie_value, json.dumps(data))
        return response
    else:
        # Если кука есть, получаем историю ответов
        responses = r.lrange(cookie_value, 0, -1)
        # Декодируем байтовые строки в словари
        history_items = [json.loads(response.decode('utf-8')) for response in responses]
        # Добавляем новый ответ в историю
        current_time = datetime.now(moscow_tz).strftime('%d/%m/%Y : %H:%M:%S МСК')  # Время в МСК
        new_data = {
            "id": instance_id,
            "ts": current_time
        }
        r.lpush(cookie_value, json.dumps(new_data))
        history_items.insert(0, new_data)  # Добавляем текущий ответ в начало списка

        # Формируем HTML-ответ с использованием списка
        history_list = ''.join(
            f'<li>Response from instance {item["id"]} - {item["ts"]}</li>'
            for item in history_items[1:]
        )

        html_response = f'''
        <html>
            <head>
                <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
                <title>История ответов</title>
                <style>
                    html, body {{
                        font-family: 'Poppins', sans-serif;
                        margin: 0;
                        padding: 0;
                    }}

                    .text-container {{
                        z-index: 100;
                        width: 100vw;
                        height: 100vh;
                        display: flex;
                        position: absolute;
                        top: 0;
                        left: 0;
                        justify-content: center;
                        align-items: center;
                        font-size: 96px;
                        color: white;
                        opacity: 0.8;
                        user-select: none;
                        text-shadow: 1px 1px rgba(0,0,0,0.1);
                    }}

                    :root {{
                        --color-bg1: rgb(16, 112, 116); /* Бирюзовый */
                        --color-bg2: rgb(3, 3, 4); /* Темный */
                        --color1: 16, 118, 122;
                        --color2: 25, 75, 77;
                        --color3: 194, 236, 237;
                        --color4: 29, 115, 103;
                        --color5: 12, 99, 87;
                        --color-interactive: 8, 92, 83;
                        --circle-size: 80%;
                        --blending: hard-light;
                    }}

                    .gradient-bg {{
                        width: 100vw;
                        height: 100vh;
                        position: fixed;
                        top: 0;
                        left: 0;
                        overflow: hidden;
                        background: linear-gradient(40deg, var(--color-bg1), var(--color-bg2));
                    }}

                    .gradients-container {{
                        filter: url(#goo) blur(40px);
                                                width: 100%;
                        height: 100%;
                    }}

                    .g1, .g2, .g3, .g4, .g5, .interactive {{
                        position: absolute;
                        background: radial-gradient(circle at center, rgba(var(--color1), 0.8) 0, rgba(var(--color1), 0) 50%) no-repeat;
                        mix-blend-mode: var(--blending);
                        width: var(--circle-size);
                        height: var(--circle-size);
                        top: calc(50% - var(--circle-size) / 2);
                        left: calc(50% - var(--circle-size) / 2);
                        opacity: 1;
                    }}

                    .g2 {{
                        background: radial-gradient(circle at center, rgba(var(--color2), 0.8) 0, rgba(var(--color2), 0) 50%) no-repeat;
                    }}

                    .g3 {{
                        background: radial-gradient(circle at center, rgba(var(--color3), 0.8) 0, rgba(var(--color3), 0) 50%) no-repeat;
                        top: calc(50% - var(--circle-size) / 2 + 250px);
                        left: calc(50% - var(--circle-size) / 2 - 850px);
                    }}

                    .g4 {{
                        background: radial-gradient(circle at center, rgba(var(--color4), 0.8) 0, rgba(var(--color4), 0) 50%) no-repeat;
                        opacity: 0.7;
                    }}

                    .g5 {{
                        background: radial-gradient(circle at center, rgba(var(--color5), 0.8) 0, rgba(var(--color5), 0) 50%) no-repeat;
                        width: calc(var(--circle-size) * 2);
                        height: calc(var(--circle-size) * 2);
                        top: calc(50% - var(--circle-size));
                        left: calc(50% - var(--circle-size));
                    }}

                    .interactive {{
                        background: radial-gradient(circle at center, rgba(var(--color-interactive), 0.8) 0, rgba(var(--color-interactive), 0) 50%) no-repeat;
                        width: 100%;
                        height: 100%;
                        top: -50%;
                        left: -50%;
                        opacity: 0.7;
                    }}

                    .content {{
                        position: relative;
                        z-index: 100;
                        color: white;
                        text-align: center;
                        padding: 20px;
                    }}

                    h1 {{
                        color: white;
                        text-align: center;
                        margin-top: 20px;
                    }}

                    ul {{
                        list-style-type: none;
                        padding: 0;
                        margin: 20px auto;
                        max-width: 600px;
                    }}

                    li {{
                        background-color: rgba(12, 86, 89,0.45);
                        margin: 10px 0;
                        padding: 27px;
                        border: 2px solid rgba(16, 112, 116, 0.85);
                        border-radius: 10px;
                        position: relative;
                        transition: transform 0.2s ease;
                    }}

                    li:hover {{
                        transform: scale(1.05);
                    }}

                    li:hover::after {{
                        content: '';
                        position: absolute;
                        top: 50%;
                        left: -20px;
                        width: 10px;
                        height: 10px;
                        background-color: rgba(16, 112, 116, 0.5);
                        border-radius: 50%;
                        transform: translateY(-50%);
                    }}

                    .current-response {{
                         font-weight: bold;
                         color: #ffffff; /* Белый цвет */
                         text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 20px #00ffff; /* Неоновый эффект */
                    }}
                </style>
            </head>
            <body>
                <div class="gradient-bg">
                    <svg xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <filter id="goo">
                                <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
                                <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -8" result="goo" />
                                <feBlend in="SourceGraphic" in2="goo" />
                            </filter>
                        </defs>
                    </svg>
                    <div class="gradients-container">
                        <div class="g1"></div>
                        <div class="g2"></div>
                        <div class="g3"></div>
                        <div class="g4"></div>
                        <div class="interactive"></div>
                    </div>
                </div>
                <div class="content">
                    <h1>История запросов:</h1>
                    <ul>
                        <li><strong>Current Response:</strong> <span class="current-response">Response from instance {history_items[0]["id"]} - {history_items[0]["ts"]}</span></li>
                        {history_list}
                    </ul>
                </div>
            </body>
        </html>
        '''
        return html_response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

