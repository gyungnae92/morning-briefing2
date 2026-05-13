export const dynamic = 'force-dynamic';

import { createClient } from '@supabase/supabase-js';

export async function GET() {
  try {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL || '',
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
    );

    const { data, error } = await supabase
      .from('briefings')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(1)
      .single();

    if (error) throw error;
    if (!data) return Response.json({ error: '브리핑 없음' }, { status: 404 });

    const briefing = typeof data.data === 'string' ? JSON.parse(data.data) : data.data;
    briefing._meta = {
      date: data.date,
      time_slot: data.time_slot,
      created_at: data.created_at,
    };

    return Response.json(briefing);
  } catch (err) {
    return Response.json({ error: err.message || '조회 실패' }, { status: 500 });
  }
}
