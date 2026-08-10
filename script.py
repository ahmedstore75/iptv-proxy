import json
import re
import requests
from bs4 import BeautifulSoup

# আপনার ওয়েবসাইট লিঙ্ক
URL = "https://iptvlive-beta.vercel.app"
JSON_OUTPUT = "tv_channels.json"
M3U_OUTPUT = "playlist.m3u"


def fetch_and_extract():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    print(f"📡 Requesting Website: {URL}")

    try:
        response = requests.get(URL, headers=headers, timeout=25)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"⚠️ Error loading website: {e}")
        return

    channels = []

    # ১. প্রথমে সরাসরি HTML / JS Script ট্যাগের ভেতরের JSON ডাটা খুঁজবে
    try:
        # Next.js/React সাইটগুলোতে __NEXT_DATA__ বা JSON এম্বেড করা থাকে
        soup = BeautifulSoup(html_content, "html.parser")
        next_data = soup.find("script", id="__NEXT_DATA__")

        if next_data:
            json_payload = json.loads(next_data.string)
            # JSON অবজেক্টের ভেতর চ্যানেল লিস্ট সার্চ করা
            page_props = json_payload.get("props", {}).get("pageProps", {})
            channels = (
                page_props.get("channels")
                or page_props.get("data")
                or page_props.get("items")
                or []
            )

        # ২. যদি __NEXT_DATA__ না পাওয়া যায়, তবে Regex দিয়ে লিঙ্ক ও নাম স্ক্র্যাপ করবে
        if not channels:
            print("🔍 Extracting channels directly from HTML/JS Regex...")
            # HTTP/HTTPS প্লেলিস্ট (.m3u8 বা স্ট্রিম) লিঙ্ক খোঁজা
            stream_links = re.findall(
                r'https?://[^\s\'"]+\.(?:m3u8|mpd|ts|flv|mp4)', html_content
            )

            # যদি লিঙ্ক পাওয়া যায়
            for index, link in enumerate(set(stream_links), start=1):
                channels.append(
                    {
                        "name": f"Channel {index}",
                        "url": link,
                        "logo": "",
                        "category": "Live TV",
                    }
                )
    except Exception as e:
        print(f"⚠️ Error parsing site data: {e}")

    # যদি ডাটা খালি থাকে
    if not channels:
        print("⚠️ No streaming data or channels could be extracted.")
        return

    # ১. JSON ফাইল সেভ
    try:
        with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=4)
        print(f"✓ Saved {JSON_OUTPUT}")
    except Exception as e:
        print(f"❌ Error writing JSON: {e}")

    # ২. M3U প্লেলিস্ট তৈরি
    m3u_lines = ["#EXTM3U"]
    count = 0

    for item in channels:
        if not isinstance(item, dict):
            continue

        title = item.get("name") or item.get("title") or "Unknown Channel"
        stream_url = item.get("url") or item.get("link") or item.get("src")
        logo = item.get("logo") or item.get("icon") or ""
        group = item.get("category") or item.get("group") or "Live TV"

        if stream_url and str(stream_url).startswith("http"):
            extinf = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{title}'
            m3u_lines.append(extinf)
            m3u_lines.append(str(stream_url).strip())
            count += 1

    # ৩. M3U ফাইল সেভ
    try:
        with open(M3U_OUTPUT, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))
        print(f"✓ M3U created successfully with {count} channels!")
    except Exception as e:
        print(f"❌ Error writing M3U: {e}")


if __name__ == "__main__":
    fetch_and_extract()
