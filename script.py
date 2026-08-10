import json
import sys
import requests

# আপনার API EndPoint
URL = "https://iptvlive-beta.vercel.app"
JSON_OUTPUT = "tv_channels.json"
M3U_OUTPUT = "playlist.m3u"


def fetch_and_convert():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    print(f"📡 Requesting API: {URL}")

    try:
        response = requests.get(URL, headers=headers, timeout=30)
        response.raise_for_status()

        # HTML রিটার্ন করছে নাকি আসল JSON চেক করা
        try:
            data = response.json()
        except ValueError:
            print(
                "❌ Error: API did not return JSON. Make sure the URL points to a JSON Endpoint, not an HTML page."
            )
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error fetching API data: {e}")
        sys.exit(1)

    if not data:
        print("❌ Received empty data from API!")
        sys.exit(1)

    # ১. JSON ফাইল সেভ করা
    try:
        with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✓ Saved {JSON_OUTPUT}")
    except Exception as e:
        print(f"❌ Could not write JSON file: {e}")
        sys.exit(1)

    # ২. চ্যানেল লিস্ট এক্সট্র্যাক্ট করা
    channels = []
    if isinstance(data, list):
        channels = data
    elif isinstance(data, dict):
        channels = (
            data.get("channels")
            or data.get("data")
            or data.get("items")
            or data.get("result")
            or list(data.values())
        )

    if not isinstance(channels, list):
        print("❌ Could not parse channels array from response.")
        sys.exit(1)

    # ৩. M3U প্লেলিস্ট তৈরি করা
    m3u_lines = ["#EXTM3U"]
    count = 0

    for item in channels:
        if not isinstance(item, dict):
            continue

        # চ্যানেল টাইটেল খোঁজা
        title = (
            item.get("name")
            or item.get("title")
            or item.get("channel_name")
            or item.get("channel")
            or "Unknown Channel"
        )

        # স্ট্রিম ইউআরএল খোঁজা
        stream_url = (
            item.get("url")
            or item.get("link")
            or item.get("stream_url")
            or item.get("src")
            or item.get("file")
        )

        # লোগো এবং ক্যাটাগরি
        logo = (
            item.get("logo")
            or item.get("tvg-logo")
            or item.get("icon")
            or item.get("image")
            or ""
        )
        group = item.get("group") or item.get("category") or "Live TV"

        # বৈধ স্ট্রিম ইউআরএল ফিল্টারিং
        if stream_url and str(stream_url).strip().startswith("http"):
            extinf = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{title}'
            m3u_lines.append(extinf)
            m3u_lines.append(str(stream_url).strip())
            count += 1

    # ৪. M3U ফাইল সেভ করা
    try:
        with open(M3U_OUTPUT, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))
        print(f"✓ M3U playlist created successfully with {count} channels!")
    except Exception as e:
        print(f"❌ Could not write M3U file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    fetch_and_convert()
