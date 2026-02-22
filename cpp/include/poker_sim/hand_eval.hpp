#ifndef POKER_SIM_HAND_EVAL_HPP
#define POKER_SIM_HAND_EVAL_HPP

#include <array>
#include <cstdint>
#include <vector>

namespace poker_sim {

constexpr int HIGH_CARD = 0, ONE_PAIR = 1, TWO_PAIR = 2, THREE_KIND = 3,
              STRAIGHT = 4, FLUSH = 5, FULL_HOUSE = 6, FOUR_KIND = 7, STRAIGHT_FLUSH = 8;

inline int card_rank(uint8_t c) { return c % 13; }
inline int card_suit(uint8_t c) { return c / 13; }

/// Compare two 7-card hands. Returns 1 if h1 wins, -1 if h2 wins, 0 if tie.
int compare_hands(const std::vector<uint8_t>& h1, const std::vector<uint8_t>& h2);

}  // namespace poker_sim

#endif
