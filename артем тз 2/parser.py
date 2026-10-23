import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import xml.etree.ElementTree as ET

def get_cash_gold():
    """Парсит цены скупки с cash-gold.ru"""
    url = "https://cash-gold.ru"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
                # ВРЕМЕННАЯ ОТЛАДКА
        print(f"DEBUG: Статус ответа от cash-gold.ru: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Текст ответа: {response.text[:200]}") # Первые 200 символов
        # КОНЕЦ ОТЛАДКИ
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Ошибка cash-gold: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    results = {"gold": [], "silver": [], "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S")}

    gold_container = soup.find(id="gold-probes")
            if not gold_container:
            print("DEBUG: Блок с золотом (id='gold-probes') не найден на странице!")
            # Сохраняем кусок HTML, чтобы понять, что там
            print(f"DEBUG HTML: {soup.text[:500]}") 
    if gold_container:
        for btn in gold_container.find_all("button", class_="probe-btn"):
            name = btn.get("data-name")
            price = btn.get("data-price")
            premium = btn.get("data-premium-price")
            if name and price:
                results["gold"].append({
                    "name": name,
                    "price": int(price),
                    "premium": int(premium) if premium else None
                })

    silver_container = soup.find(id="silver-probes")
    if silver_container:
        for btn in silver_container.find_all("button", class_="probe-btn"):
            name = btn.get("data-name")
            price = btn.get("data-price")
            if name and price:
                results["silver"].append({
                    "name": name,
                    "price": int(price),
                    "premium": None
                })
    return results

def get_vtb_metals():
    """Парсит котировки ВТБ через Selenium (поиск по тексту)"""
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    
    url = "https://www.vtb.ru/personal/vklady-i-scheta/obezlichennyj-metallicheskij-schet/"
    metals = []
    
    try:
        print("⏳ Загрузка ВТБ через Selenium...")
        
        # Настройки браузера (безголовый режим, чтобы не открывалось окно)
                # Указываем путь к Chrome, который мы скачали на Render
        if os.path.exists("./chrome/chrome-linux64/chrome"):
            chrome_options.binary_location = "./chrome/chrome-linux64/chrome"
            os.environ["PATH"] += os.pathsep + os.path.abspath("./chrome/chromedriver-linux64")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Запускаем браузер
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        
        # Ждём 7 секунд, чтобы страница прогрузилась
        time.sleep(7)
        
        # Получаем весь текст страницы
        page_text = driver.find_element(By.TAG_NAME, "body").text
                # Временная отладка: сохраняем текст страницы в файл, чтобы посмотреть, что видит Selenium
        with open("vtb_debug.txt", "w", encoding="utf-8") as f:
            f.write(page_text)
        driver.quit()
        driver.quit()
        
        # Ищем блоки с металлами
        import re
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
        
        target_metals = ["Золото", "Серебро", "Платина", "Палладий"]
        
        for i, line in enumerate(lines):
            if line in target_metals:
                # Ищем следующие строки с цифрами (цены)
                prices = []
                for j in range(1, 6):
                    if i + j < len(lines):
                        # Ищем числа с запятой (например, 10 173,33)
                        match = re.search(r'(\d[\d\s]*,\d{2})', lines[i + j])
                        if match:
                            prices.append(match.group(1).strip())
                    if len(prices) == 2:
                        break
                
                if len(prices) == 2:
                    metals.append({
                        "name": line,
                        "buy": prices[0],
                        "sell": prices[1],
                        "source": "ВТБ"
                    })
        
    except Exception as e:
        print(f"❌ Ошибка ВТБ (Selenium): {e}")
        return [{"name": "Золото", "buy": "Ошибка", "sell": "Ошибка", "source": "ВТБ"}]
        
    return metals
def get_all_data():
    """Собирает данные со всех источников"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск парсинга...")
    
    data = {
        "cash_gold": get_cash_gold(),
        "vtb": get_vtb_metals(), # Переименовали ключ, но по сути это теперь ЦБ
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }
    
    if data["cash_gold"]:
        save_to_csv(data["cash_gold"], data["timestamp"])
        
    print(f"[{data['timestamp']}] ✅ Парсинг завершен.")
    return data

def save_to_csv(results, timestamp):
    file_exists = os.path.isfile("history.csv")
    with open("history.csv", mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        if not file_exists:
            writer.writerow(["Дата", "Металл", "Название", "Цена за грамм", "Премиум цена"])
            
        for item in results["gold"]:
            writer.writerow([timestamp, "Золото", item["name"], item["price"], item["premium"] or "-"])
        for item in results["silver"]:
            writer.writerow([timestamp, "Серебро", item["name"], item["price"], "-"])

if __name__ == "__main__":
    get_all_data()
