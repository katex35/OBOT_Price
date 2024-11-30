import os
from flask import Flask, render_template, jsonify
import requests
import threading
import time

app = Flask(__name__)

CHAIN_ID = "solana"
PAIR_ID = "7GqEtF893LmBj7XLmpEAswvE6bpoBP4aYTQK9xMrfNwb"
DEXSCREENER_URL = f"https://api.dexscreener.com/latest/dex/pairs/{CHAIN_ID}/{PAIR_ID}"

current_price = {"price": 0.0}  
previous_price = {"price": 0.0}  
price_change_24h = {"change": 0.0} 


def fetch_price():
    global current_price, previous_price
    while True:
        try:
            response = requests.get(DEXSCREENER_URL)  
            data = response.json()

            if data and data.get("pairs") and len(data["pairs"]) > 0:
                dex_price = float(data["pairs"][0]["priceUsd"])
                change_24h = float(data["pairs"][0]["priceChange"]["h24"])

                previous_price["price"] = current_price["price"]  
                current_price["price"] = dex_price  
                price_change_24h["change"] = change_24h  

                #print(f"Fiyat güncellendi: {dex_price}")
            else:
                print("Dexscreener API'den geçerli fiyat bilgisi alınamadı.")
        except Exception as e:
            print(f"API hatası: {e}")
        
        time.sleep(1.5)  


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/price")
def price():
    return jsonify({
        "current": current_price["price"],
        "previous": previous_price["price"],
        "change_24h": price_change_24h["change"]
    })


if __name__ == "__main__":
    price_thread = threading.Thread(target=fetch_price)
    price_thread.daemon = True
    price_thread.start()
    app.run(debug=True)
    #app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))