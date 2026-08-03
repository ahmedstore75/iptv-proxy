import os
import json
import requests

API_URL = "https://sm-monirul.top/api/app/info/channel_data.json"
OUTPUT_DIR = "Bangla-Iptv"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_playlists():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        # ১. JSON প্লেলিস্ট সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved.")

        # ২. ডাটা থেকে চ্যানেলের লিস্ট বের করা
        channels = []
        if isinstance(data, list):
            channels = data
        elif isinstance(data, dict):
            # সম্ভাব্য সকল key চেক করা হচ্ছে
            for key in ["channels", "data", "channel", "result", "list"]:
                if key in data and isinstance(data[key], list):
                    channels = data[key]
                    break
            # যদি কোনো নির্দিষ্ট key না থাকে, তবে ডিকশনারির ভেতরের ভ্যালু সংগ্রহ করা
            if not channels:
                for val in data.values():
                    if isinstance(val, list):
                        channels.extend(val)

        print(f"Total channels found: {len(channels)}")

        # ৩. M3U ফাইল তৈরি করা
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        m3u_content = "#EXTM3U\n"

        valid_channel_count = 0
        for ch in channels:
            if isinstance(ch, dict):
                # চ্যানেল নাম, লোগো এবং লিঙ্ক খোঁজা
                name = (ch.get("name") or ch.get("channel_name") or 
                        ch.get("title") or ch.get("channel_title") or "Unknown Channel")
                
                logo = (ch.get("logo") or ch.get("icon") or 
                        ch.get("image") or ch.get("channel_logo") or "")
                
                url = (ch.get("url") or ch.get("stream_url") or 
                       ch.get("link") or ch.get("src") or ch.get("stream") or "")

                if url:
                    m3u_content += f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{url}\n'
                    valid_channel_count += 1

        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        print(f"✅ M3U playlist saved with {valid_channel_count} channels.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_playlists()
