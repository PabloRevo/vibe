***
## Инструкция по эксплуатации проекта
***

### Перечень файлов и краткое описание админ-панели (Django).
***

### Файлы в корне проекта:

1. __manage.py__ - файл с командами приложения.

### Пакеты и директории в корне проекта:

#### 1. vibe:
* __init.py__ - инициализирует пакет vibe и его содержимое.
* __asgi.py__ - файл для ассинхронной связи сервера и проекта.
* __wsgi.py__ - файл для связи сервера и проекта.
* __settings.py__ - файл с конфигурациями проекта.
* __urls.py__ - файл с URL-адресами проекта.

#### 2. app_config:
* __init.py__ - инициализирует пакет app_config и его содержимое.
* __admin.py__ - файл с настройками админ-панели.
* __apps.py__ - файл с конфигурацией приложения.
* __models.py__ - файл с моделями базы данных приложения.
    #### 1. migrations:
    * __init.py__ - инициализирует пакет migrations и его содержимое

#### 3. app_vibe:
* __init.py__ - инициализирует пакет app_vibe и его содержимое.
* __admin.py__ - файл с настройками админ-панели.
* __apps.py__ - файл с конфигурацией приложения.
* __models.py__ - файл с моделями базы данных приложения.
    #### 1. migrations:
    * __init.py__ - инициализирует пакет migrations и его содержимое

#### 4. config:
* __gunicorn.conf.py__ - файл с конфигурациями гуникорна.
* __vibe.conf__ - файл с конфигурациями супервизора.

#### 5. static:
* Содержит все статический файлы приложения (css, js, изображения)

#### 6. media:
* Содержит все медиа-файлы

### Перечень файлов и краткое описание бота vibe (Aiogram).
***

### Файлы в корне проекта:

1. __.env.template__ - образец файла .env с описанием данных.
2. __.env__ - необходимо создать вручную и поместить Токен телеграм-бота.
3. __loader.py__ - создаёт экземпляры: телеграмм-бота и логгера.
4. __logging_config.py__ - задаёт конфигурацию логгеру.
5. __main.py__ - запускает бота.
6. __requirements.txt__ - файл с зависимостями.

### Пакеты в корне проекта:
#### 1. settings:
* __init.py__ - инициализирует пакет settings и его содержимое.
* __settings.py__ - подгружает переменные окружения, для работы бота.
* __constants.py__ - файл с текстами сообщений бота.

#### 2. keyboards:
* __init.py__ - инициализирует пакет keyboards и его содержимое
* __keyboards.py__  - содержит все клавиатуры участвующие в проекте
* __key_text.py__ - файл с текстами кнопок клавиатур бота.

#### 3. handlers:
* __init.py__ - инициализирует пакет handlers и его содержимое.
* __start.py__ - содержит хэндлеры старта и регистрации в боте.
* __rates.py__ - содержит хэндлеры с основным сценарием работы бота.
* __admin.py__ - содержит хэндлеры команд администратора.
* __support.py__ - содержит хэндлеры вспомогательных команд пользователя.
* __timer.py__ - содержит функцию разблокирования вопрос пользователя по таймеру.
* __echo.py__ - содержит хэндлер для отлова сообщений вне сценария.

#### 4. database:
* __init.py__ - инициализирует пакет database и его содержимое
* __states.py__ - содержит модели классов машины состояния.
* __models.py__ - содержит модели базы данных.

#### 5. config:
* __bot.conf__ - файл с конфигурациями супервизора.

#### 6. media:
* Содержит все медиа-файлы

