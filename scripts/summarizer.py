"""AI 브리핑 생성기 — 2단계 요약"""

import os
import json
import anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# 1단계: Haiku가 각 소스에서 핵심 이슈 추출
EXTRACT_PROMPT = """아래는 한국 아침 시사 라디오/뉴스 원문입니다.
이 텍스트에서 다뤄진 주요 이슈를 추출하세요.

규칙:
- 각 이슈마다 헤드라인, 2~3줄 요약, 관련 발언 핵심 인용(1줄)을 포함
- 평택 관련(평택항, 고덕, 미군기지, GTX 등) 이슈는 반드시 포함
- 최대한 많이 추출 (중요도 낮은 것도 포함)

JSON만 출력. 백틱 없이. 큰따옴표 안에 큰따옴표 쓰지 말고 작은따옴표로:
{"issues":[{"headline":"헤드라인","summary":"요약","quote":"핵심인용1줄","category":"정치/경제/노동/여성/사회/국제/지역현안(평택)","importance":"high/medium/low"}]}"""

# 2단계: Sonnet이 전체 이슈를 종합해서 최종 브리핑 생성
SYNTHESIZE_PROMPT = """당신은 한국 아침 시사 브리핑 편집장입니다.
아래는 5개 라디오 프로그램에서 추출한 이슈 목록입니다.
이것을 종합해서 최종 브리핑을 만드세요.

규칙:
- 같은 주제는 하나로 통합하되, 어떤 프로그램에서 다뤘는지 sources에 모두 기재
- 카테고리: 정치, 경제, 노동, 여성, 사회, 국제, 지역현안(평택) 등
- 이슈 30~50개 (적으면 안 됨! 사소한 것도 포함)
- 각 이슈에 importance (high/medium/low) 배정
- 뉴스 기사 검색도 필요하면 포함

JSON만 출력. 백틱 없이. 큰따옴표 안에 큰따옴표 쓰지 말고 작은따옴표로:

{"date":"날짜","data_quality":"수집현황 1줄","one_liner":"오늘 핵심 한줄","sections":[{"category":"카테고리","icon":"이모지","items":[{"id":"item_0","headline":"헤드라인","summary":"3~5줄요약","sources":["프로그램명"],"source_type":"radio/news/both","source_detail":"코너/출연자","importance":"high/medium/low","has_transcript":true,"transcript_hint":"원문검색쿼리"}]}],"source_coverage":{"cbs":"요약","mbc":"요약","sbs":"요약","kbs":"요약","newsFactory":"요약"}}"""


def repair_json(text):
    """AI 응답에서 JSON 추출 및 복구"""
    s = text.replace("```json", "").replace("```", "").strip()
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1:
        return None
    s = s[start:end + 1]

    for attempt in range(4):
        try:
            return json.loads(s)
        except:
            if attempt == 0:
                s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
            elif attempt == 1:
                import re
                s = re.sub(r",\s*}", "}", s)
                s = re.sub(r",\s*]", "]", s)
            elif attempt == 2:
                s = re.sub(r'\s{2,}', ' ', s)
    return None


def call_claude(model, system, user_content, max_tokens=4000):
    """Claude API 호출"""
    client = anthropic.Anthropic(api_key=API_KEY)
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )
    text = "".join(b.text for b in message.content if b.type == "text")
    return text


def generate_briefing(all_sources):
    """2단계 브리핑 생성"""

    if not API_KEY:
        print("   ❌ ANTHROPIC_API_KEY 환경변수 없음")
        return None

    # === 1단계: Haiku로 각 소스에서 이슈 추출 ===
    print("   [1/2] Haiku로 이슈 추출 중...")
    all_issues = []

    # 소스를 청크로 나누기 (Haiku 입력 제한 ~180K 토큰)
    # 대략 4000자 = 1K 토큰 기준, 청크당 60K자
    CHUNK_SIZE = 60000
    chunks = []
    current_chunk = ""
    current_sources = []

    for src in all_sources:
        entry = f"\n\n[{src['source']}] {src['title']}\n{src['text'][:15000]}"
        if len(current_chunk) + len(entry) > CHUNK_SIZE:
            if current_chunk:
                chunks.append({"text": current_chunk, "sources": current_sources})
            current_chunk = entry
            current_sources = [src["source"]]
        else:
            current_chunk += entry
            current_sources.append(src["source"])

    if current_chunk:
        chunks.append({"text": current_chunk, "sources": current_sources})

    print(f"   → {len(chunks)}개 청크로 분할")

    for i, chunk in enumerate(chunks):
        print(f"   → 청크 {i+1}/{len(chunks)} 처리 중 ({len(chunk['text']):,}자)...")
        try:
            result_text = call_claude(
                model="claude-haiku-4-5-20251001",
                system=EXTRACT_PROMPT,
                user_content=chunk["text"],
                max_tokens=4000,
            )
            parsed = repair_json(result_text)
            if parsed and "issues" in parsed:
                for issue in parsed["issues"]:
                    issue["_chunk_sources"] = chunk["sources"]
                all_issues.extend(parsed["issues"])
                print(f"     → {len(parsed['issues'])}개 이슈 추출")
            else:
                print(f"     ⚠️ JSON 파싱 실패")
        except Exception as e:
            print(f"     ⚠️ Haiku 호출 실패: {e}")

    print(f"   → 총 {len(all_issues)}개 이슈 추출 완료\n")

    if not all_issues:
        return None

    # === 2단계: Sonnet으로 최종 브리핑 생성 ===
    print("   [2/2] Sonnet으로 최종 브리핑 생성 중...")

    # 이슈 목록을 텍스트로 변환 (Sonnet 입력용)
    issues_text = json.dumps(all_issues, ensure_ascii=False, indent=None)

    # 너무 길면 앞쪽만 (Sonnet 입력 제한)
    if len(issues_text) > 100000:
        issues_text = issues_text[:100000] + "...]}"

    try:
        from datetime import datetime, timezone, timedelta
        KST = timezone(timedelta(hours=9))
        today = datetime.now(KST).strftime("%Y년 %m월 %d일")

        result_text = call_claude(
            model="claude-sonnet-4-6",
            system=SYNTHESIZE_PROMPT,
            user_content=f"오늘 날짜: {today}\n\n추출된 이슈 목록:\n{issues_text}",
            max_tokens=8000,
        )
        briefing = repair_json(result_text)
        if briefing:
            print(f"   → 브리핑 생성 완료!")
            return briefing
        else:
            print(f"   ⚠️ 최종 JSON 파싱 실패, 재시도...")
            # 재시도: 깨진 JSON 수정 요청
            fix_text = call_claude(
                model="claude-sonnet-4-6",
                system="깨진 JSON을 유효한 JSON으로 고쳐주세요. 백틱 없이.",
                user_content=result_text[:5000],
                max_tokens=8000,
            )
            return repair_json(fix_text)
    except Exception as e:
        print(f"   ❌ Sonnet 호출 실패: {e}")
        return None
