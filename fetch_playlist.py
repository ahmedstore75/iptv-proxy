import os
import json
import requests

API_URL = "http://198.195.239.50/tv_channels.json"
OUTPUT_DIR = "Bangla-Iptv"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_fresh_bd_proxies():
    """
    বিভিন্ন প্রক্সি সোর্স থেকে অটোমেটিক লাইভ বাংলাদেশ (BD) প্রক্সি সংগ্রহ করবে
    """
    bd_proxies = []
    
    # সোর্স ১: Proxyscrape API (BD Proxies)
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

    # সোর্স ২: ব্যাকআপ ম্যানুয়াল প্রক্সি লিস্ট (নতুন কার্যকর প্রক্সি পেলে এখানে আপডেট করতে পারেন)
    backup_list = [
        "http://103.119.100.17:8080",
        "http://103.150.190.2:8080",
        "http://103.134.88.2:8080",
        "http://103.204.244.130:8080",
        "http://103.106.238.10:8080"
    ]
    
    for p in backup_list:
        if p not in bd_proxies:
            bd_proxies.append(p)
            
    return bd_proxies

def fetch_data_with_proxy(url, headers):
    # প্রথমে প্রক্সি ছাড়া সরাসরি ট্রাই করা (যদি কখনো ওপেন থাকে)
    try:
        print("⚡ Trying direct connection without proxy...")
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            print("✅ Directly fetched successfully!")
            return res.json()
    except Exception:
        print("⚠️ Direct connection failed. Fetching BD Proxies...\n")

    # লাইভ প্রক্সি সংগ্রহ
    proxies_to_try = get_fresh_bd_proxies()
    print(f"🔍 Found {len(proxies_to_try)} BD proxies to test...")

    for proxy in proxies_to_try:
        proxies = {"http": proxy, "https": proxy}
        try:
            print(f"🔄 Trying BD Proxy: {proxy}")
            res = requests.get(url, headers=headers, proxies=proxies, timeout=12)
            if res.status_code == 200:
                print(f"✅ Successfully fetched data using proxy: {proxy}")
                return res.json()
        except Exception:
            print(f"❌ Proxy {proxy} failed or timed out.")

    raise Exception("All fetched BD proxies failed to connect.")

def generate_playlists():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print("Fetching JSON data from API...")
        data = fetch_data_with_proxy(API_URL, headers)

        # ১. অ্যাপ ইনফো আপডেট করা
        data["app_name"] = "Bangla Iptv"
        data["developed_by"] = "Ahammad Ali"
        data["telegram_channel"] = "https://t.me/banglatvlivefree"

        # ২. JSON ফাইল সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved successfully.")

        # ৩. M3U ফাইল তৈরি করা (কুকিজ সাপোর্টসহ)
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        m3u_content = "#EXTM3U\n"
        
        valid_channel_count = 0
        categories = data.get("categories", [])
        
        for category in categories:
            cat_name = category.get("name", "General")
            channels = category.get("channels", [])
            
            for ch in channels:
                name = ch.get("name", "Unknown Channel")
                logo = ch.get("logo", "")
                url = ch.get("stream_url", "")
                cookie = ch.get("cookie", "")

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
