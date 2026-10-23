from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import parser
import atexit
import os

app = Flask(__name__)
current_data = None

def update_data():
    global current_data
    try:
        current_data = parser.get_all_data()
        if current_data and current_data.get("cash_gold"):
            print("✅ Данные успешно обновлены на сервере!")
        else:
            print("⚠️ Данные загружены, но список скупки пуст (возможно, сайт блокирует IP).")
    except Exception as e:
        print(f"❌ ОШИБКА при парсинге на Render: {e}")
        # Если произошла ошибка, ставим заглушку, чтобы страница не выдавала 500
        if current_data is None:
            current_data = {"cash_gold": None, "vtb": [], "timestamp": "Ошибка загрузки данных"}

# Обновляем каждые 15 минут
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", minutes=15)
scheduler.start()

# Первый запуск
update_data()

atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def index():
    return render_template('index.html', data=current_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
