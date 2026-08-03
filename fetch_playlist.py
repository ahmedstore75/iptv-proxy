import os
import json
import requests

# ১. API URL এবং ফোল্ডার পাথ নির্ধারণ
API_URL = "https://sm-monirul.top/api/app/info/channel_data.json"
OUTPUT_DIR = "Bangla-Iptv"

# ফোল্ডার না থাকলে তৈরি করা
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_playlists():
    try:
        # ২. API থেকে ডাটা ফেচ করা
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        data = response.json()

        # ৩. JSON প্লেলিস্ট সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("JSON playlist created successfully.")

        # ৪. M3U প্লেলিস্ট তৈরি ও সেভ করা
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        
        # ডাটার স্ট্রাকচার অনুযায়ী মডিফাই করতে হতে পারে (এখানে সাধারণ JSON Array ধরা হয়েছে)
        m3u_content = "#EXTM3U\n"
        
        # ডাটা যদি সরাসরি লিস্ট না হয়ে কোনো কি (key)-এর ভেতর থাকে, তবে তা হ্যান্ডেল করা
        channels = data if isinstance(data, list) else data.get("channels", data.get("data", []))

        for channel in channels:
            # ফিল্ডের নাম API অনুযায়ী চেক করে নিন (যেমন: name, logo, url)
            name = channel.get("name") or channel.get("channel_name", "Unknown Channel")
            logo = channel.get("logo") or channel.get("icon", "")
            url = channel.get("url") or channel.get("stream_url", "")

            if url:
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{url}\n'

        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print("M3U playlist created successfully.")

    except Exception as e:
        print(f"Error fetching or saving playlist: {e}")

if __name__ == "__main__":
    generate_playlists()
