import json
import re
import requests

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

    print(f"📡 Fetching data from: {URL}")

    try:
        response = requests.get(URL, headers=headers, timeout=25)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"⚠️ Could not load URL: {e}")
        # ফেল না করে খালি ফাইল বা ফাঁকা রেজাল্ট রিটার্ন করবে
        html_content = ""

    channels = []

    if html_content:
        # Regex ব্যবহার করে Next.js/React থেকে JSON খুঁজে বের করা
        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html_content,
            re.DOTALL,
        )

        if next_data_match:
            try:
                json_payload = json.loads(next_data_match.group(1))
                page_props = json_payload.get("props", {}).get("pageProps", {})
                channels = (
                    page_props.get("channels")
                    or page_props.get("data")
                    or page_props.get("items")
                    or []
                )
            except Exception as e:
                print(f"⚠️ Error parsing JSON script: {e}")

        # যদি JSON না পাওয়া যায় তবে M3U8 বা প্লেলিস্ট লিংক খোঁজা
        if not channels:
            print("🔍 Searching for stream links directly...")
            stream_links = re.findall(
                r'https?://[^\s\'"]+\.(?:m3u8|mpd|ts|flv|mp4)', html_content
            )

            for index, link in enumerate(set(stream_links), start=1):
                channels.append(
                    {
                        "name": f"Channel {index}",
                        "url": link,
                        "logo": "",
                        "category": "Live TV",
                    }
                )

    # ১. JSON ফাইল সেভ করা (ডাটা না থাকলেও খালি লিস্ট দিয়ে সেভ করবে)
    try:
        with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=4)
        print(f"✓ Saved {JSON_OUTPUT}")
    except Exception as e:
        print(f"❌ Could not write JSON: {e}")

    # ২. M3U প্লেলিস্ট তৈরি করা
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

    # ৩. M3U ফাইল সেভ করা
    try:
        with open(M3U_OUTPUT, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))
        print(f"✓ M3U created successfully with {count} channels!")
    except Exception as e:
        print(f"❌ Could not write M3U: {e}")


if __name__ == "__main__":
    fetch_and_extract()
