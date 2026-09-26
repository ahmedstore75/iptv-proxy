import os
import json
import requests

API_URL = "http://198.195.239.50/tv_channels.json"
OUTPUT_DIR = "Bangla-Iptv"

# ফ্রি বাংলাদেশ (BD) প্রক্সি লিস্ট (IP:Port)
# ফ্রি প্রক্সিগুলো সময়ে সময়ে পরিবর্তন হতে পারে, তাই না চললে নতুন BD Proxy আপডেট করে নিন
FREE_BD_PROXIES = [
    "http://103.119.100.17:8080",
    "http://103.150.190.2:8080",
    "http://103.134.88.2:8080",
    "http://103.204.244.130:8080",
    "http://103.106.238.10:8080"
]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def fetch_data_with_free_proxy(url, headers):
    """
    ফ্রি প্রক্সিগুলোর মধ্য থেকে একের পর এক চেষ্টা করে ডাটা ফেচ করার ফাংশন
    """
    # প্রথমে প্রক্সি ছাড়া সরাসরি চেষ্টা করবে
    try:
        print("⚡ Trying direct connection without proxy...")
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            print("✅ Directly fetched successfully!")
            return res.json()
    except Exception:
        print("⚠️ Direct connection failed. Switching to Free BD Proxies...\n")

    # ফ্রি প্রক্সি দিয়ে চেষ্টা করা
    for proxy in FREE_BD_PROXIES:
        proxies = {
            "http": proxy,
            "https": proxy
        }
        try:
            print(f"🔄 Trying BD Proxy: {proxy}")
            res = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            if res.status_code == 200:
                print(f"✅ Successfully fetched data using proxy: {proxy}")
                return res.json()
        except Exception as e:
            print(f"❌ Proxy {proxy} failed or timed out.")

    raise Exception("All free proxies failed to connect.")

def generate_playlists():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print("Fetching JSON data from API...")
        data = fetch_data_with_free_proxy(API_URL, headers)

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
            
        print(f"✅ M3U playlist with Cookies saved successfully ({valid_channel_count} channels).")

    except Exception as e:
        print(f"❌ Error generating playlists: {e}")

if __name__ == "__main__":
    generate_playlists()
