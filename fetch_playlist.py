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

def clean_channel_name(name):
    """
    চ্যানেলের নাম এবং ইউআরএল তুলনার জন্য নরম্যালাইজ করে সব ক্যারেক্টার ও কেস সমান করবে।
    যেমন: 'ENTER10.BANGLA' এবং 'enter10Bangla' উভয়ই 'ENTER10BANGLA' হয়ে যাবে।
    """
    clean = re.sub(r'[\.\_\-\s]+', '', name)
    return clean.upper().strip()

def remove_duplicates(channels):
    """
    ইউআরএল (Case-insensitive) এবং নামের বৈষম্য রিমুভ করে ডুপ্লিকেট বাদ দেবে।
    """
    seen_names = set()
    seen_urls = set()
    unique_channels = []

    for ch in channels:
        raw_name = ch.get("name", "")
        raw_url = ch.get("url", "") or ch.get("stream_url", "")
        
        normalized_name = clean_channel_name(raw_name)
        # ইউআরএল কেস ইনসেনসিটিভ করার জন্য lower() করা হলো
        normalized_url = raw_url.lower().strip()

        if normalized_name not in seen_names and normalized_url not in seen_urls:
            seen_names.add(normalized_name)
            if normalized_url:
                seen_urls.add(normalized_url)
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

        # ২. ডুপ্লিকেট চ্যানেল ফিল্টার করা
        channels = remove_duplicates(raw_channels)
        print(f"🧹 Removed duplicates: {len(raw_channels)} -> {len(channels)} unique channels.")

        # ৩. লোগো লিংক সম্পূর্ণ ইউআরএল করা
        for ch in channels:
            raw_logo = ch.get("logo", "")
            ch["logo"] = fix_logo_url(raw_logo)

        # ৪. ক্যাটাগরি সাজানোর সিরিয়াল (Priority Order)
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
            "English Movies": 16,
            "English News": 17,
            "International": 18,
            "General": 19
        }

        def sort_key(ch):
            cat = ch.get("category", "General").strip()
            cat_rank = category_order.get(cat, 999)
            
            name = ch.get("name", "")
            
            # সনি স্পোর্টস ও অন্যান্য স্পোর্টস চ্যানেল ১, ২, ৩, ৪ ক্রমানুসারে সাজানোর নিয়ম
            # নামের মধ্যে থাকা সংখ্যাগুলোকে প্রপার ইনটিজার হিসেবে সর্ট করবে
            name_parts = [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', name)]
            
            return (cat_rank, cat, name_parts)

        sorted_channels = sorted(channels, key=sort_key)
        data["channels"] = sorted_channels

        # ৫. JSON সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved successfully (No Duplicates & Alphabetically Sorted).")

        # ৬. M3U সেভ করা
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
