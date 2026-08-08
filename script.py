import json
import requests

URL = "http://198.195.239.50/tv_channels.json"
JSON_OUTPUT = "tv_channels.json"
M3U_OUTPUT = "playlist.m3u"


def fetch_and_convert():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    print(f"Fetching data from {URL}...")
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error fetching JSON: {e}")
        # যদি URL কাজ না করে তবে খালি ফাইল না বানিয়ে স্ক্রিপ্ট থামাবে
        return

    # JSON ফাইল হিসেবে সেভ
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✓ Saved {JSON_OUTPUT}")

    # ডাইনামিক ফিল্টারিং দিয়ে M3U তৈরি
    channels = []
    if isinstance(data, list):
        channels = data
    elif isinstance(data, dict):
        # যদি ডিকশনারির ভেতরে 'channels', 'data', 'items' বা সরাসরি অবজেক্ট থাকে
        channels = (
            data.get("channels")
            or data.get("data")
            or data.get("items")
            or list(data.values())
        )

    m3u_lines = ["#EXTM3U"]
    count = 0

    for item in channels:
        if not isinstance(item, dict):
            continue

        # নাম খোঁজা
        title = (
            item.get("name")
            or item.get("title")
            or item.get("channel_name")
            or item.get("channel")
            or "Unknown Channel"
        )

        # লিঙ্ক/ইউআরএল খোঁজা
        stream_url = (
            item.get("url")
            or item.get("link")
            or item.get("stream_url")
            or item.get("src")
            or item.get("file")
        )

        logo = (
            item.get("logo")
            or item.get("tvg-logo")
            or item.get("icon")
            or item.get("image")
            or ""
        )
        group = item.get("group") or item.get("category") or "Live TV"

        if stream_url and str(stream_url).startswith("http"):
            extinf = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{title}'
            m3u_lines.append(extinf)
            m3u_lines.append(str(stream_url))
            count += 1

    with open(M3U_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    print(f"✓ M3U created successfully with {count} channels!")


if __name__ == "__main__":
    fetch_and_convert()
