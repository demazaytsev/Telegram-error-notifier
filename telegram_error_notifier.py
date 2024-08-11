from functools import wraps
from pathlib import Path
from requests import post
from sys import argv
from traceback import format_exc
from typing import Any, Callable, Dict, Optional


class TelegramNotifier:

    '''Отправка сообщений о возбужденных исключениях через Телеграм-бота.'''

    class TelegramNotifierException(Exception):

        '''Специфическое исключение для класса TelegramNotifier.'''

    class ChatIDNotFound(TelegramNotifierException):
        
        '''Отсутствует информация о chat_id указанного пользователя.'''

    class SendingFailed(TelegramNotifierException):
        
        '''Сообщение не было отправлено из-за возникшей ошибки.'''

    def __init__(
        self,
        token: str,
        quiet: bool,
    ) -> None:
        '''
        Параметры:
            token: валидный токен Телеграм-бота.
                Подробнее о создании ботов и выделении токенов: https://tlgrm.ru/docs/bots.
            quiet: True - исключения не возбуждаются явно, вместо этого выводятся
                короткие имформационные сообщения. False - исключения возбуждаются.
        '''
        url: str = 'https://api.telegram.org'
        self.url: str = f'{url}/bot{token}'
        self.quiet: bool = quiet
        # Установка соответствия между username пользователя и его chat_id
        self.user_base: Dict[str, str] = {}

    def send_message(
        self,
        receiver: str,
        message: str
    ) -> None:
        '''
        Отправка сообщения пользователю.

        Параметры:
            receiver: получатель сообщения. Может быть указан как username, так и chat_id.
                В превом случае необходимо задать соответствие между этими двумя значениями в словаре self.user_base.
                Отправка сообщения будет невозможна, если данным пользователем не был инициирован диалог с ботом.
            message: текст передаваемого сообщения.

        Исключения:
            ChatIDNotFound: в словаре self.user_base отсутствует информация о chat_id указанного пользователя.
            SendingFailed: отправка сообщения не удалась.
        '''
        METHOD: str = 'sendMessage'
        url: str = f'{self.url}/{METHOD}'
        if receiver.isdigit():
            receiver_id: str = receiver
        else:
            receiver_id: Optional[str] = self.user_base.get(receiver)
            if receiver_id is None:
                error_message: str = f'Отсутствует информация о chat_id пользователя @{receiver} в словаре {self.__class__.__name__}.user_base.'
                if self.quiet:
                    print(f'[UNKNOWN USER] {error_message}')
                else:
                    raise self.ChatIDNotFound(error_message)

        payload: Dict[str, str] = {
            'chat_id': receiver_id,
            'text': message,
        }

        response_json: Dict[str, Any] = post(url=url, json=payload).json()
        status: Optional[bool] = response_json.get('ok')
        user_identity: str = f'{"с chat_id " if receiver.isdigit() else "@"}{receiver}'
        if not status:
            description: str = response_json.get('description', 'Информация о причине ошибки не найдена')
            description_translation: Dict[str, str] = {
                'Bad Request: chat not found': 'Диалог не найден. Проверьте корректность chat_id или попробуйте отправить любое сообщение боту',
                'Unauthorized': 'Бот с указанным токеном не найден'
            }
            description: str = description_translation.get(description, description)
            error_message: str = f'Сообщение пользователю {user_identity} не было отправлено. {description}.'
            if self.quiet:
                print(f'[SENDING ERROR] {error_message}')
                return
            else:
                raise self.SendingFailed(error_message)
        elif status is True:
            success_message: str = f'Сообщение о возникшей ошибке направлено пользователю {user_identity}.'
            print(f'[MESSAGE SENDED] {success_message}')
            return

def catch(
    token: str,
    receiver: str,
    quiet: bool=True
) -> Callable[[Callable], Callable]:
    '''
    Создание функции-декоратора.

    Параметры:
        token: валидный токен Телеграм-бота.
            Подробнее о создании ботов и выделении токенов: https://tlgrm.ru/docs/bots.
        receiver: получатель сообщения. Может быть указан как username, так и chat_id.
            В превом случае необходимо задать соответствие между этими двумя значениями в словаре self.user_base.
            Отправка сообщения будет невозможна, если данным пользователем не был инициирован диалог с ботом.
        quiet: True - исключения не возбуждаются явно, вместо этого выводятся
            короткие имформационные сообщения. False - исключения возбуждаются.
    '''
    def decorator(
        func: Callable
    ) -> Callable:
        wraps(func)
        def wrapper(
            *args: Any,
            **kwargs: Any
        ) -> Any:
            '''
            Попытка вызова декорируемой функции.
            В случае возбуждения исключения - его текст будет отправлен указанному пользователю.
            '''
            try:
                return func(*args, **kwargs)
            except Exception as exception:
                file_name: str = Path(argv[0]).name
                message: str = f'Произошел сбой при выполнении {file_name}:\n\n{format_exc()}'
                TelegramNotifier(token, quiet).send_message(receiver, message)
                raise exception
        return wrapper
    return decorator