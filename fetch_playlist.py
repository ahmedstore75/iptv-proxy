import os
import json
import requests

API_URL = "https://sm-monirul.top/api/app/info/channel_data.json"
OUTPUT_DIR = "Bangla-Iptv"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_playlists():
    # ব্রাউজারের মতো রিকোয়েস্ট পাঠানোর জন্য User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        # ১. JSON ফাইল সেভ
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved.")

        # ২. M3U ফাইল তৈরি
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        m3u_content = "#EXTM3U\n"

        # ডাটা স্ট্রাকচার চেক
        channels = data
        if isinstance(data, dict):
            channels = data.get("channels") or data.get("data") or data.get("categories", [])

        for channel in channels:
            # যদি নেস্টেড ডাটা থাকে (ক্যাটাগরি বা লিস্ট হিসেবে)
            if isinstance(channel, dict):
                name = channel.get("name") or channel.get("title") or channel.get("channel_name", "Unknown")
                logo = channel.get("logo") or channel.get("icon") or channel.get("image", "")
                url = channel.get("url") or channel.get("link") or channel.get("stream_url", "")

                if url:
                    m3u_content += f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{url}\n'

        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print("✅ M3U playlist saved.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    generate_playlists()
