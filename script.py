import json
import re
import requests

URL = "https://iptvlive-beta.vercel.app"
JSON_OUTPUT = "tv_channels.json"
M3U_OUTPUT = "playlist.m3u"


def clean_channel_name(url):
    """
    URL থেকে সঠিক চ্যানেলের নাম এক্সট্র্যাক্ট ও ফরম্যাট করার ফাংশন
    উদাহরণ: http://.../ban-boisakhi-tv-hd/index.m3u8 -> Boisakhi Tv Hd
    """
    try:
        # URL এর শেষ অংশের ফোল্ডার নাম নেওয়া
        parts = url.rstrip("/").split("/")
        slug = parts[-2] if "index.m3u8" in parts[-1] else parts[-1]

        # দেশের কোড/ল্যাঙ্গুয়েজ প্রিফিক্স সরানো (যেমন: ban-, hindi-, de-, in-)
        slug = re.sub(
            r"^(ban|hindi|de|in|pk|yp|sp|tamil|kannada|assam|sp)-",
            "",
            slug,
            flags=re.IGNORECASE,
        )

        # হাইফেনগুলোকে স্পেস বানানো এবং প্রতি শব্দের ১ম অক্ষর বড় হাতের করা
        clean_name = slug.replace("-", " ").title()

        return clean_name
    except Exception:
        return "Live TV Channel"


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
        html_content = ""

    channels = []

    if html_content:
        # ১. Next.js / React ডাটা অবজেক্ট খোঁজা
        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html_content,
            re.DOTALL,
        )

        if next_data_match:
            try:
                json_payload = json.loads(next_data_match.group(1))
                page_props = json_payload.get("props", {}).get("pageProps", {})

                raw_channels = (
                    page_props.get("channels")
                    or page_props.get("data")
                    or page_props.get("items")
                    or []
                )

                for item in raw_channels:
                    if isinstance(item, dict):
                        url = (
                            item.get("url")
                            or item.get("link")
                            or item.get("src")
                        )
                        name = (
                            item.get("name")
                            or item.get("title")
                            or (clean_channel_name(url) if url else None)
                        )
                        logo = (
                            item.get("logo")
                            or item.get("icon")
                            or item.get("tvg-logo")
                            or ""
                        )
                        category = (
                            item.get("category")
                            or item.get("group")
                            or "Live TV"
                        )

                        if url:
                            channels.append(
                                {
                                    "name": name,
                                    "url": url,
                                    "logo": logo,
                                    "category": category,
                                }
                            )
            except Exception as e:
                print(f"⚠️ JSON Parse Error: {e}")

        # ২. ব্যাকআপ: যদি HTML থেকে সরাসরি লিঙ্ক বের করতে হয়
        if not channels:
            print(
                "🔍 Next.js payload not found. Extracting and parsing URLs directly..."
            )
            stream_links = re.findall(
                r'https?://[^\s\'"]+\.(?:m3u8|mpd|ts|flv|mp4)', html_content
            )

            # ডুপ্লিকেট বাদ দেওয়া
            unique_links = list(set(stream_links))

            for link in unique_links:
                channel_name = clean_channel_name(link)
                channels.append(
                    {
                        "name": channel_name,
                        "url": link,
                        "logo": "",
                        "category": "Live TV",
                    }
                )

    # ১. JSON ফাইল সেভ করা
    try:
        with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=4)
        print(f"✓ Saved {JSON_OUTPUT}")
    except Exception as e:
        print(f"❌ Error writing JSON: {e}")

    # ২. M3U ফাইল তৈরি করা
    m3u_lines = ["#EXTM3U"]
    count = 0

    for item in channels:
        title = item.get("name") or "Unknown Channel"
        stream_url = item.get("url")
        logo = item.get("logo") or ""
        group = item.get("category") or "Live TV"

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
        print(f"❌ Error writing M3U: {e}")


if __name__ == "__main__":
    fetch_and_extract()
