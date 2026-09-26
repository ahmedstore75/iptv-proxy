import os
import json
import requests

API_URL = "http://198.195.239.50/tv_channels.json"
OUTPUT_DIR = "Bangla-Iptv"

def get_live_bd_proxies():
    """
    বিভিন্ন ফ্রী প্রক্সি API থেকে সরাসরি লাইভ বাংলাদেশ প্রক্সি নিয়ে আসবে
    """
    proxies = []
    try:
        # PubProxy API থেকে BD HTTP Proxy নেওয়ার চেষ্টা
        res = requests.get("http://pubproxy.com/api/proxy?country=BD&type=http", timeout=5)
        if res.status_code == 200:
            pdata = res.json()
            if "data" in pdata and len(pdata["data"]) > 0:
                proxies.append(f"http://{pdata['data'][0]['ip']}:{pdata['data'][0]['port']}")
    except Exception:
        pass

    # ব্যাকআপ স্ট্যাটিক লিস্ট
    proxies.extend([
        "http://103.119.100.17:8080",
        "http://103.150.190.2:8080",
        "http://103.134.88.2:8080",
        "http://103.204.244.130:8080"
    ])
    return proxies

def fetch_data_with_free_proxy(url, headers):
    # ১. সরাসরি চেষ্টা
    try:
        print("⚡ Trying direct connection without proxy...")
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            print("✅ Directly fetched successfully!")
            return res.json()
    except Exception:
        print("⚠️ Direct connection failed. Fetching live BD Proxies...\n")

    # ২. প্রক্সি দিয়ে চেষ্টা
    bd_proxies = get_live_bd_proxies()
    for proxy in bd_proxies:
        proxies = {"http": proxy, "https": proxy}
        try:
            print(f"🔄 Trying BD Proxy: {proxy}")
            res = requests.get(url, headers=headers, proxies=proxies, timeout=12)
            if res.status_code == 200:
                print(f"✅ Successfully fetched data using proxy: {proxy}")
                return res.json()
        except Exception:
            print(f"❌ Proxy {proxy} failed or timed out.")

    raise Exception("All free proxies failed to connect.")
