export const dynamic = 'force-dynamic';
export const revalidate = 0;

import { createClient } from '@supabase/supabase-js';

export async function GET() {
  const headers = {
    'Cache-Control': 'no-store, no-cache, must-revalidate',
    'Pragma': 'no-cache',
  };

  try {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL || '',
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
    );

    const { data, error } = await supabase
      .from('briefings')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(1);

    if (error) {
      return Response.json({ error: error.message }, { status: 500, headers });
    }

    if (!data || data.length === 0) {
      return Response.json({ error: 'No briefing found' }, { status: 404, headers });
    }

    const row = data[0];
    const briefing = typeof row.data === 'string' ? JSON.parse(row.data) : row.data;
    briefing._meta = {
      date: row.date,
      time_slot: row.time_slot,
      created_at: row.created_at,
    };

    return Response.json(briefing, { headers });
  } catch (err) {
    return Response.json({ error: err.message }, { status: 500, headers });
  }
}
