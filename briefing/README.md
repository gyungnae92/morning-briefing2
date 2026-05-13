# ☀️ 아침 브리핑

5개 시사 라디오 프로그램 + 뉴스 기사 → AI 자동 큐레이션 브리핑

## 소스
- CBS 박성태의 뉴스쇼 (녹취록 직접 크롤링)
- MBC 김종배의 시선집중 (유튜브 자막)
- SBS 김태현의 정치쇼 (유튜브 자막)
- KBS 전격시사 (유튜브 자막)
- 김어준 뉴스공장 (유튜브 자막)

## 아키텍처
```
GitHub Actions (매일 8시, 13시)
  → CBS 크롤링 + 유튜브 자막 추출
  → Haiku로 이슈 추출 → Sonnet으로 브리핑 생성
  → Supabase에 저장

Vercel (웹앱)
  → Supabase에서 최신 브리핑 읽기
  → 접속 즉시 표시 (0.1초)
```

## 셋업 가이드

### 1단계: Supabase 설정 (5분)
1. supabase.com 가입 (무료)
2. New Project 생성
3. SQL Editor → scripts/setup.sql 내용 복붙 → Run
4. Settings → API에서 복사:
   - Project URL (https://xxx.supabase.co)
   - anon/public 키

### 2단계: GitHub 저장소 (5분)
1. github.com에서 New Repository → `morning-briefing`
2. 이 폴더의 파일 전부 push
3. Settings → Secrets and Variables → Actions에 추가:
   - `ANTHROPIC_API_KEY`: sk-ant-...
   - `SUPABASE_URL`: https://xxx.supabase.co
   - `SUPABASE_KEY`: anon 키

### 3단계: Vercel 배포 (3분)
1. vercel.com → Add New Project → GitHub 저장소 선택
2. Environment Variables에 추가:
   - `NEXT_PUBLIC_SUPABASE_URL`: https://xxx.supabase.co
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: anon 키
3. Deploy

### 4단계: 첫 크롤링 테스트
- GitHub → Actions 탭 → "Morning Briefing Crawler" → Run workflow
- 또는 로컬에서: `cd scripts && pip install -r requirements.txt && python crawl.py`

## 월 비용
| 항목 | 비용 |
|---|---|
| Vercel | 무료 |
| Supabase | 무료 |
| GitHub Actions | 무료 |
| Claude API | 월 3~4만원 |

## 로컬 개발
```bash
npm install
cp .env.example .env.local  # 키 입력
npm run dev
```
