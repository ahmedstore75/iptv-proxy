import os
import json
import re
import requests
from urllib.parse import quote

API_URL = "http://198.195.239.50/tv_channels.json"
BASE_URL = "http://198.195.239.50/"
OUTPUT_DIR = "Bangla-Iptv"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# স্ক্রিনশট ও এপিআই-এর সমস্ত ভিন্ন বানানের চ্যানেলকে ১টি স্ট্যান্ডার্ড নামে ম্যাপ করার লিস্ট
CHANNEL_NAME_MAP = {
    # Sports Channels
    "SONY.SPORTS.1": "Sony Sports Ten 1 HD",
    "SONY.SPORTS.1.HD": "Sony Sports Ten 1 HD",
    "SONY.SPORTS.2": "Sony Sports Ten 2 HD",
    "SONY.SPORTS2.HD": "Sony Sports Ten 2 HD",
    "SONY.SPORTS.3": "Sony Sports Ten 3 HD",
    "SONY.SPORTS.4": "Sony Sports Ten 4 HD",
    "SONY-SPORTS.5HD": "Sony Sports Ten 5 HD",
    "SONY.SPORTS.5": "Sony Sports Ten 5 HD",
    "STAR-SPORTS.1": "Star Sports 1 HD",
    "STAR.SPORTS1.HD": "Star Sports 1 HD",
    "STAR-SPORTS.2": "Star Sports 2 HD",
    "STAR.SPORTS2.HD": "Star Sports 2 HD",
    "STAR-SPORTS.3": "Star Sports 3 HD",
    "A.SPORTS.HD": "A Sports HD",
    "EUROSPORTS.HD": "Eurosport HD",
    "FAST.SPORTS.HD": "Fast Sports HD",
    "GOLF.SPORTS": "Golf Channel",
    "PTV-SPORTS-HD": "PTV Sports HD",
    "SHOMOY TV HD": "Somoy TV HD",
    
    # Bangla Channels
    "COLOR BANGLA CHIN...": "Colors Bangla Cinema",
    "COLORS.BANGLA.CINEMA": "Colors Bangla Cinema",
    "COLOR BANGLA HD": "Colors Bangla HD",
    "COLORS.BANGLA.HD": "Colors Bangla HD",
    "ENTER 10 BANGLA": "Enter10 Bangla",
    "ENTER10.BANGLA": "Enter10 Bangla",
    "JALSHA MOVIES HD": "Jalsha Movies HD",
    "SONY AATH": "Sony Aath",
    "SONY.AAT": "Sony Aath",
    "STAR JALSHA HD": "Star Jalsha HD",
    "SUN.BANGLA.HD": "Sun Bangla HD",
    "ZEE BANGLA HD": "Zee Bangla HD",
    "ZEE.BANGLA.CINEMA": "Zee Bangla Cinema",
}

# সনি স্পোর্টস ও স্টার স্পোর্টস ১, ২, ৩, ৪ অনুযায়ী সাজানোর কাস্টম অর্ডারিং
EXACT_CHANNEL_ORDER = [
    # Sports Ordering
    "Sony Sports Ten 1 HD",
    "Sony Sports Ten 2 HD",
    "Sony Sports Ten 3 HD",
    "Sony Sports Ten 4 HD",
    "Sony Sports Ten 5 HD",
    "Star Sports 1 HD",
    "Star Sports 2 HD",
    "Star Sports 3 HD",
    "A Sports HD",
    "Eurosport HD",
    "Fast Sports HD",
    "Golf Channel",
    "PTV Sports HD",
    "Somoy TV HD",
    
    # Bangla Ordering
    "Star Jalsha HD",
    "Zee Bangla HD",
    "Colors Bangla HD",
    "Colors Bangla Cinema",
    "Jalsha Movies HD",
    "Zee Bangla Cinema",
    "Sony Aath",
    "Enter10 Bangla",
    "Sun Bangla HD"
]

def get_fresh_bd_proxies():
    bd_proxies = []
    try:
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=BD&ssl=all&anonymity=all"
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and res.text:
            lines = res.text.strip().split("\r\n")
            for line in lines:
                if ":" in line:
                    bd_proxies.append(f"http://{line.strip()}")
    except Exception:
        pass

    backup_list = [
        "http://103.119.100.17:8080",
        "http://103.150.190.2:8080",
        "http://103.134.88.2:8080",
        "http://103.204.244.130:8080"
    ]
    for p in backup_list:
        if p not in bd_proxies:
            bd_proxies.append(p)
            
    return bd_proxies

def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive"
    }
    
    try:
        print("⚡ Trying direct connection...")
        res = requests.get(API_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            print("✅ Directly fetched successfully!")
            return res.json()
    except Exception:
        print("⚠️ Direct connection failed. Trying BD Proxies...\n")

    proxies_list = get_fresh_bd_proxies()
    for proxy in proxies_list:
        proxies = {"http": proxy, "https": proxy}
        try:
            print(f"🔄 Trying BD Proxy: {proxy}")
            res = requests.get(API_URL, headers=headers, proxies=proxies, timeout=12)
            if res.status_code == 200:
                print(f"✅ Successfully fetched using proxy: {proxy}")
                return res.json()
        except Exception:
            print(f"❌ Proxy {proxy} failed.")

    raise Exception("Could not fetch data via direct or proxy connection.")

def fix_logo_url(logo_path):
    if not logo_path:
        return ""
    if logo_path.startswith("http://") or logo_path.startswith("https://"):
        return logo_path
    
    clean_path = logo_path.lstrip("/")
    encoded_path = quote(clean_path, safe="/")
    return f"{BASE_URL}{encoded_path}"

def standardize_channel_name(raw_name):
    """
    যেকোনো এলেমেলো নামকে ম্যানুয়াল ম্যাপের সাহায্যে সুন্দর এবং স্ট্যান্ডার্ড নামে রূপান্তর করবে।
    """
    clean_key = raw_name.strip().upper()
    for key, std_name in CHANNEL_NAME_MAP.items():
        if key.upper() == clean_key:
            return std_name
        
    # ম্যানুয়াল তালিকায় না থাকলে সাধারণ ক্লিন করা নাম রিটার্ন করবে
    clean = re.sub(r'[\.\_\-]+', ' ', raw_name)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def remove_duplicates_strictly(channels):
    seen_names = set()
    unique_channels = []

    for ch in channels:
        raw_name = ch.get("name", "")
        # প্রথমে নামটিকে স্ট্যান্ডার্ড করে নেওয়া
        std_name = standardize_channel_name(raw_name)
        ch["name"] = std_name  # আপডেট নাম সেভ হলো

        # একই স্ট্যান্ডার্ড নামের চ্যানেল একবারের বেশি থাকবে না
        if std_name not in seen_names:
            seen_names.add(std_name)
            unique_channels.append(ch)

    return unique_channels

def generate_playlists():
    try:
        print("Fetching JSON data from API...")
        data = fetch_data()

        # ১. অ্যাপ ইনফো আপডেট
        data["app_name"] = "Bangla Iptv"
        data["developed_by"] = "Ahammad Ali"
        data["telegram_channel"] = "https://t.me/banglatvlivefree"

        raw_channels = data.get("channels", [])

        # ২. ম্যানুয়াল ম্যাপিং এবং ডুপ্লিকেট ছাঁটাই
        channels = remove_duplicates_strictly(raw_channels)
        print(f"🧹 Duplicates Removed: {len(raw_channels)} -> {len(channels)} unique channels.")

        # ৩. লোগো লিংক ঠিক করা
        for ch in channels:
            raw_logo = ch.get("logo", "")
            ch["logo"] = fix_logo_url(raw_logo)

        # ৪. ক্যাটাগরি এবং ক্রমানুসারে সাজানো
        category_order = {
            "Bangla": 1,
            "Indian Bangla": 2,
            "Sports": 3,
            "News": 4,
            "Entertainment": 5,
            "Movies": 6,
            "Hindi": 7,
            "Kids": 8,
            "Music": 9,
            "General": 10
        }

        def master_sort_key(ch):
            cat = ch.get("category", "General").strip()
            cat_rank = category_order.get(cat, 999)
            
            name = ch.get("name", "")
            
            # EXACT_CHANNEL_ORDER লিস্ট অনুযায়ী সিকোয়েন্স ঠিক করা
            if name in EXACT_CHANNEL_ORDER:
                name_rank = EXACT_CHANNEL_ORDER.index(name)
            else:
                name_rank = 999

            return (cat_rank, cat, name_rank, name)

        sorted_channels = sorted(channels, key=master_sort_key)
        data["channels"] = sorted_channels

        # ৫. JSON ফাইল সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved successfully.")

        # ৬. M3U ফাইল সেভ করা
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        m3u_content = "#EXTM3U\n"
        
        valid_channel_count = 0
        
        for ch in sorted_channels:
            name = ch.get("name", "Unknown Channel")
            cat_name = ch.get("category", "General")
            logo = ch.get("logo", "")
            url = ch.get("url", "") or ch.get("stream_url", "")
            cookie = ch.get("cookie", "")

            if url:
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="{cat_name}",{name}\n'
                if cookie:
                    m3u_content += f'#EXTVLCOPT:http-cookie={cookie}\n'
                m3u_content += f'{url}\n'
                valid_channel_count += 1

        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.write(m3u_content)
            
        print(f"✅ M3U playlist saved successfully ({valid_channel_count} channels).")

    except Exception as e:
        print(f"❌ Error generating playlists: {e}")

if __name__ == "__main__":
    generate_playlists()
