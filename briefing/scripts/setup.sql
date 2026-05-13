-- Supabase SQL Editor에서 실행하세요
-- (supabase.com → 프로젝트 → SQL Editor → New Query)

CREATE TABLE briefings (
  id BIGSERIAL PRIMARY KEY,
  date DATE NOT NULL,
  time_slot TEXT NOT NULL DEFAULT 'morning',  -- 'morning' or 'afternoon'
  data JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 날짜+시간대 인덱스 (최신 브리핑 빠르게 조회)
CREATE INDEX idx_briefings_date ON briefings (date DESC, time_slot);

-- Row Level Security (공개 읽기 허용)
ALTER TABLE briefings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "공개 읽기" ON briefings
  FOR SELECT USING (true);

CREATE POLICY "서버만 쓰기" ON briefings
  FOR INSERT WITH CHECK (true);
