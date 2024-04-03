from flask import Flask, request, jsonify
import logging
import sqlite3
from data import bd_session
from data.events import Events
from data.keywords import Keywords

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    bd_session.global_init("eventopia.db")
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return jsonify(response)

keywords = []

# функция для начала диалога с пользователем
def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'started': False,
            'grade': None
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. В каком ты классе?'
            res['response']['buttons'] = [
                {
                    'hide': True,
                    'title': '5',
                    'payload': {"grade": 5}
                },
                {
                    'hide': True,
                    'title': '6',
                    'payload': {"grade": 6}
                },
                {
                    'hide': True,
                    'title': '7',
                    'payload': {"grade": 7}
                },
                {
                    'hide': True,
                    'title': '8',
                    'payload': {"grade": 8}
                },
                {
                    'hide': True,
                    'title': '9',
                    'payload': {"grade": 9}
                }
            ]

    else:
        grade = req['request']['nlu']['tokens'][0]
        sessionStorage[user_id]['grade'] = grade
        if not sessionStorage[user_id]['started']:
            res['response']['text'] = f'Отлично! Чем интересуешься сегодня?'
            sessionStorage[user_id]['started'] = True
        else:
            find_results(res, req)

# функция поиска результатов по запросу
def find_results(res, req):
    db_sess = bd_session.create_session()
    keywords = db_sess.query(Keywords).all()
    print(keywords)
    to_find = get_subject(req)
    res['response']['card']['type'] = 'BigImage'
    res['response']['card']['title'] = 'Спектакль Недоросль в Малом театре'
    res['response']['card']['image_id'] = "https://www.maly.ru/images/performances/5f8c0e8432189.jpg"
    res['response']['buttons'] = [
            {
                'hide': True,
                'title': 'Перейти',
                "url": "https://www.maly.ru/spectacle/view?name=nedorosl"
            }]
    # поиск по базе данных результатов и составление ответа
    return


# функция для поиска в ответе пользователя писателя или книги
def get_subject(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO, то пытаемся получить город(city), если нет, то возвращаем None
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('last_name', None)
    for word in req['request']['nlu']['tokens']:
        if word.lower() in keywords:
            return word.lower()



# функция для поиска в ответе пользователя имени
def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()

# https://www.maly.ru/spectacle/view?name=nedorosl