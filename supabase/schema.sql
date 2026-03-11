-- Poker Simulation schema for Supabase PostgreSQL
-- Run in Supabase SQL Editor (Dashboard > SQL Editor)

-- Profiles: synced from auth.users for display names in friends/games
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  username TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Trigger: create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, username)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    username = COALESCE(EXCLUDED.username, profiles.username);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT OR UPDATE ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Friends
CREATE TABLE IF NOT EXISTS public.friends (
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  friend_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, friend_id),
  CHECK (user_id != friend_id)
);

CREATE INDEX IF NOT EXISTS idx_friends_user ON public.friends(user_id);

CREATE TABLE IF NOT EXISTS public.friend_requests (
  from_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  to_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (from_id, to_id),
  CHECK (from_id != to_id)
);

CREATE INDEX IF NOT EXISTS idx_friend_requests_to ON public.friend_requests(to_id);

-- Games
CREATE TABLE IF NOT EXISTS public.games (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  host_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  join_code TEXT UNIQUE NOT NULL,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'ended')),
  display_name TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_games_code ON public.games(join_code);
CREATE INDEX IF NOT EXISTS idx_games_host ON public.games(host_id);

CREATE TABLE IF NOT EXISTS public.game_players (
  game_id UUID NOT NULL REFERENCES public.games(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,  -- UUID or 'manual-xxx' for manual players
  user_name TEXT NOT NULL,
  initial_buy_in REAL DEFAULT 0,
  total_buy_in REAL DEFAULT 0,
  cash_out REAL,
  left_at TIMESTAMPTZ,
  PRIMARY KEY (game_id, user_id)
);

CREATE TABLE IF NOT EXISTS public.game_invites (
  game_id UUID NOT NULL REFERENCES public.games(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  PRIMARY KEY (game_id, user_id)
);

-- Winnings
CREATE TABLE IF NOT EXISTS public.winnings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  session_date DATE NOT NULL,
  buy_in REAL NOT NULL DEFAULT 0,
  cash_out REAL NOT NULL DEFAULT 0,
  profit REAL NOT NULL,
  hours REAL DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_winnings_user ON public.winnings(user_id);
CREATE INDEX IF NOT EXISTS idx_winnings_date ON public.winnings(session_date);

-- RLS: Allow service role full access; anon/authenticated use RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.friends ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.friend_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.games ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.game_players ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.game_invites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.winnings ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS. For API using service_role key, no extra policies needed.
-- Optional: add policies for direct client access if using anon key.
