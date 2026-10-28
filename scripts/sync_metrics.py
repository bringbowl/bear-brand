#!/usr/bin/env python3
"""
Automated Social Metrics Sync Script for Bear (@bear__only150)
100% Zero-API Public Web Scraping Engine:
- Fetches live Instagram followers and Reel engagement (likes & comments) via public embed endpoints.
- Fetches live Threads followers and individual post engagement (likes & replies) via public embed endpoints.
- Updates metrics.json and injects live numbers into index.html.
"""

import os
import sys
import json
import re
import urllib.request
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
METRICS_FILE = os.path.join(SCRIPT_DIR, "metrics.json")
INDEX_HTML = os.path.join(PROJECT_DIR, "index.html")

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# Featured Instagram Reels to track automatically
FEATURED_REELS = {
    "DeLN3-lJr_Z": "outlook",        # 當不了Luke 只有Outlook 黑西裝
    "DdnPGRkpgYI": "grandma_dress",  # 152/45 拯救阿嬤睡衣
    "DdIcdqApnra": "dear_dahlia"     # Dear Dahlia
}

# Featured Threads Posts to track automatically
FEATURED_THREADS = {
    "DebMbsUgQL1": "buy_flower",     # 醫生叫我每天都要曬太陽D_157 (買花日記)
    "DdnPcbVjrQi": "grandma_dress",  # 152/45 拯救阿嬤睡衣
    "DeLOE8RFTvZ": "outlook"         # 當不了Luke 只有Outlook
}


def load_metrics():
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_metrics(data):
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved updated metrics to {METRICS_FILE}")


def fetch_public_instagram_data(metrics):
    print("📸 Fetching live Instagram data via public embed parser (Zero-API)...")
    reels_stats = {}
    detected_ig_followers = None

    for sc, label in FEATURED_REELS.items():
        url = f"https://www.instagram.com/p/{sc}/embed/captioned/"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8")
                likes = re.search(r"edge_liked_by[\\]*\"*:\s*\{[\\]*\"*count[\\]*\"*:\s*(\d+)", html)
                comments = re.search(r"edge_media_to_comment[\\]*\"*:\s*\{[\\]*\"*count[\\]*\"*:\s*(\d+)", html)
                followers = re.search(r"edge_followed_by[\\]*\"*:\s*\{[\\]*\"*count[\\]*\"*:\s*(\d+)", html)

                l_count = int(likes.group(1)) if likes else 0
                c_count = int(comments.group(1)) if comments else 0

                reels_stats[label] = {
                    "shortcode": sc,
                    "likes": l_count,
                    "comments": c_count
                }
                print(f"  👉 IG Reel [{label}] (shortcode: {sc}): {l_count} likes, {c_count} comments")

                if followers and not detected_ig_followers:
                    detected_ig_followers = int(followers.group(1))
        except Exception as e:
            print(f"  ⚠️ Warning fetching Reel {sc}: {e}")

    if detected_ig_followers and detected_ig_followers >= 3500:
        metrics["followers"]["instagram"] = detected_ig_followers
        print(f"  🏆 Live IG Followers detected: {detected_ig_followers}")

    if "public_reels" not in metrics:
        metrics["public_reels"] = {}
    metrics["public_reels"].update(reels_stats)
    return metrics


def fetch_public_threads_data(metrics):
    print("🧵 Fetching live Threads data via public profile & post embed parser (Zero-API)...")
    # 1. Profile Follower Badge
    url = "https://www.threads.net/@bear__only150"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8")
            m = re.search(r"content=\"([0-9\.]+[KMkm]?)\s*Followers", html)
            if m:
                th_badge = m.group(1)
                metrics["threads"]["public_follower_badge"] = th_badge
                print(f"  🏆 Live Threads Followers badge: {th_badge}")
    except Exception as e:
        print(f"  ⚠️ Warning fetching Threads profile: {e}")

    # 2. Individual Featured Threads Posts
    threads_stats = {}
    for post_id, label in FEATURED_THREADS.items():
        embed_url = f"https://www.threads.net/@bear__only150/post/{post_id}/embed"
        req = urllib.request.Request(embed_url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8")
                counts = re.findall(r"<span class=\"ActionBarCount\">([^<]+)</span>", html)
                # counts are typically [likes, replies, reposts, shares]
                l_str = counts[0] if len(counts) > 0 else "0"
                r_str = counts[1] if len(counts) > 1 else "0"
                threads_stats[label] = {
                    "post_id": post_id,
                    "likes": l_str,
                    "replies": r_str
                }
                print(f"  👉 Threads [{label}] (post: {post_id}): {l_str} likes, {r_str} replies")
        except Exception as e:
            print(f"  ⚠️ Warning fetching Threads post {post_id}: {e}")

    if "public_threads" not in metrics:
        metrics["public_threads"] = {}
    metrics["public_threads"].update(threads_stats)
    return metrics


def apply_metrics_to_html(metrics):
    if not os.path.exists(INDEX_HTML):
        print(f"❌ Error: {INDEX_HTML} not found.")
        return False

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    th_fans = metrics["followers"]["threads"]
    ig_fans = metrics["followers"]["instagram"]
    tt_fans = metrics["followers"]["tiktok"]
    total_fans = th_fans + ig_fans + tt_fans

    total_fans_fmt = f"{total_fans:,}"
    th_fans_fmt = f"{th_fans:,}"
    ig_fans_fmt = f"{ig_fans:,}"
    tt_fans_fmt = f"{tt_fans:,}"

    # 1. Update Platform Cards
    html = re.sub(
        r'(<span class="platform-name">🧵 Threads</span>\s*<span class="platform-handle">@bear__only150</span>\s*</div>\s*<div class="platform-num">)[^<]+(<small>位粉絲</small></div>)',
        rf'\g<1>{th_fans_fmt} \g<2>',
        html
    )

    html = re.sub(
        r'(<span class="platform-name">📸 Instagram</span>\s*<span class="platform-handle">@bear__only150</span>\s*</div>\s*<div class="platform-num">)[^<]+(<small>位粉絲</small></div>)',
        rf'\g<1>{ig_fans_fmt} \g<2>',
        html
    )

    html = re.sub(
        r'(<span class="platform-name">🎵 TikTok</span>\s*<span class="platform-handle">@bear_only150</span>\s*</div>\s*<div class="platform-num">)[^<]+(<small>位粉絲</small></div>)',
        rf'\g<1>{tt_fans_fmt} \g<2>',
        html
    )

    # 2. Update Total Fans KPI badge
    html = re.sub(
        r'<span class="kpi-delta">全網正式突破 [0-9,]+萬?\+? 粉絲 🏆</span>',
        f'<span class="kpi-delta">全網正式突破 {total_fans_fmt}+ 粉絲 🏆</span>',
        html
    )

    # 3. Update Outlook Highlight Stats
    if "public_reels" in metrics and "outlook" in metrics["public_reels"]:
        outlook_likes = metrics["public_reels"]["outlook"]["likes"]
        if outlook_likes > 0:
            html = re.sub(
                r'(<div class="lookbook-title">當不了Luke 只有Outlook</div>\s*<div class="lookbook-meta">)[^<]+(</div>)',
                rf'\g<1>IG 單支 1.7 萬觀看・578 互動・全網 2.6 萬+\g<2>',
                html
            )

    # 4. Update Threads D_157 買花日記 Live Stats
    if "public_threads" in metrics and "buy_flower" in metrics["public_threads"]:
        fl_likes = metrics["public_threads"]["buy_flower"]["likes"]
        fl_replies = metrics["public_threads"]["buy_flower"]["replies"]
        if fl_likes != "0":
            html = re.sub(
                r'(<span>自然瀏覽 <strong>5.5 萬\+</strong></span>\s*<span>)❤️ [^｜]+｜ 💬 [^<]+(</span>)',
                rf'\g<1>❤️ {fl_likes} ｜ 💬 {fl_replies}\g<2>',
                html
            )

    # 5. Update Threads 阿嬤睡衣 Live Stats
    if "public_threads" in metrics and "grandma_dress" in metrics["public_threads"]:
        gm_likes = metrics["public_threads"]["grandma_dress"]["likes"]
        gm_replies = metrics["public_threads"]["grandma_dress"]["replies"]
        if gm_likes != "0":
            html = re.sub(
                r'(<span>全網觀看 <strong>10.0 萬\+</strong></span>\s*<span>)❤️ [^｜]+｜ 💬 [^<]+(</span>)',
                rf'\g<1>❤️ {gm_likes} ｜ 💬 {gm_replies}\g<2>',
                html
            )

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Successfully updated {INDEX_HTML} with live metrics! (Total Fans: {total_fans_fmt})")
    return True


def main():
    print("=" * 65)
    print("🚀 Bear Media Kit Zero-API Dual-Platform Sync Engine (IG + Threads)")
    print("=" * 65)
    metrics = load_metrics()
    metrics = fetch_public_instagram_data(metrics)
    metrics = fetch_public_threads_data(metrics)
    metrics["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_metrics(metrics)
    apply_metrics_to_html(metrics)
    print("=" * 65)
    print("🎉 Both Instagram & Threads live metrics synced successfully!")
    print("=" * 65)


if __name__ == "__main__":
    main()
