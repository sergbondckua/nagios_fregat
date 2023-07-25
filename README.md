## Телеграм бот для моніторингу Nagios (шляхом парсингу веб-сторінки)


> [![Python 3.11](https://img.shields.io/badge/python-3.10_|_3.11-blue?labelColor=blue&color=yellow)](https://www.python.org/)
> [![Aiogram](https://img.shields.io/badge/aiogram-v2.25.1-blue)](https://docs.aiogram.dev/en/latest/)
> [![Code Style](https://img.shields.io/badge/codestyle-black-black)](https://github.com/psf/black)


Цей проект є телеграм ботом, який взаємодіє з моніторинговою системою Nagios, використовуючи метод парсингу даних з веб-сторінки. Бот буде сканувати стан адрес кожні `N` секунд і, якщо будь-яка адреса буде непрацюючою протягом `MAX_DOWN_TIME_MINUTES` хвилин і більше, бот надішле повідомлення в `CHAT_SUPPORT_ID` чат.

### Вимоги

Переконайтеся, що у вас є наступне:

1. **Python**: Бот написаний на Python, тому переконайтеся, що у вас встановлений Python 3.10+.

2. **Telegram Bot Token**: Отримайте токен для свого бота від [@BotFather](https://t.me/BotFather) в Телеграмі.

3. **Nagios Web Interface URL**: Ви повинні знати URL адресу вашого Nagios веб-інтерфейсу.

### Встановлення

1. Склонуйте цей репозиторій:

    ```bash
    git clone https://github.com/sergbondckua/nagios_fregat.git
    ```
2. Скопіюйте `.env.template` в `.env` і заповніть необхідні дані.
   ```bash
   cp .env.template .env
   ```
3. **Без Docker:**
   1. Створіть [venv](https://docs.python.org/3/library/venv.html)
       ```bash
       cd nagios_fregat/
       ```
       ```bash
       python3 -m venv venv
       ```
       ```bash
       source venv/bin/activate
       ```
   2. Оновіть `pip`:
      ```bash
       pip install --upgrade pip
      ```
   3. Встановить залежності із `requirements.txt`:
      ```bash
      pip install -r requirements.txt
      ```
   4. Запустіть проєкт з команди
      ```bash
      python bot.py
      ```
4. **Docker:**
   1. Можете одразу запускати проєкт із Docker, а якщо в вас його немає, то [завантажте, та встановіть](https://docs.docker.com/get-docker/).
   2. Запустіть проєкт з команди `docker-compose up` або `docker-compose up -d`
