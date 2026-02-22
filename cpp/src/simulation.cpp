#include "poker_sim/simulation.hpp"
#include "poker_sim/hand_eval.hpp"
#include <algorithm>
#include <random>
#include <vector>

namespace poker_sim {

SimResult run_monte_carlo(const std::vector<uint8_t>& hole_cards,
                          const std::vector<uint8_t>& board,
                          int num_opponents,
                          std::uint32_t num_trials,
                          unsigned seed) {
  SimResult result;
  result.total = static_cast<int>(num_trials);

  std::mt19937 rng(seed != 0 ? seed : 12345u);

  for (std::uint32_t t = 0; t < num_trials; ++t) {
    std::vector<uint8_t> used(hole_cards.begin(), hole_cards.end());
    used.insert(used.end(), board.begin(), board.end());
    std::vector<uint8_t> deck;
    for (int c = 0; c < 52; ++c) {
      if (std::find(used.begin(), used.end(), static_cast<uint8_t>(c)) == used.end())
        deck.push_back(static_cast<uint8_t>(c));
    }
    std::shuffle(deck.begin(), deck.end(), rng);

    std::vector<uint8_t> board_final(board.begin(), board.end());
    size_t idx = 0;
    while (board_final.size() < 5)
      board_final.push_back(deck[idx++]);

    std::vector<std::vector<uint8_t>> opp_hands;
    for (int o = 0; o < num_opponents; ++o) {
      opp_hands.push_back({deck[idx], deck[idx + 1]});
      idx += 2;
    }

    std::vector<uint8_t> hero_hand(hole_cards.begin(), hole_cards.end());
    hero_hand.insert(hero_hand.end(), board_final.begin(), board_final.end());

    int hero_value = 1;  // win unless we lose or tie
    for (const auto& opp : opp_hands) {
      std::vector<uint8_t> opp_hand = opp;
      opp_hand.insert(opp_hand.end(), board_final.begin(), board_final.end());
      int cmp = compare_hands(hero_hand, opp_hand);
      if (cmp < 0) { hero_value = -1; break; }  // loss
      if (cmp == 0) hero_value = 0;  // at least one tie
    }

    if (hero_value > 0) ++result.wins;
    else if (hero_value < 0) ++result.losses;
    else ++result.ties;
  }
  return result;
}

}  // namespace poker_sim
