export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // ১. প্রক্সি টার্গেট URL চেক করা (যেমন: ?url=https://example.com/live.m3u8)
    const targetUrl = url.searchParams.get("url");

    // হোম পেজ বা হেল্প মেসেজ
    if (!targetUrl) {
      return new Response(
        "IPTV Proxy is Running!\n\nUsage: https://" + url.hostname + "/?url=YOUR_STREAM_OR_M3U_URL",
        {
          headers: { "content-type": "text/plain; charset=utf-8" }
        }
      );
    }

    try {
      // ২. অরিজিনাল IPTV স্ট্রিম/প্লেলিস্ট ফ্রেচ করা
      const response = await fetch(targetUrl, {
        headers: {
          "User-Agent": request.headers.get("User-Agent") || "Mozilla/5.0",
        },
      });

      // ৩. রেসপন্স হেডারে CORS পারমিশন যোগ করা
      const newHeaders = new Headers(response.headers);
      newHeaders.set("Access-Control-Allow-Origin", "*");
      newHeaders.set("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");

      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: newHeaders,
      });

    } catch (err) {
      return new Response("Error fetching the stream: " + err.message, { status: 500 });
    }
  },
};
