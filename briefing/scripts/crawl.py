"""
아침 브리핑 크롤러 — 메인 오케스트레이터
매일 8시, 13시에 GitHub Actions에서 실행됨
"""

import os
import json
import sys
from datetime import datetime, timezone, timedelta

from cbs_crawler import fetch_cbs_transcripts
from youtube_crawler import fetch_youtube_transcripts
from summarizer import generate_briefing
from db import save_briefing

KST = timezone(timedelta(hours=9))


def main():
    now = datetime.now(KST)
    print(f"{'='*50}")
    print(f"☀️ 아침 브리핑 크롤러 시작: {now.strftime('%Y-%m-%d %H:%M KST')}")
    print(f"{'='*50}\n")

    # ① CBS 녹취록 크롤링
    print("📻 [1/3] CBS 뉴스쇼 녹취록 수집...")
    cbs_data = fetch_cbs_transcripts()
    print(f"   → {len(cbs_data)}건 수집\n")

    # ② 유튜브 자막 추출 (MBC, SBS, KBS, 뉴스공장)
    print("📺 [2/3] 유튜브 자막 추출...")
    yt_data = fetch_youtube_transcripts()
    for name, items in yt_data.items():
        total_chars = sum(len(it.get("text", "")) for it in items)
        print(f"   → {name}: {len(items)}건 ({total_chars:,}자)")
    print()

    # 전체 원문 합치기
    all_sources = []
    for item in cbs_data:
        all_sources.append({
            "source": "CBS 박성태의 뉴스쇼",
            "source_type": "radio",
            "title": item["title"],
            "text": item["text"],
            "url": item.get("url", ""),
        })
    for name, items in yt_data.items():
        for item in items:
            all_sources.append({
                "source": name,
                "source_type": "radio",
                "title": item["title"],
                "text": item["text"],
                "video_id": item.get("video_id", ""),
            })

    total_chars = sum(len(s["text"]) for s in all_sources)
    print(f"📊 총 원문: {len(all_sources)}건, {total_chars:,}자\n")

    if total_chars == 0:
        print("⚠️ 수집된 원문이 없습니다. 종료.")
        return

    # ③ AI 요약 (2단계: Haiku로 추출 → Sonnet으로 최종 브리핑)
    print("🤖 [3/3] AI 브리핑 생성...")
    briefing = generate_briefing(all_sources)

    if not briefing:
        print("❌ 브리핑 생성 실패")
        return

    section_count = sum(len(s.get("items", [])) for s in briefing.get("sections", []))
    print(f"   → {len(briefing.get('sections', []))}개 카테고리, {section_count}개 이슈\n")

    # ④ DB 저장
    print("💾 Supabase 저장...")
    briefing["crawled_at"] = now.isoformat()
    briefing["raw_source_count"] = len(all_sources)
    briefing["raw_total_chars"] = total_chars

    # 원문도 함께 저장 (팩트체크용, 텍스트는 앞 2000자만)
    briefing["raw_sources"] = [
        {
            "source": s["source"],
            "title": s["title"],
            "text": s["text"][:2000],
            "url": s.get("url", ""),
            "video_id": s.get("video_id", ""),
        }
        for s in all_sources
    ]

    save_briefing(briefing)
    print("✅ 완료!\n")


if __name__ == "__main__":
    # scripts/ 디렉토리를 모듈 경로에 추가
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
