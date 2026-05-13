"""유튜브 자막 추출 크롤러"""

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import requests
from youtube_transcript_api import YouTubeTranscriptApi

CHANNELS = {
    "MBC 김종배의 시선집중": {
        "handle": "mbcradio_sisa",
        "keywords": ["시선집중", "김종배", "JB TIMES"],
        "scan_limit": 30,  # MBC는 영상이 많아서 더 스캔
    },
    "SBS 김태현의 정치쇼": {
        "handle": "sbsradio_sisa",
        "keywords": ["정치쇼", "김태현"],
        "scan_limit": 15,
    },
    "KBS 전격시사": {
        "handle": "KBS_1Radio",
        "keywords": ["전격시사"],
        "scan_limit": 15,
    },
    "김어준 뉴스공장": {
        "handle": "gyeomsonisnothing",
        "keywords": ["뉴스공장", "겸손"],
        "scan_limit": 10,
    },
}

HOURS_BACK = 28  # 최근 28시간 (여유)


def get_channel_id(handle):
    """채널 핸들 → 채널 ID"""
    try:
        resp = requests.get(f"https://www.youtube.com/@{handle}", timeout=15)
        match = re.search(r'"channelId":"(UC[^"]+)"', resp.text)
        if match:
            return match.group(1)
        match = re.search(r'"externalId":"(UC[^"]+)"', resp.text)
        if match:
            return match.group(1)
    except:
        pass
    return None


def get_recent_videos(channel_id, keywords, hours_back=HOURS_BACK):
    """RSS 피드에서 키워드 매칭 최근 영상"""
    try:
        resp = requests.get(
            f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
            timeout=10,
        )
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
        entries = root.findall("atom:entry", ns)

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        videos = []

        for entry in entries:
            title = entry.find("atom:title", ns).text or ""
            video_id = entry.find("yt:videoId", ns).text or ""
            published = entry.find("atom:published", ns).text or ""

            try:
                pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            except:
                continue

            if any(kw in title for kw in keywords) and pub_dt > cutoff:
                videos.append({"id": video_id, "title": title, "published": published})

        return videos
    except:
        return []


def extract_transcript(video_id):
    """영상에서 한국어 자막 추출 (신구 API 호환)"""
    # 신 API (v1.0+)
    try:
        api = YouTubeTranscriptApi()
        try:
            transcript = api.fetch(video_id, languages=["ko"])
            texts = []
            for item in transcript:
                t = item.text if hasattr(item, "text") else item.get("text", "")
                if t:
                    texts.append(t)
            if texts:
                return " ".join(texts)
        except:
            pass
        try:
            transcript = api.fetch(video_id)
            texts = []
            for item in transcript:
                t = item.text if hasattr(item, "text") else item.get("text", "")
                if t:
                    texts.append(t)
            if texts:
                return " ".join(texts)
        except:
            pass
    except TypeError:
        pass

    # 구 API (v0.x)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ko"])
        return " ".join(item.get("text", "") for item in transcript)
    except:
        pass
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(item.get("text", "") for item in transcript)
    except:
        pass

    return ""


def fetch_youtube_transcripts():
    """전체 채널 자막 추출"""
    results = {}

    for name, info in CHANNELS.items():
        channel_id = get_channel_id(info["handle"])
        if not channel_id:
            print(f"   ⚠️ {name}: 채널 ID 못 찾음")
            results[name] = []
            continue

        videos = get_recent_videos(channel_id, info["keywords"])
        if not videos:
            print(f"   ⚠️ {name}: 최근 영상 없음")
            results[name] = []
            continue

        channel_results = []
        for v in videos:
            text = extract_transcript(v["id"])
            if text and len(text) > 50:
                channel_results.append({
                    "title": v["title"],
                    "text": text,
                    "video_id": v["id"],
                    "published": v["published"],
                })

        results[name] = channel_results

    return results
