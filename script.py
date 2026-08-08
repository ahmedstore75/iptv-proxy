import json
import os
import requests

# ১. টার্গেট URL এবং সেভ করার ফাইল পাথ নির্ধারণ
URL = "http://198.195.239.50/tv_channels.json"
JSON_OUTPUT_FILE = "tv_channels.json"
M3U_OUTPUT_FILE = "playlist.m3u"


def fetch_json_data(url):
    """লিংক থেকে JSON ডেটা সংগ্রহ করে"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # JSON ফাইল স্থানীয়ভাবে সেভ করা
        data = response.json()
        with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"✓ JSON ডেটা সফলভাবে ডাউনলোড ও সেভ হয়েছে: {JSON_OUTPUT_FILE}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"❌ ডেটা সংগ্রহ করতে ব্যর্থ হয়েছে: {e}")
        return None


def convert_json_to_m3u(json_data):
    """JSON ডেটাকে M3U প্লেলিস্ট ফরম্যাটে রূপান্তর করে"""
    if not json_data:
        print("M3U তৈরির জন্য কোনো JSON ডেটা পাওয়া যায়নি।")
        return

    # M3U ফাইলের হেডার
    m3u_lines = ["#EXTM3U"]

    # JSON ফরম্যাট অনুযায়ী চ্যানেল প্রসেসিং
    # (সাধারণত JSON ডেটা একটি লিস্ট হয় অথবা এর ভেতরে 'channels' অবজেক্ট থাকে)
    channels = (
        json_data if isinstance(json_data, list) else json_data.get("channels", [])
    )

    for item in channels:
        # সম্ভাব্য কি (Key) নামসমূহ চেক করা
        title = (
            item.get("name")
            or item.get("title")
            or item.get("channel_name")
            or "Unknown Channel"
        )
        stream_url = (
            item.get("url")
            or item.get("stream_url")
            or item.get("link")
            or item.get("src")
        )
        logo = item.get("logo") or item.get("tvg-logo") or ""
        group = item.get("group") or item.get("category") or "General"

        if stream_url:
            # EXTINF ট্যাগ গঠন
            extinf = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{title}'
            m3u_lines.append(extinf)
            m3u_lines.append(stream_url)

    # M3U ফাইল তৈরি/রাইট করা
    with open(M3U_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    print(f"✓ M3U প্লেলিস্ট সফলভাবে তৈরি হয়েছে: {M3U_OUTPUT_FILE}")


if __name__ == "__main__":
    print("ডেটা ডাউনলোড প্রক্রিয়া শুরু হচ্ছে...")
    data = fetch_json_data(URL)
    if data:
        convert_json_to_m3u(data)
