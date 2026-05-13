"""CBS 박성태의 뉴스쇼 녹취록 크롤러"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

LIST_URL = "https://www.cbs.co.kr/board/list/cbs_P000246_interview"
BASE_URL = "https://www.cbs.co.kr"


def fetch_cbs_transcripts():
    """오늘자 CBS 인터뷰 전문 크롤링"""
    results = []
    today_str = datetime.now().strftime("%-m/%-d")  # e.g. "5/13"
    today_str_win = datetime.now().strftime("%#m/%#d")  # Windows

    try:
        resp = requests.get(LIST_URL, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # 게시판 링크 찾기
        links = soup.select("a[href*='/board/view/cbs_P000246_interview']")

        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href", "")

            # 오늘 날짜 필터
            if today_str not in title and today_str_win not in title:
                continue

            # 개별 페이지 fetch
            full_url = href if href.startswith("http") else BASE_URL + href
            try:
                detail = requests.get(full_url, timeout=15)
                detail.encoding = "utf-8"
                detail_soup = BeautifulSoup(detail.text, "html.parser")

                # 본문 텍스트 추출
                content_div = detail_soup.select_one(".board-view-content, .view-content, .board_view_content")
                if content_div:
                    text = content_div.get_text("\n", strip=True)
                else:
                    # fallback: 전체 텍스트에서 구분선 이후 추출
                    full_text = detail_soup.get_text("\n", strip=True)
                    marker = "==========="
                    if marker in full_text:
                        text = full_text.split(marker, 1)[1]
                    else:
                        text = full_text

                # ◇◆ 발언자 표시가 있으면 인터뷰 녹취 확실
                if len(text) > 100:
                    results.append({
                        "title": title,
                        "text": text.strip(),
                        "url": full_url,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                    })
            except Exception as e:
                print(f"   ⚠️ CBS 개별 페이지 실패: {e}")

    except Exception as e:
        print(f"   ⚠️ CBS 목록 페이지 실패: {e}")

    return results
