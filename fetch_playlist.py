import os
import json
import requests

API_URL = "http://198.195.239.50/tv_channels.json"
OUTPUT_DIR = "Bangla-Iptv"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_fresh_bd_proxies():
    """
    লাইভ প্রক্সি সোর্স থেকে বাংলাদেশ প্রক্সি সংগ্রহ করবে
    """
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
    
    # ১. প্রথমে সরাসরি চেষ্টা
    try:
        print("⚡ Trying direct connection...")
        res = requests.get(API_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            print("✅ Directly fetched successfully!")
            return res.json()
    except Exception:
        print("⚠️ Direct connection failed. Trying BD Proxies...\n")

    # ২. প্রক্সি দিয়ে চেষ্টা
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

def generate_playlists():
    try:
        print("Fetching JSON data from API...")
        data = fetch_data()

        # ১. অ্যাপ ইনফো আপডেট করা
        data["app_name"] = "Bangla Iptv"
        data["developed_by"] = "Ahammad Ali"
        data["telegram_channel"] = "https://t.me/banglatvlivefree"

        # ২. JSON ফাইল সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved successfully.")

        # ৩. M3U ফাইল তৈরি করা (স্ক্রিনশটের সঠিক JSON অবজেক্ট অনুযায়ী)
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        m3u_content = "#EXTM3U\n"
        
        valid_channel_count = 0
        channels = data.get("channels", []) # স্ক্রিনশট অনুযায়ী "channels" তালিকা নেওয়া হলো
        
        for ch in channels:
            # যদি স্ট্যাটাস "hidden" থাকে তবে বাদ দিতে পারেন, সাধারণ অবস্থায় সব প্রসেস হবে
            name = ch.get("name", "Unknown Channel")
            cat_name = ch.get("category", "General")
            logo = ch.get("logo", "")
            url = ch.get("url", "") or ch.get("stream_url", "")
            cookie = ch.get("cookie", "")

            # লোগো যদি রিলেটিভ পাথ থাকে তবে ফুল URL বানানো (যেমন: img/channels/...)
            if logo and not logo.startswith("http"):
                logo = f"http://198.195.239.50/{logo}"

            if url:
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="{cat_name}",{name}\n'
                if cookie:
                    m3u_content += f'#EXTVLCOPT:http-cookie={cookie}\n'
                m3u_content += f'{url}\n'
                valid_channel_count += 1

        # ৪. M3U ফাইল সেভ করা
        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.write(m3u_content)
            
        print(f"✅ M3U playlist saved successfully ({valid_channel_count} channels).")

    except Exception as e:
        print(f"❌ Error generating playlists: {e}")

if __name__ == "__main__":
    generate_playlists()
