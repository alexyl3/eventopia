from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {
    'москва': ['1540737/daa6e420d33102bf6947', '213044/7df73ae4cc715175059e'],
    'нью-йорк': ['1652229/728d5c86707054d4745f', '1030494/aca7ed7acefde2606bdc'],
    'париж': ["1652229/f77136c2364eb90a3ea8", '123494/aca7ed7acefd12e606bdc']
}

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
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return jsonify(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,  # здесь будет храниться имя
            'started': False,  # здесь информация о том, что пользователь начал игру. По умолчанию False
            'grade': None
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            # создаём пустой массив, в который будем записывать города, которые пользователь уже отгадал
            sessionStorage[user_id]['guessed_cities'] = []
            # как видно из предыдущего навыка, сюда мы попали, потому что пользователь написал своем имя.
            # Предлагаем ему сыграть и два варианта ответа "Да" и "Нет".
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
        sessionStorage[user_id]['grade'] = req['request']['nlu']['tokens'][0]
        print(sessionStorage[user_id])
        if not sessionStorage[user_id]['started']:
            res['response']['text'] = f'Отлично! Чем интересуешься сегодня?'
            sessionStorage[user_id]['started'] = True
        else:
            play_game(res, req)


def play_game(res, req):
    res['response']['text'] = req['request']['nlu']['tokens']
    return


def get_city(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO, то пытаемся получить город(city), если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()


# res['response']['card'] = {}
#             res['response']['card']['type'] = 'BigImage'
#             res['response']['text'] = f'Отлично! Чем интересуешься сегодня?'
#             res['response']['card']['title'] = 'Спектакль Недоросль в Малом театре'
#             res['response']['card']['image_id'] = "https://www.maly.ru/images/performances/5f8c0e8432189.jpg"
#             res['response']['buttons'] = [
#                 {
#                     'hide': True,
#                     'title': 'Перейти',
#                     "url": "https://www.maly.ru/spectacle/view?name=nedorosl"
#                 }]