from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import parser
import atexit

app = Flask(__name__)

# Глобальная переменная для хранения текущих данных
current_data = None

def update_data():
    """Функция для обновления данных. Вызывается таймером."""
    global current_data
    current_data = parser.get_prices()

# Настраиваем планировщик: обновлять каждые 30 минут (можно поменять на минуты)
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", minutes=3)
scheduler.start()

# Запускаем парсинг сразу при старте сервера (чтобы не ждать 30 минут)
update_data()

# Корректно останавливаем планировщик при выключении
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def index():
    return render_template('index.html', data=current_data)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)