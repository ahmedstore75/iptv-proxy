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

def get_base_channel_identity(name, url):
    """
    চ্যানেলটি ডুপ্লিকেট কি না তা যাচাই করার মূল লজিক।
    নাম থেকে ডট, ড্যাশ, স্পেস, HD/SD লেখা সব কেটে একদম মূল নামটি বের করবে।
    যেমন: 'COLOR BANGLA HD' এবং 'COLORS.BANGLA.A.HD' দুটোই 'COLORBANGLA' তে পরিণত হবে।
    """
    text = f"{name}"
    # ১. ডট, ড্যাশ, আন্ডারস্কোর রিমুভ
    clean = re.sub(r'[\.\_\-\s]+', '', text).upper()
    # ২. এইচডি, এসডি শব্দ বা অতিরিক্ত ক্যারেক্টার ছেঁটে ফেলা
    clean = re.sub(r'(HD|SD|CINEMA|CHANNEL)$', '', clean)
    clean = re.sub(r'COLORS', 'COLOR', clean) # COLORS -> COLOR
    clean = re.sub(r'JALSNA', 'JALSHA', clean) # বানানের ভুল ঠিক করা
    
    # ৩. স্ট্রিম ইউআরএল থেকে মূল ফাইল নেম বের করা
    url_clean = ""
    if url:
        match = re.search(r'/([^/]+)/index\.m3u8', url, re.IGNORECASE)
        if match:
            url_clean = re.sub(r'[\.\_\-\s]+', '', match.group(1)).upper()

    return clean, url_clean

def remove_duplicates_strictly(channels):
    seen_identities = set()
    unique_channels = []

    for ch in channels:
        raw_name = ch.get("name", "")
        raw_url = ch.get("url", "") or ch.get("stream_url", "")
        
        name_id, url_id = get_base_channel_identity(raw_name, raw_url)

        # যদি নাম আইডি অথবা ইউআরএল আইডির যেকোনো একটি পূর্বে পেয়ে থাকি তবে তা বাদ যাবে
        if name_id and name_id in seen_identities:
            continue
        if url_id and url_id in seen_identities:
            continue

        if name_id:
            seen_identities.add(name_id)
        if url_id:
            seen_identities.add(url_id)

        unique_channels.append(ch)

    return unique_channels

def get_sort_number(name):
    """
    নামের ভেতরে ১, ২, ৩, ৪ সংখ্যা থাকলে তা বের করে নিয়ে আসবে সর্টিং করার জন্য।
    """
    numbers = re.findall(r'\d+', name)
    if numbers:
        return int(numbers[0])
    return 0

def generate_playlists():
    try:
        print("Fetching JSON data from API...")
        data = fetch_data()

        # ১. অ্যাপ ইনফো আপডেট
        data["app_name"] = "Bangla Iptv"
        data["developed_by"] = "Ahammad Ali"
        data["telegram_channel"] = "https://t.me/banglatvlivefree"

        raw_channels = data.get("channels", [])

        # ২. ডুপ্লিকেট চ্যানেল পুরোপুরি ফিল্টার করা
        channels = remove_duplicates_strictly(raw_channels)
        print(f"🧹 Duplicates Removed: {len(raw_channels)} total -> {len(channels)} clean unique channels.")

        # ৩. লোগো লিংক ফুল ইউআরএল এ রূপান্তর
        for ch in channels:
            raw_logo = ch.get("logo", "")
            ch["logo"] = fix_logo_url(raw_logo)

        # ৪. ক্যাটাগরি অর্ডারিং (Bangla -> Indian Bangla -> Sports...)
        category_order = {
            "Bangla": 1,
            "Indian Bangla": 2,
            "Sports": 3,
            "News": 4,
            "Entertainment": 5,
            "Movies": 6,
            "Hindi": 7,
            "Hindi Movies": 8,
            "Infotainment": 9,
            "Documentary": 10,
            "Kids": 11,
            "Music": 12,
            "Religious": 13,
            "Islamic": 14,
            "English": 15,
            "General": 16
        }

        def master_sort_key(ch):
            cat = ch.get("category", "General").strip()
            cat_rank = category_order.get(cat, 999)
            
            raw_name = ch.get("name", "")
            
            # স্পোর্টস বা একই ব্র্যান্ডের চ্যানেল ১, ২, ৩, ৪ ক্রমানুসারে সাজানোর জন্য
            # মূল ব্রান্ড নেম (যেমন: SONY SPORTS বা STAR SPORTS) এবং তার নাম্বার বের করা
            brand_name = re.sub(r'[\.\_\-\d]+', '', raw_name).strip().upper()
            channel_num = get_sort_number(raw_name)

            return (cat_rank, cat, brand_name, channel_num, raw_name)

        sorted_channels = sorted(channels, key=master_sort_key)
        data["channels"] = sorted_channels

        # ৫. JSON ফাইল সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved successfully (Strictly Sorted & Cleaned).")

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
            
        print(f"✅ M3U playlist saved successfully ({valid_channel_count} unique channels).")

    except Exception as e:
        print(f"❌ Error generating playlists: {e}")

if __name__ == "__main__":
    generate_playlists()
