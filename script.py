import os
import json
import requests

API_URL = "https://iptvlive-beta.vercel.app"
OUTPUT_DIR = "Bangla"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_playlists():
    # ব্রাউজার ট্র্যাকিং এড়াতে সম্পূর্ণ হেডার ব্যবহার
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        print("Fetching JSON data from API...")
        response = requests.get(API_URL, headers=headers, timeout=20)
        
        # স্ট্যাটাস কোড চেক
        print(f"API Response Status Code: {response.status_code}")
        response.raise_for_status()

        # রিসপন্স ডাটা প্রিন্ট করে চেক করা (যদি ফাঁকা থাকে)
        if not response.text.strip():
            raise ValueError("API returned empty response!")

        # JSON পার্স করা
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("⚠️ API didn't return valid JSON! Response snippet:")
            print(response.text[:300]) # প্রথম ৩০০ ক্যারেক্টার দেখাবে সমস্যার ধরণ বুঝতে
            return

        # ১. অ্যাপ ইনফো আপডেট করা
        data["app_name"] = "Bangla Iptv"
        data["developed_by"] = "Ahammad Ali"
        data["telegram_channel"] = "https://t.me/banglatvlivefree"

        # ২. JSON ফাইল সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved successfully.")

        # ৩. M3U ফাইল তৈরি করা
        m3u_lines = ["#EXTM3U\n"]
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
                    m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{cat_name}",{name}\n')
                    
                    if cookie:
                        m3u_lines.append(f'#EXTVLCOPT:http-cookie={cookie}\n')
                    
                    m3u_lines.append(f'{url}\n')
                    valid_channel_count += 1

        # ৪. M3U ফাইল সেভ করা
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.writelines(m3u_lines)
            
        print(f"✅ M3U playlist saved successfully ({valid_channel_count} channels).")

    except Exception as e:
        print(f"❌ Error generating playlists: {e}")

if __name__ == "__main__":
    generate_playlists()
