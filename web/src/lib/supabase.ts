import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL || ''
const key = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

const looksLikePlaceholder =
  url.includes('your-project.supabase.co') || key === 'your-anon-key'
const looksLikeSupabaseUrl = /^https:\/\/.+\.supabase\.co\/?$/.test(url)

export const supabase =
  url && key && looksLikeSupabaseUrl && !looksLikePlaceholder
    ? createClient(url, key)
    : null
export const supabaseConfigured =
  !!(url && key && looksLikeSupabaseUrl && !looksLikePlaceholder)
