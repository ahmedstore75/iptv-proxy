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

def clean_text_for_comparison(text):
    """
    যেকোনো টেক্সট বা ইউআরএল থেকে ডট, স্পেস, ড্যাশ সরিয়ে 
    একদম কমন ক্যাপিটাল লেটারে রূপান্তর করে যেন হুবহু তুলনা করা যায়।
    """
    if not text:
        return ""
    clean = re.sub(r'[\.\_\-\s\/]+', '', str(text))
    return clean.upper().strip()

def remove_all_duplicates(channels):
    """
    সমস্ত চ্যানেলের নাম ও স্ট্রিম ইউআরএল চেকের মাধ্যমে যেকোনো ডুপ্লিকেট বাদ দেবে।
    """
    seen_normalized_names = set()
    seen_normalized_urls = set()
    unique_channels = []

    for ch in channels:
        raw_name = ch.get("name", "")
        raw_url = ch.get("url", "") or ch.get("stream_url", "")
        
        norm_name = clean_text_for_comparison(raw_name)
        norm_url = clean_text_for_comparison(raw_url)

        # নাম অথবা স্ট্রিম লিঙ্ক যেকোনো একটি মিলে গেলেই সেটাকে ডুপ্লিকেট ধরা হবে
        if norm_name not in seen_normalized_names and norm_url not in seen_normalized_urls:
            if norm_name:
                seen_normalized_names.add(norm_name)
            if norm_url:
                seen_normalized_urls.add(norm_url)
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

        # ২. সব ডুপ্লিকেট চ্যানেল একবারে বাদ দেওয়া
        channels = remove_all_duplicates(raw_channels)
        print(f"🧹 Successfully cleaned duplicates: {len(raw_channels)} total -> {len(channels)} unique channels remaining.")

        # ৩. লোগো লিংক সম্পূর্ণ ইউআরএল করা
        for ch in channels:
            raw_logo = ch.get("logo", "")
            ch["logo"] = fix_logo_url(raw_logo)

        # ৪. ক্যাটাগরি সাজানোর সিকোয়েন্স
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
            
            # Sony Sports 1, Sony Sports 2, Sony Sports 3 ক্রমানুসারে সাজানোর লজিক
            name_parts = [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', name)]
            
            return (cat_rank, cat, name_parts)

        sorted_channels = sorted(channels, key=sort_key)
        data["channels"] = sorted_channels

        # ৫. JSON ফাইল সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved successfully (No Duplicates across all channels).")

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
