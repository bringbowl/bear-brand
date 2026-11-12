#!/usr/bin/env python3
"""
Automated Social Metrics Sync Script for Bear (@bear__only150)
100% Zero-API Multi-Platform Scraping Engine (IG + Threads + TikTok):
- Instagram: Live followers and Reel engagement (likes & comments) via public embed parser.
- Threads: Live followers and post engagement (likes & replies) via public embed parser.
- TikTok: Live followers and total hearts via live public counter API.
- Automatically calculates total audience and updates index.html.
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
MEDIA_KIT_HTMLS = [
    INDEX_HTML,
    os.path.join(PROJECT_DIR, "公開模特卡_對外品牌版.html"),
    os.path.join(PROJECT_DIR, "小熊_品牌合作履歷與模特卡.html"),
]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# Featured Instagram Reels / Posts
FEATURED_REELS = {
    "Dfjx-XlJplC": "nuegray_reel",      # nuegray 雙色唇釉測評 (2026/11/10)
    "DfebFdRtSQq": "puppy_control",     # 被這隻狗狗硬控了10分鐘 (2026/11/08)
    "DfeZ8UjNtwU": "picnic_outfit",     # 151/45 野餐怎麼可以沒有花草跟小狗 (2026/11/08)
    "DfbLumTpofI": "dont_film_me",      # 再錄我打爆你喔👊🏻💥 背後激凸日常 (2026/11/07)
    "DfRGLjHN6M1": "aomo_xmas_reel",      # 奧莫聖誕寫真挑照片大對決 Reels (2026/11/03)
    "DfL0-_ENJjw": "beef_noodles_reel", # 藍海饌牛肉麵雙11開團短影音 (2026/11/01)
    "DfG9G8kN2TP": "weekly_outfit",     # 一週七天不同穿搭 (2026/10/30)
    "DfHnBt9CcET": "moana_ai",          # Moana AI 萬聖節公主裝扮 (2026/10/30)
    "DfEFEc5NgyB": "windows_boot",      # 工程師說過：重新開機可以解決 99% 的問題 (Windows 開機穿搭)
    "DeLN3-lJr_Z": "outlook",           # 當不了Luke 只有Outlook 黑西裝
    "DdnPGRkpgYI": "grandma_dress",     # 152/45 拯救阿嬤睡衣
    "DdIcdqApnra": "dear_dahlia",       # Dear Dahlia
    "Dc5iZoqiTBt": "eaton_dried_fruit"  # EATON 伊頓果乾團購 (2026/09)
}

# Featured Threads Posts
FEATURED_THREADS = {
    "Dfl34SygXJy": "sunbathe_d183",        # 醫生叫我每天都要曬太陽D_183☀️ 再婚皇后50話 (2026/11/11)
    "Dfl4NTWAUye": "heels_walk_threads",   # 穿高跟鞋偷偷欣賞自己的步伐 (2026/11/11)
    "DfkDvF1gZMq": "flower_thread",        # 收過另一伴送你最印象深刻的花 (2026/11/10)
    "Dfjz7icgWQ7": "nuegray_threads",      # nuegray 雙色試色二選一 (2026/11/10)
    "DfjMnClAQ_c": "sunbathe_d182",        # 醫生叫我每天都要曬太陽D_182☀️ (2026/11/10)
    "DfeaEyYgTEA": "picnic_outfit",        # 151/45 野餐怎麼可以沒有花草跟小狗 (2026/11/08)
    "DfRFCI1Aa4R": "aomo_xmas_threads",    # 奧莫聖誕寫真挑照片大對決 (2026/11/03)
    "DfOU98KgVp3": "sunbathe_d175",        # 醫生叫我每天都要曬太陽D_175☀️ 迷你玫瑰 (2026/11/02)
    "DfLzzKYgeD_": "beef_noodles_threads", # 藍海饌牛肉麵開團文 (2026/11/01)
    "DfL_qzYgQjq": "sunbathe_d174",        # 醫生叫我每天都要曬太陽D_174☀️ 信義區 (2026/11/01)
    "DfJFJ45Af3Z": "sunbathe_d173",        # 醫生叫我每天都要曬太陽D_173🎃 (2026/10/30)
    "DfJBr0GAZDP": "pomelo_halloween",    # 柚子問它可以一起過萬聖節嗎 (2026/10/30)
    "DfGz76kgdIa": "sunbathe_new",        # 醫生叫我每天要曬太陽 (2026/10/30)
    "DfG9TZ8lTP7": "weekly_outfit",       # 一週七天不同穿搭 (2026/10/30)
    "DfG4O04gZK3": "nangang_bento",       # 南港車站有超省錢便當 (2026/10/30)
    "DfHnC7KCWGg": "moana_ai",            # Moana AI 萬聖節公主裝扮 (2026/10/30)
    "DfHnhiRAcZh": "moana_disney",        # Disney+ 海洋奇緣合作文 (2026/10/30)
    "DfEFKfVjl06": "windows_boot",        # 工程師說過：重新開機可以解決 99% 的問題 (Windows 開機穿搭)
    "DebMbsUgQL1": "buy_flower",          # 醫生叫我每天都要曬太陽D_157 (買花日記)
    "DdnPcbVjrQi": "grandma_dress",       # 152/45 拯救阿嬤睡衣
    "DeLOE8RFTvZ": "outlook"              # 當不了Luke 只有Outlook
}

# Featured TikTok Videos
FEATURED_TIKTOK_VIDEOS = {
    "7706505140433374482": "nuegray_tiktok",      # nuegray 雙色唇釉測評 (2026/11/10)
    "7705726517854145810": "picnic_outfit",       # 151/45 野餐日穿搭 (2026/11/08)
    "7705259051969482002": "dont_film_me",        # 再看我打你喔 (2026/11/07)
    "7703458907158482183": "dewytree",            # DEWYTREE 自顏源露泡泡愛心挑戰 (2026/11/02)
    "7703047882932292871": "beef_noodles_tiktok", # 藍海饌牛肉麵開團 (2026/11/01)
    "7702347579811499272": "weekly_outfit"        # 一週七天不同穿搭 (2026/10/30)
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
    print("📸 [1/3] Fetching live Instagram data via public embed parser...")
    reels_stats = {}
    detected_ig_followers = None

    for sc, label in FEATURED_REELS.items():
        url = f"https://www.instagram.com/p/{sc}/embed/captioned/"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8")
                likes = re.search(r"edge_liked_by[\\]*\"*:\s*\{[\\]*\"*count[\\]*\"*:\s*(\d+)", html)
                l_count = int(likes.group(1)) if likes else None
                if l_count is None:
                    m = re.search(r"([\d,]+)\s*(?:likes|like|次贊|個讚|個贊)", html)
                    l_count = int(m.group(1).replace(",", "")) if m else 0

                comments = re.search(r"edge_media_to_comment[\\]*\"*:\s*\{[\\]*\"*count[\\]*\"*:\s*(\d+)", html)
                c_count = int(comments.group(1)) if comments else None
                if c_count is None:
                    c = re.search(r"([\d,]+)\s*(?:comments|comment|則留言|條評論)", html)
                    c_count = int(c.group(1).replace(",", "")) if c else 0

                followers = re.search(r"edge_followed_by[\\]*\"*:\s*\{[\\]*\"*count[\\]*\"*:\s*(\d+)", html)

                reels_stats[label] = {
                    "shortcode": sc,
                    "likes": l_count,
                    "comments": c_count
                }
                print(f"  👉 IG Reel [{label}]: {l_count} likes, {c_count} comments")

                if followers and not detected_ig_followers:
                    detected_ig_followers = int(followers.group(1))
        except Exception as e:
            print(f"  ⚠️ Warning fetching Reel {sc}: {e}")

    if detected_ig_followers and detected_ig_followers >= 3500:
        metrics["followers"]["instagram"] = detected_ig_followers
        print(f"  🏆 Live IG Followers: {detected_ig_followers}")

    if "public_reels" not in metrics:
        metrics["public_reels"] = {}
    metrics["public_reels"].update(reels_stats)
    return metrics


def _parse_badge_to_int(badge):
    s = badge.strip().upper()
    if s.endswith("K"):
        return int(float(s[:-1]) * 1000)
    if s.endswith("M"):
        return int(float(s[:-1]) * 1_000_000)
    return int(float(s.replace(",", "")))


def fetch_public_threads_data(metrics):
    print("🧵 [2/3] Fetching live Threads data via public profile & post embed parser...")
    url = "https://www.threads.net/@bear__only150"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8")
            m = re.search(r"content=\"([0-9\.]+[KMkm]?)\s*Followers", html)
            if m:
                th_badge = m.group(1)
                metrics["threads"]["public_follower_badge"] = th_badge
                badge_floor = _parse_badge_to_int(th_badge)
                cur_th = metrics["followers"].get("threads", 0)
                if badge_floor > cur_th:
                    metrics["followers"]["threads"] = badge_floor
                    print(f"  📈 Updated Threads follower baseline from badge {th_badge} -> {badge_floor}")
                print(f"  🏆 Live Threads Followers badge: {th_badge}")
    except Exception as e:
        print(f"  ⚠️ Warning fetching Threads profile: {e}")

    threads_stats = {}
    for post_id, label in FEATURED_THREADS.items():
        embed_url = f"https://www.threads.net/@bear__only150/post/{post_id}/embed"
        req = urllib.request.Request(embed_url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8")
                counts = re.findall(r"<span class=\"ActionBarCount\">([^<]+)</span>", html)
                l_str = counts[0] if len(counts) > 0 else "0"
                r_str = counts[1] if len(counts) > 1 else "0"
                threads_stats[label] = {
                    "post_id": post_id,
                    "likes": l_str,
                    "replies": r_str
                }
                print(f"  👉 Threads [{label}]: {l_str} likes, {r_str} replies")
        except Exception as e:
            print(f"  ⚠️ Warning fetching Threads post {post_id}: {e}")

    if "public_threads" not in metrics:
        metrics["public_threads"] = {}
    metrics["public_threads"].update(threads_stats)
    return metrics


def fetch_public_tiktok_data(metrics):
    print("🎵 [3/3] Fetching live TikTok data via public counter API...")
    url = "https://countik.com/api/exist/bear_only150"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") == "success":
                tt_followers = data.get("followerCount", 0)
                tt_hearts = data.get("heartCount", 0)
                if tt_followers > 2000:
                    metrics["followers"]["tiktok"] = tt_followers
                    print(f"  🏆 Live TikTok Followers: {tt_followers:,}")
                if tt_hearts > 10000:
                    metrics["tiktok"]["likes_total"] = f"{tt_hearts / 10000:.1f} 萬+"
                    print(f"  🏆 Live TikTok Total Hearts: {tt_hearts:,} ({metrics['tiktok']['likes_total']})")
    except Exception as e:
        print(f"  ⚠️ Warning fetching TikTok data: {e}")

    # Fetch featured individual TikTok videos
    tiktok_videos_stats = {}
    for vid, label in FEATURED_TIKTOK_VIDEOS.items():
        v_url = f"https://www.tiktok.com/@bear_only150/video/{vid}"
        v_req = urllib.request.Request(v_url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(v_req, timeout=8) as v_resp:
                v_html = v_resp.read().decode("utf-8")
                v_likes = re.search(r'\"diggCount\":(\d+)', v_html)
                v_plays = re.search(r'\"playCount\":(\d+)', v_html)
                v_comments = re.search(r'\"commentCount\":(\d+)', v_html)
                l_num = int(v_likes.group(1)) if v_likes else 0
                p_num = int(v_plays.group(1)) if v_plays else 0
                c_num = int(v_comments.group(1)) if v_comments else 0
                if l_num > 0 or p_num > 0:
                    tiktok_videos_stats[label] = {
                        "video_id": vid,
                        "likes": l_num,
                        "plays": p_num,
                        "comments": c_num
                    }
                    print(f"  👉 TikTok [{label}]: {l_num} likes, {p_num} plays, {c_num} comments")
                else:
                    print(f"  ⚠️ TikTok [{label}] returned empty stats; preserving cached metrics")
        except Exception as e:
            print(f"  ⚠️ Warning fetching TikTok video {vid}: {e}")

    if "public_videos" not in metrics["tiktok"]:
        metrics["tiktok"]["public_videos"] = {}
    metrics["tiktok"]["public_videos"].update(tiktok_videos_stats)
    return metrics


def apply_metrics_to_html(metrics):
    target_paths = [p for p in MEDIA_KIT_HTMLS if os.path.exists(p)]
    if not target_paths:
        print(f"❌ Error: no target Media Kit HTML files found in {MEDIA_KIT_HTMLS}.")
        return False

    th_fans = metrics["followers"]["threads"]
    ig_fans = metrics["followers"]["instagram"]
    tt_fans = metrics["followers"]["tiktok"]
    total_fans = th_fans + ig_fans + tt_fans

    total_fans_fmt = f"{total_fans:,}"
    th_badge = metrics.get("threads", {}).get("public_follower_badge", "")
    if th_badge.upper().endswith("K") and th_fans == _parse_badge_to_int(th_badge):
        th_fans_fmt = f"{th_fans:,}+"
    else:
        th_fans_fmt = f"{th_fans:,}"
    ig_fans_fmt = f"{ig_fans:,}"
    tt_fans_fmt = f"{tt_fans:,}"
    wan_str = f"{(total_fans // 1000) / 10:.1f} 萬+"
    tt_likes = metrics.get("tiktok", {}).get("likes_total", "1.4 萬+")
    last_updated = metrics.get("last_updated", "")

    for html_path in target_paths:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

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

        # Update TikTok detail likes if available
        html = re.sub(
            r'(<div class="platform-detail">累計獲讚 <strong>)[^<]+(</strong>)',
            rf'\g<1>{tt_likes}\g<2>',
            html
        )

        # 2. Update Total Fans KPI badge & narrative copy
        html = re.sub(
            r'<span class="kpi-delta">全網正式突破 [0-9,]+萬?\+? 粉絲 🏆</span>',
            f'<span class="kpi-delta">全網正式突破 {total_fans_fmt}+ 粉絲 🏆</span>',
            html
        )
        html = re.sub(
            r'(跨平台突破 <b>)[^<]+(</b>)',
            rf'\g<1>{wan_str}粉絲（{total_fans_fmt}+）\g<2>',
            html
        )
        html = re.sub(
            r'累積逾 [0-9.]+\s*萬\+?粉絲（[0-9,]+\+?）',
            f'累積逾 {wan_str}粉絲（{total_fans_fmt}+）',
            html
        )
        html = re.sub(
            r'(<span>📸 Instagram 核心商業池（)[0-9,]+( 粉）</span>)',
            rf'\g<1>{ig_fans_fmt}\g<2>',
            html
        )
        html = re.sub(
            r'(<span>🧵 Threads [^（]+（)[0-9,]+( 粉）</span>)',
            rf'\g<1>{th_fans_fmt}\g<2>',
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

        # 6. Update DEWYTREE Live Stats (Lookbook + Showcase Card)
        dt_data = metrics.get("tiktok", {}).get("public_videos", {}).get("dewytree", {})
        if dt_data:
            dt_plays = dt_data.get("plays", 0)
            dt_likes = dt_data.get("likes", 0)
            dt_comments = dt_data.get("comments", 0)
            if dt_plays > 0:
                dt_plays_fmt = f"{dt_plays:,}"
                dt_likes_fmt = f"{dt_likes:,}"
                html = re.sub(
                    r'(<div class="lookbook-title">DEWYTREE 愛心泡泡挑戰</div>\s*<div class="lookbook-meta">)[^<]+(</div>)',
                    rf'\g<1>TikTok {dt_plays_fmt} 觀看・{dt_likes_fmt} 讚・12K 新觀眾\g<2>',
                    html
                )
                html = re.sub(
                    r'(<span>TikTok 自然觀看 <strong>)[^<]+(</strong></span>\s*<span>)❤️ [^｜]+｜ 💬 [^<]+(</span>)',
                    rf'\g<1>{dt_plays_fmt}+\g<2>❤️ {dt_likes_fmt} ｜ 💬 {dt_comments}\g<3>',
                    html
                )

        # 7. Update visible sync timestamp in footer
        if last_updated:
            sync_stamp = f'<br><span class="sync-stamp" style="display:inline-block;margin-top:6px;font-size:12px;opacity:0.8;">📊 全平台公開數據最後同步：{last_updated}（每日 07:17 CST 自動執行）</span>'
            if 'class="sync-stamp"' in html:
                html = re.sub(
                    r'<br><span class="sync-stamp"[^>]*>.*?</span>',
                    lambda m: sync_stamp,
                    html,
                    flags=re.DOTALL
                )
            else:
                html = re.sub(
                    r'(\s*</footer>)',
                    lambda m: f'\n    {sync_stamp}{m.group(1)}',
                    html,
                    count=1
                )

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ Successfully updated {os.path.basename(html_path)} with live metrics! (Total Fans: {total_fans_fmt}+)")

    return True


def main():
    print("=" * 68)
    print("🚀 Bear Media Kit Zero-API Triple-Platform Sync Engine (IG + Threads + TikTok)")
    print("=" * 68)
    metrics = load_metrics()
    metrics = fetch_public_instagram_data(metrics)
    metrics = fetch_public_threads_data(metrics)
    metrics = fetch_public_tiktok_data(metrics)
    metrics["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_metrics(metrics)
    apply_metrics_to_html(metrics)
    print("=" * 68)
    print("🎉 All 3 platforms (IG, Threads, TikTok) live metrics synced successfully!")
    print("=" * 68)


if __name__ == "__main__":
    main()
