# Telegram-error-notifier

Модуль для отправки уведомлений о возникших исключениях через Telegram-бота. Включает в себя класс для управления отправкой сообщений, а также декоратор, упрощающий процесс отслеживания исключений в функциях.


## Установка
1. Создайте виртуальное окружение:
- Для Windows:
``` bash
python -m venv venv
```
- Для Linux или MacOS:
```bash
python3 -m venv venv
```
2. Активируйте виртуальное окружение:
- Для Windows:
```bash
.\venv\Scripts\activate
```
- Для Linux или MacOS:
```bash
source venv/bin/activate
```
3. Установите необходимые зависимости:
```
pip install -r requirements.txt
```
    
## Подготовка к использованию
Перед использованием модуля выполните следующие шаги для настройки Telegram-бота и получения необходимых данных:
1. Создание Telegram-бота и получение токена:
- Откройте Telegram и найдите бота [@BotFather](https://t.me/BotFather)
- Начните диалог и отправьте команду /newbot для создания нового бота
- Следуйте инструкциям, задайте имя бота и уникальный username
- [@BotFather](https://t.me/BotFather) предоставит вам токен для доступа к API. Сохраните этот токен, он потребуется для настройки модуля
2. Получение chat_id (уникального идентификатора чата в Telegram.):
- Найдите своего бота в Telegram (используйте username, указанный при создании) и отправьте ему любое сообщение
- Откройте следующий URL в браузере, подставив токен вашего бота:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```
- В полученном JSON-объекте найдите информацию о последнем сообщении - в нем будет указан chat_id отправителя (ваш): result -> message -> from -> id
- Сохраните этот chat_id, он понадобится для настройки модуля
3. Сохранение псевдонима для chat_id:
- Для удобства вы можете присвоить удобный псевдоним полученному chat_id в свойстве user_base класса TelegramNotifier. Его можно будет использовать вместо chat_id при отправке сообщений 
## Пример
- Создание псевдонима для chat_id (опционально)
```python
# telegram_error_notifier.py, метод __init__ класса TelegramNotifier:

self.user_base: Dict[str, str] = {
    "your_alias": "your_chat_id"
}
```
- Использование декоратора catch
```python
# division_by_zero.py

from telegram_error_notifier import catch


@catch(
    token="YOUR_TELEGRAM_BOT_TOKEN",
    receiver="your_chat_id", # receiver="your_alias", если был задан псевдоним
    quiet=False
)
def divide(a, b):
    return a / b

if __name__ == "__main__":
    divide(10, 0)
```
- Запуск этого файла приведет к отправке Telegram-ботом сообщения с таким содержимым:
```
Произошел сбой при выполнении division_by_zero.py:
 
Traceback (most recent call last):
  File "/home/demyan/Code/tools/TelegramErrorNotifier/telegram_error_notifier.py", line 130, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/home/demyan/Code/tools/TelegramErrorNotifier/division_by_zero.py", line 10, in divide
    return a / b
           ~~^~~
ZeroDivisionError: division by zero
```

