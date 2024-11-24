from flask import Flask, render_template, jsonify
from requests import Session, ConnectionError, Timeout, TooManyRedirects
import json
import threading
import time

app = Flask(__name__)

# API ve global değişkenler
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {
    'id': '33986',  # OBOT'un ID'si
    'convert': 'USD'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '2b1d2be1-b8db-4e78-b793-a5467c44c588',
}

current_price = {"price": 0.0}  # Mevcut fiyat
previous_price = {"price": 0.0}  # Önceki fiyat

# API'den fiyat çekme işlemi
def fetch_price():
    global current_price, previous_price
    session = Session()
    session.headers.update(headers)

    while True:
        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            obot_price = data['data']['33986']['quote']['USD']['price']

            # Önceki fiyatı güncelle ve yeni fiyatı sakla
            previous_price["price"] = current_price["price"]
            current_price["price"] = obot_price
            print(f"Fiyat güncellendi: {obot_price}")
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(f"API hatası: {e}")
        
        time.sleep(10)  # Her 10 saniyede bir fiyatı API'den güncelle

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/price")
def price():
    # Sadece güncellenmiş fiyatları döndür
    return jsonify({
        "current": current_price["price"],
        "previous": previous_price["price"]
    })

if __name__ == "__main__":
    # Fiyat çekme işlemini arka planda başlat
    price_thread = threading.Thread(target=fetch_price)
    price_thread.daemon = True
    price_thread.start()
    app.run(debug=True)