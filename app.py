from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/7GqEtF893LmBj7XLmpEAswvE6bpoBP4aYTQK9xMrfNwb"
APT_DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/tokens/0x8512b34017e087c3707748869ddc317d83f3fe70ab3a162abdc055c761ca9906::OBOT::OBOT"
OSOL_DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/tokens/HeLp6NuQkmYB4pYWo2zYs22mESHXPQYzXbB8n4V98jwC"
OSOL_DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/tokens/7ukzrv5JkFrHCgGkv8GaUTxXhV2KHsCWcjzYqkNSTWZq"

def format_market_cap(market_cap):
    if market_cap >= 1_000_000_000:
        return f"{market_cap / 1_000_000_000:.1f}B"  # Milyar için B
    elif market_cap >= 1_000_000:
        return f"{market_cap / 1_000_000:.1f}M"  # Milyon için M
    elif market_cap >= 1_000:
        return f"{market_cap / 1_000:.1f}K"  # Bin için K
    else:
        return str(market_cap)  # Eğer 1000'den küçükse direkt sayıyı döndür

current_price = 0.0
previous_price = 0.0
price_change_24h = 0.0


def fetch_price():
    """Fetch price data from Dexscreener API"""
    global current_price, previous_price, price_change_24h
    try:
        response = requests.get(DEXSCREENER_URL, timeout=10)  
        response.raise_for_status()  
        data = response.json()

        price = data.get("pair", {}).get("priceUsd", None)
        change_24h = data.get("pair", {}).get("priceChange", {}).get("h24", 0.0)


        if price:
            previous_price = current_price
            current_price = float(price)
            price_change_24h = float(change_24h)
            return current_price, previous_price, price_change_24h
        else:
            return None, None, None
    except requests.exceptions.RequestException:
        return None, None, None
    except Exception:
        return None, None, None
    
apt_current_price = 0.0
apt_previous_price = 0.0
apt_price_change_24h = 0.0

def fetch_apt_price():
    """Fetch price data from Dexscreener API"""
    global apt_current_price, apt_previous_price, apt_price_change_24h
    try:
        response = requests.get(APT_DEXSCREENER_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        pairs = data.get("pairs", [])
        if pairs:
            price = pairs[0].get("priceUsd")
            price_change = pairs[0].get("priceChange", {}).get("h24", 0.0)


            if price:
                apt_previous_price = apt_current_price
                apt_current_price = float(price)
                apt_price_change_24h = float(price_change)
                return apt_current_price, apt_previous_price, apt_price_change_24h

        return None, None, None
    except requests.exceptions.RequestException as e:
        return None, None, None
    except Exception as e:
        return None, None, None
    
osol_current_price = 0.0
osol_previous_price = 0.0
osol_price_change_24h = 0.0

def fetch_osol_price():
    """Fetch price data from Dexscreener API"""
    global osol_current_price, osol_previous_price, osol_price_change_24h
    try:
        response = requests.get(OSOL_DEXSCREENER_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        pairs = data.get("pairs", [])
        if pairs:
            price = pairs[0].get("priceUsd")
            market_cap = pairs[0].get("marketCap")
            price_change = pairs[0].get("priceChange", {}).get("h24", 0.0)


            if price:
                osol_previous_price = osol_current_price
                osol_current_price = float(price)
                osol_price_change_24h = float(price_change)
                return osol_current_price, osol_previous_price, osol_price_change_24h, market_cap

        return None, None, None, None
    except requests.exceptions.RequestException as e:
        return None, None, None, None
    except Exception as e:
        return None, None, None, None
    
@app.route("/")
def home():
    """Home page"""
    return render_template("timer.html")


@app.route("/price")
def price():
    """Price endpoint"""
    current, previous, price_change_24h = fetch_price()
    apt_current, apt_previous, apt_price_change_24h = fetch_apt_price()
    osol_current, osol_previous, osol_price_change_24h, formatted_market_cap = fetch_osol_price()
    if current is not None or apt_current is not None:
        return jsonify({
            "currentPrice": current,
            "previousPrice": previous,
            "priceChange": price_change_24h,
            "aptCurrentPrice": apt_current,
            "aptPreviousPrice":  apt_previous,
            "aptPriceChange": apt_price_change_24h,
            "osolCurrentPrice": osol_current,
            "osolPreviousPrice":  osol_previous,
            "osolPriceChange": osol_price_change_24h,
            "osolMarketCap": formatted_market_cap,
        })
    else:
        return jsonify({"error": "Failed to fetch price"}), 500
    
@app.route('/timer')
def timer():
    return render_template('timer.html')

@app.route('/osol')
def osol():
    return render_template('osol.html')

@app.route('/price-osol')
def price_osol():
    return render_template('price-osol.html')

# @app.route('/zenith')
# def zenith():
#     return render_template('zenith.html')

if __name__ == "__main__":
    app.run(debug=True)