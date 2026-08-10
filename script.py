import os
import json
import requests

API_URL = "https://iptvlive-beta.vercel.app"
# ফোল্ডারের নাম আপনার পছন্দ অনুযায়ী 'Bangla' দেওয়া হলো
OUTPUT_DIR = "Bangla"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_playlists():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print("Fetching JSON data from API...")
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

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
                    # চ্যানলের সাধারণ ইনফো
                    m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{cat_name}",{name}\n')
                    
                    # কুকি থাকলে তা যোগ হবে
                    if cookie:
                        m3u_lines.append(f'#EXTVLCOPT:http-cookie={cookie}\n')
                    
                    # স্ট্রিম লিঙ্ক
                    m3u_lines.append(f'{url}\n')
                    valid_channel_count += 1

        # ৪. M3U ফাইল সেভ করা
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.writelines(m3u_lines)
            
        print(f"✅ M3U playlist with Cookies saved successfully ({valid_channel_count} channels).")

    except Exception as e:
        print(f"❌ Error generating playlists: {e}")

if __name__ == "__main__":
    generate_playlists()
