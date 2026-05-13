"""Supabase DB 연결"""

import os
import json
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def save_briefing(briefing_data):
    """브리핑 결과를 Supabase에 저장"""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")

    if not url or not key:
        # DB 없으면 로컬 파일로 저장 (테스트용)
        filename = f"briefing_{datetime.now(KST).strftime('%Y%m%d_%H%M')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(briefing_data, f, ensure_ascii=False, indent=2)
        print(f"   💾 로컬 저장: {filename}")
        return

    from supabase import create_client
    supabase = create_client(url, key)

    now = datetime.now(KST)
    supabase.table("briefings").insert({
        "date": now.strftime("%Y-%m-%d"),
        "time_slot": "morning" if now.hour < 12 else "afternoon",
        "data": json.dumps(briefing_data, ensure_ascii=False),
        "created_at": now.isoformat(),
    }).execute()

    print(f"   💾 Supabase 저장 완료")
