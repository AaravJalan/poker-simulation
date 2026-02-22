#include "poker_sim/hand_eval.hpp"
#include <algorithm>
#include <array>
#include <unordered_map>
#include <utility>
#include <vector>

namespace poker_sim {

namespace {

struct HandKey {
  int type;
  std::array<int, 5> tb;
  bool operator>(const HandKey& o) const {
    if (type != o.type) return type > o.type;
    for (int i = 0; i < 5; ++i)
      if (tb[i] != o.tb[i]) return tb[i] > o.tb[i];
    return false;
  }
};

bool has_straight(const std::vector<int>& ranks) {
  return false;  // used via straight_high
}

int straight_high(std::vector<int> ranks) {
  std::sort(ranks.begin(), ranks.end());
  ranks.erase(std::unique(ranks.begin(), ranks.end()), ranks.end());
  if (ranks.size() < 5) return -1;
  for (int high = 12; high >= 3; --high) {
    bool ok = true;
    for (int k = 0; k < 5 && ok; ++k)
      ok = (std::find(ranks.begin(), ranks.end(), (high - k + 13) % 13) != ranks.end());
    if (ok) return high;
  }
  // wheel A-2-3-4-5
  bool wheel = (std::find(ranks.begin(), ranks.end(), 12) != ranks.end() &&
                std::find(ranks.begin(), ranks.end(), 0) != ranks.end() &&
                std::find(ranks.begin(), ranks.end(), 1) != ranks.end() &&
                std::find(ranks.begin(), ranks.end(), 2) != ranks.end() &&
                std::find(ranks.begin(), ranks.end(), 3) != ranks.end());
  return wheel ? 3 : -1;
}

HandKey eval5(const uint8_t* cards) {
  std::vector<int> ranks, suits;
  for (int i = 0; i < 5; ++i) {
    ranks.push_back(card_rank(cards[i]));
    suits.push_back(card_suit(cards[i]));
  }
  std::sort(ranks.begin(), ranks.end(), std::greater<int>());

  std::unordered_map<int, int> count;
  for (int r : ranks) count[r]++;
  std::vector<std::pair<int, int>> count_grp;
  for (const auto& p : count) count_grp.push_back({p.second, p.first});
  std::sort(count_grp.begin(), count_grp.end(), [](const auto& a, const auto& b) {
    if (a.first != b.first) return a.first > b.first;
    return a.second > b.second;
  });

  bool is_flush = (suits[0] == suits[1] && suits[1] == suits[2] && suits[2] == suits[3] && suits[3] == suits[4]);
  int str_high = straight_high(ranks);

  HandKey k{};
  k.tb = {0, 0, 0, 0, 0};

  if (is_flush && str_high >= 0) {
    k.type = STRAIGHT_FLUSH;
    k.tb[0] = str_high;
    return k;
  }
  if (count_grp[0].first == 4) {
    k.type = FOUR_KIND;
    k.tb[0] = count_grp[0].second;
    k.tb[1] = count_grp.size() > 1 ? count_grp[1].second : 0;
    return k;
  }
  if (count_grp[0].first == 3 && count_grp.size() > 1 && count_grp[1].first >= 2) {
    k.type = FULL_HOUSE;
    k.tb[0] = count_grp[0].second;
    k.tb[1] = count_grp[1].second;
    return k;
  }
  if (is_flush) {
    k.type = FLUSH;
    for (int i = 0; i < 5 && i < (int)ranks.size(); ++i) k.tb[i] = ranks[i];
    return k;
  }
  if (str_high >= 0) {
    k.type = STRAIGHT;
    k.tb[0] = str_high;
    return k;
  }
  if (count_grp[0].first == 3) {
    k.type = THREE_KIND;
    for (size_t i = 0; i < count_grp.size(); ++i) k.tb[i] = count_grp[i].second;
    return k;
  }
  if (count_grp[0].first == 2 && count_grp.size() > 1 && count_grp[1].first == 2) {
    k.type = TWO_PAIR;
    for (size_t i = 0; i < count_grp.size(); ++i) k.tb[i] = count_grp[i].second;
    return k;
  }
  if (count_grp[0].first == 2) {
    k.type = ONE_PAIR;
    for (size_t i = 0; i < count_grp.size(); ++i) k.tb[i] = count_grp[i].second;
    return k;
  }
  k.type = HIGH_CARD;
  for (int i = 0; i < 5; ++i) k.tb[i] = ranks[i];
  return k;
}

void comb5(const std::vector<uint8_t>& cards, int idx, int depth, uint8_t* out, HandKey& best) {
  if (depth == 5) {
    HandKey k = eval5(out);
    if (k > best) best = k;
    return;
  }
  for (size_t i = idx; i < cards.size(); ++i) {
    out[depth] = cards[i];
    comb5(cards, static_cast<int>(i) + 1, depth + 1, out, best);
  }
}

HandKey evaluate7(const std::vector<uint8_t>& cards) {
  uint8_t buf[5];
  HandKey best{};
  best.type = -1;
  comb5(cards, 0, 0, buf, best);
  return best;
}

}  // namespace

int compare_hands(const std::vector<uint8_t>& h1, const std::vector<uint8_t>& h2) {
  HandKey k1 = evaluate7(h1);
  HandKey k2 = evaluate7(h2);
  if (k1 > k2) return 1;
  if (k2 > k1) return -1;
  return 0;
}

}  // namespace poker_sim
