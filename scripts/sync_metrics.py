#!/usr/bin/env python3
"""
Automated Social Metrics Sync Script for Bear (@bear__only150)
Synchronizes live data from Meta Graph API / Threads API into metrics.json and index.html.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
METRICS_FILE = os.path.join(SCRIPT_DIR, "metrics.json")
INDEX_HTML = os.path.join(PROJECT_DIR, "index.html")


def load_metrics():
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_metrics(data):
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved metrics to {METRICS_FILE}")


def fetch_from_meta_api(metrics):
    """
    Optional live fetch if META_ACCESS_TOKEN and IG_USER_ID are configured in environment.
    """
    token = os.environ.get("META_ACCESS_TOKEN")
    ig_id = os.environ.get("IG_USER_ID")

    if not token or not ig_id:
        print("ℹ️ META_ACCESS_TOKEN or IG_USER_ID not set. Skipping live API fetch, using existing metrics.json.")
        return metrics

    print("🌐 Connecting to Meta Graph API...")
    try:
        # 1. Fetch Basic Profile & Followers
        url = f"https://graph.facebook.com/v21.0/{ig_id}?fields=followers_count,media_count&access_token={token}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "followers_count" in data:
                metrics["followers"]["instagram"] = data["followers_count"]
                print(f"  👉 Fetched live IG followers: {data['followers_count']}")

        # 2. Fetch 28-day Insights (Reach, Impressions)
        insights_url = f"https://graph.facebook.com/v21.0/{ig_id}/insights?metric=reach,impressions&period=days_28&access_token={token}"
        req = urllib.request.Request(insights_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            idata = json.loads(resp.read().decode("utf-8"))
            for item in idata.get("data", []):
                name = item.get("name")
                values = item.get("values", [{}])
                val = values[0].get("value", 0) if values else 0
                if name == "reach" and val > 0:
                    metrics["instagram"]["reach_30d"] = val
                    print(f"  👉 Fetched live IG 28-day Reach: {val}")
                elif name == "impressions" and val > 0:
                    metrics["instagram"]["views_30d"] = val
                    print(f"  👉 Fetched live IG 28-day Impressions: {val}")

        # 3. Fetch Follower Demographics (Gender & Age)
        demo_url = f"https://graph.facebook.com/v21.0/{ig_id}/insights?metric=follower_demographics&period=lifetime&metric_type=total_value&breakdown=age,gender&access_token={token}"
        req = urllib.request.Request(demo_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            ddata = json.loads(resp.read().decode("utf-8"))
            # Process breakdowns if available
            # (Meta API returns breakdowns in total_value)

        metrics["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        print("✅ Meta Graph API sync completed successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch from Meta API: {e}")

    return metrics


def apply_metrics_to_html(metrics):
    if not os.path.exists(INDEX_HTML):
        print(f"❌ Error: {INDEX_HTML} not found.")
        return False

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # Calculate computed aggregates
    th_fans = metrics["followers"]["threads"]
    ig_fans = metrics["followers"]["instagram"]
    tt_fans = metrics["followers"]["tiktok"]
    total_fans = th_fans + ig_fans + tt_fans

    # Format numbers
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

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Successfully updated {INDEX_HTML} (Total Fans: {total_fans_fmt})")
    return True


def main():
    print("🚀 Starting Bear Media Kit Automated Metrics Sync...")
    metrics = load_metrics()
    metrics = fetch_from_meta_api(metrics)
    save_metrics(metrics)
    apply_metrics_to_html(metrics)
    print("🎉 All done!")


if __name__ == "__main__":
    main()
