import os
import requests

API_URL = "https://iptvlive-beta.vercel.app"
OUTPUT_DIR = "Bangla"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_playlists():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    
    try:
        print("Fetching playlist data from API...")
        response = requests.get(API_URL, headers=headers, timeout=20)
        
        print(f"API Response Status Code: {response.status_code}")
        response.raise_for_status()

        m3u_text = response.text.strip()

        if not m3u_text:
            raise ValueError("API returned empty response!")

        # M3U ফাইল সেভ করা
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.write(m3u_text)
            
        print("✅ M3U playlist saved successfully to Bangla/playlist.m3u")

    except Exception as e:
        print(f"❌ Error generating playlist: {e}")

if __name__ == "__main__":
    generate_playlists()
