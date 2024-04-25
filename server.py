from flask import Flask, request, jsonify
import logging
import sqlite3
from random import choice
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
        res['response'][
            'text'] = 'Привет!👋 Я помогу тебе найти интересные мероприятия в Москве, связанные со школьной литературой. \n\n🏛 Ты можешь назвать произведение или автора, а я предложу подходящие мероприятия. Если тебе хочется посмотреть другие варианты на свой запрос скажи "Еще". Если не знаешь, что хочется посмотреть - так и скажи, я подберу мероприятие на свой вкус!\n\n Как тебя зовут?'
        sessionStorage[user_id] = {
            'first_name': None,
            'started': False,
            'grade': None,
            'used': [],
            'last': None
        }
        return
    print(sessionStorage[user_id])
    if sessionStorage[user_id]['first_name'] is None:

        first_name = get_first_name(req)
        print(first_name)
        if first_name == "help":
            res['response'][
                'text'] = f'Я помогу тебе найти интересные мероприятия в Москве, связанные со школьной литературой. \n\n🏛 Ты можешь назвать произведение или автора, а я предложу подходящие мероприятия. Если тебе хочется посмотреть другие варианты на свой запрос скажи "Еще". Если не знаешь, что хочется посмотреть - так и скажи, я подберу мероприятие на свой вкус! Как тебя зовут?'
        elif first_name is None:
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
        if sessionStorage[user_id]['grade'] is None:
            words = " ".join([word.lower() for word in req['request']['nlu']['tokens']])
            grade = None
            for i in req['request']['nlu']['tokens']:
                if i.isnumeric():
                    grade = i
            if "что ты умеешь" in words or "помощь" in words:
                res['response'][
                    'text'] = f'Я помогу тебе найти интересные мероприятия в Москве, связанные со школьной литературой. \n\n🏛 Ты можешь назвать произведение или автора, а я предложу подходящие мероприятия. Если тебе хочется посмотреть другие варианты на свой запрос скажи "Еще". Если не знаешь, что хочется посмотреть - так и скажи, я подберу мероприятие на свой вкус!\n\n В каком классе ты учишься?'
            elif grade is None:
                res['response']['text'] = f"Не смогла понять, в каком ты классе. Повтори, пожалуйста!"
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
                sessionStorage[user_id]['grade'] = grade
                if not sessionStorage[user_id]['started']:
                    res['response']['text'] = f'Отлично! Чем интересуешься сегодня?'
                    sessionStorage[user_id]['started'] = True
        else:
            find_results(res, req)


# функция поиска результатов по запросу
def find_results(res, req):
    to_find = get_subject(req)
    print(to_find)
    if to_find == "stop":
        res['response']['text'] = f'Было приятно помочь!'
    elif to_find == "help":
        res['response'][
            'text'] = f'Я помогу тебе найти интересные мероприятия в Москве, связанные со школьной литературой. \n\n🏛 Ты можешь назвать произведение или автора, а я предложу подходящие варианты. Если тебе хочется посмотреть другие варианты на свой запрос скажи "Еще". Если не знаешь, что хочется посмотреть - так и скажи, я подберу мероприятие на свой вкус!'
    elif to_find == "nothing more":
        res['response'][
            'text'] = f'К сожалению, больше по твоему запросу нет предложений. Может тебя интересует что-то еще?'
    elif to_find is not None:
        event = to_find
        sessionStorage[req['session']['user_id']]['used'].append(event.title)
        res['response']['text'] = f"Вам может понравится {event.title}"
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = f"Вам может понравится {event.title}"
        res['response']['card']['image_id'] = event.image_link
        res['response']['buttons'] = [
            {
                'hide': True,
                'title': 'Перейти',
                "url": event.link
            }]
    else:
        res['response'][
            'text'] = f'Не удалось найти ничего по твоему запросу. Может тебя интересует еще что-то?'
    return


# функция для поиска в ответе пользователя писателя или книги
def get_subject(req):
    db_sess = bd_session.create_session()
    keywords = [keyword.word for keyword in db_sess.query(Keywords).all()]
    words = " ".join([word.lower() for word in req['request']['nlu']['tokens']])
    if "что ты умеешь" in words or "помощь" in words:
        return "help"
    if "еще" in words or "друго" in words:
        words = sessionStorage[req['session']['user_id']]["last"]
    sessionStorage[req['session']['user_id']]["last"] = words
    found = 0
    for keyword in keywords:
        if keyword.lower()[:-1] in words:
            found = 1
            key_id = db_sess.query(Keywords).filter(Keywords.word == keyword).first()
            events = db_sess.query(Events).filter(Events.key_words == key_id.id, Events.title.notin_(
                sessionStorage[req['session']['user_id']]['used'])).all()
            if not events:
                events = db_sess.query(Events).filter(Events.author == key_id.id, Events.title.notin_(
                    sessionStorage[req['session']['user_id']]['used'])).all()
            if events:
                return choice(events)

    if "нет" in words or "не" in words:
        events = db_sess.query(Events).filter(Events.grade == sessionStorage[req['session']['user_id']]['grade'],
                                              Events.title.notin_(
                                                  sessionStorage[req['session']['user_id']]['used'])).all()
        if not events:
            events = db_sess.query(Events).filter(
                Events.title.notin_(sessionStorage[req['session']['user_id']]['used'])).all()
        if events:
            return choice(events)

    if "все" in words or "хватит" in words:
        return "stop"
    if found == 1:
        return "nothing more"
    return None


# функция для поиска в ответе пользователя имени
def get_first_name(req):
    words = " ".join([word.lower() for word in req['request']['nlu']['tokens']])
    if "что ты умеешь" in words or "помощь" in words:
        return "help"
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()