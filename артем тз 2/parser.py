import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

def get_cbr_usd():
    """Берем курс доллара с сайта ЦБ"""
    try:
        resp = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        return resp.json()["Valute"]["USD"]["Value"]
    except:
        return 90.0 # Если ЦБ недоступен, берем примерный курс

def get_prices():
    url = "https://cash-gold.ru"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    usd_rate = get_cbr_usd()
    
    results = {"gold": [], "silver": [], "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"), "usd": usd_rate}

    # Золото
    gold_container = soup.find(id="gold-probes")
    if gold_container:
        for btn in gold_container.find_all("button", class_="probe-btn"):
            name = btn.get("data-name")
            price = btn.get("data-price")
            premium = btn.get("data-premium-price")
            
            if name and price:
                # Присваиваем статус на основе цены (искусственно, для визуала)
                # В реальности тут должна быть логика сравнения с биржей
                status = "минимум"
                if int(price) > 10000:
                    status = "в диапазоне"

                results["gold"].append({
                    "name": name,
                    "price": int(price),
                    "premium": int(premium) if premium else None,
                    "status": status
                })

    # Серебро
    silver_container = soup.find(id="silver-probes")
    if silver_container:
        for btn in silver_container.find_all("button", class_="probe-btn"):
            name = btn.get("data-name")
            price = btn.get("data-price")
            if name and price:
                results["silver"].append({
                    "name": name,
                    "price": int(price),
                    "premium": None,
                    "status": "минимум"
                })

    # Сохраняем историю в CSV
    save_to_csv(results)
    
    print(f"[{results['timestamp']}] ✅ Данные обновлены. Курс USD: {usd_rate:.2f}")
    return results

def save_to_csv(results):
    file_exists = os.path.isfile("history.csv")
    with open("history.csv", mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        if not file_exists:
            writer.writerow(["Дата", "Металл", "Название", "Цена за грамм", "Премиум цена", "Статус"])
            
        for item in results["gold"]:
            writer.writerow([results["timestamp"], "Золото", item["name"], item["price"], item["premium"] or "-", item["status"]])
        for item in results["silver"]:
            writer.writerow([results["timestamp"], "Серебро", item["name"], item["price"], "-", item["status"]])

if __name__ == "__main__":
    get_prices()