import os
import json
import requests

API_URL = "https://sm-monirul.top/api/app/info/channel_data.json"
OUTPUT_DIR = "Bangla-Iptv"

# ফোল্ডার না থাকলে তৈরি করবে
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_playlists():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        print("Fetching JSON data from API...")
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        # ১. আপনার চাহিদা অনুযায়ী অ্যাপ সম্পর্কিত তথ্য পরিবর্তন (Customize App Info)
        data["app_name"] = "Bangla Iptv"
        data["developed_by"] = "Ahammad Ali"
        data["telegram_channel"] = "https://t.me/banglatvlivefree"

        # ২. কাস্টমাইজড JSON ফাইল সেভ করা (Bangla-Iptv/playlist.json)
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved with custom app info.")

        # ৩. M3U ফাইল তৈরি করা
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        m3u_content = "#EXTM3U\n"
        
        valid_channel_count = 0

        # categories থেকে ডাটা এক্সট্র্যাক্ট করা
        categories = data.get("categories", [])
        
        for category in categories:
            cat_name = category.get("name", "General") # ক্যাটাগরির নাম (যেমন: Bangla)
            channels = category.get("channels", [])
            
            for ch in channels:
                name = ch.get("name", "Unknown Channel")
                logo = ch.get("logo", "")
                url = ch.get("stream_url", "")

                if url:
                    # m3u হেডার ফরম্যাটে group-title হিসেবে ক্যাটাগরির নাম যুক্ত করা
                    m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="{cat_name}",{name}\n{url}\n'
                    valid_channel_count += 1

        # ৪. M3U ফাইল সেভ করা (Bangla-Iptv/playlist.m3u)
        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.write(m3u_content)
            
        print(f"✅ M3U playlist saved successfully with {valid_channel_count} channels.")

    except Exception as e:
        print(f"❌ Error generating playlists: {e}")

if __name__ == "__main__":
    generate_playlists()
