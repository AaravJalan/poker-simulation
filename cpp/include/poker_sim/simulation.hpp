#ifndef POKER_SIM_SIMULATION_HPP
#define POKER_SIM_SIMULATION_HPP

#include <cstdint>
#include <vector>

namespace poker_sim {

struct SimResult {
  int wins = 0;
  int ties = 0;
  int losses = 0;
  int total = 0;
};

/// Full Monte Carlo: hole_cards (2), board (0,3,4,5), num_opponents (1-8), num_trials.
/// Returns wins, ties, losses, total.
SimResult run_monte_carlo(const std::vector<uint8_t>& hole_cards,
                          const std::vector<uint8_t>& board,
                          int num_opponents,
                          std::uint32_t num_trials,
                          unsigned seed = 0);

}  // namespace poker_sim

#endif
