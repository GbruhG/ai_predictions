import { createClient } from '@supabase/supabase-js';

// Replace with your Supabase URL and API key
const supabaseUrl = 'https://nyflkmktapyxlfehsfvq.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55ZmxrbWt0YXB5eGxmZWhzZnZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjQyNDk1NDAsImV4cCI6MjAzOTgyNTU0MH0.7zPmk_3Eg_0Z2QB358mCNBLhAOnSLgub5XtxebSP5WM';
const supabase = createClient(supabaseUrl, supabaseKey);

// Function to fetch predictions
export const fetchPredictions = async () => {
  const { data, error } = await supabase
    .from('prediction')
    .select('*')
    .order('league_name', { ascending: true })
    .order('fixture_id', { ascending: true });

  if (error) {
    console.error('Error fetching predictions:', error.message, error.details);
    return [];
  }
  return data;
};

// Function to fetch head-to-head data
export const getH2H = async (fixtureId) => {
  const { data, error } = await supabase
    .from('h2h')
    .select('*')
    .eq('fixture_id', fixtureId)
    .order('h2h_date', { ascending: false })
    .limit(5);

  if (error) {
    console.error('Error fetching H2H data:', error);
    return [];
  }
  return data;
};