"""
Route database calls to Supabase or SQLite based on env.
When SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set, use Supabase.
Otherwise use SQLite (friends_db, games_db, winnings_db).
"""
import os

_use_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

if _use_supabase:
    from poker_sim.supabase_backend import (
        add_friend,
        send_friend_request,
        accept_friend_request,
        decline_friend_request,
        get_pending_requests,
        get_sent_requests,
        remove_friend,
        get_friends,
        list_all_users,
        search_users,
        create_game,
        get_game_by_code,
        get_game,
        join_game,
        add_buy_in,
        leave_game,
        invite_friends,
        invite_by_email,
        add_player_manually,
        invite_friends_to_game,
        get_pending_game_invites,
        accept_game_invite,
        end_game,
        rename_game,
        delete_game,
        list_user_games,
        add_entry as winnings_add_entry,
        get_entries as winnings_get_entries,
        delete_entry as winnings_delete_entry,
    )
else:
    from poker_sim.friends_db import (
        add_friend,
        send_friend_request,
        accept_friend_request,
        decline_friend_request,
        get_pending_requests,
        get_sent_requests,
        remove_friend,
        get_friends,
        list_all_users,
        search_users,
    )
    from poker_sim.games_db import (
        create_game,
        get_game_by_code,
        get_game,
        join_game,
        add_buy_in,
        leave_game,
        invite_friends,
        invite_by_email,
        add_player_manually,
        invite_friends_to_game,
        get_pending_game_invites,
        accept_game_invite,
        end_game,
        rename_game,
        delete_game,
        list_user_games,
    )
    from poker_sim.winnings_db import (
        add_entry as winnings_add_entry,
        get_entries as winnings_get_entries,
        delete_entry as winnings_delete_entry,
    )
