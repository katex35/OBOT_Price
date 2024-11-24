import os
from flask import Flask, render_template, jsonify
import requests
import threading
import time

app = Flask(__name__)

# Dexscreener API URL ve Parametreler
CHAIN_ID = "solana"
PAIR_ID = "7GqEtF893LmBj7XLmpEAswvE6bpoBP4aYTQK9xMrfNwb"
DEXSCREENER_URL = f"https://api.dexscreener.com/latest/dex/pairs/{CHAIN_ID}/{PAIR_ID}"

# Global fiyat değişkenleri
current_price = {"price": 0.0}  # Mevcut fiyat
previous_price = {"price": 0.0}  # Önceki fiyat


# API'den fiyat çekme işlemi
def fetch_price():
    global current_price, previous_price
    while True:
        try:
            response = requests.get(DEXSCREENER_URL)  # Dexscreener API çağrısı
            data = response.json()

            # `priceUsd` alanından fiyat bilgisi alınır
            if data and data.get("pairs") and len(data["pairs"]) > 0:
                dex_price = float(data["pairs"][0]["priceUsd"])
                previous_price["price"] = current_price["price"]  # Önceki fiyatı güncelle
                current_price["price"] = dex_price  # Mevcut fiyatı güncelle
                print(f"Fiyat güncellendi: {dex_price}")
            else:
                print("Dexscreener API'den geçerli fiyat bilgisi alınamadı.")
        except Exception as e:
            print(f"API hatası: {e}")
        
        time.sleep(1.5)  # Her 5 saniyede bir API'yi çağır


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/price")
def price():
    # JSON formatında güncellenmiş fiyatları döndür
    return jsonify({
        "current": current_price["price"],
        "previous": previous_price["price"]
    })


if __name__ == "__main__":
    # Fiyat çekme işlemini ayrı bir thread ile başlat
    price_thread = threading.Thread(target=fetch_price)
    price_thread.daemon = True
    price_thread.start()
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))