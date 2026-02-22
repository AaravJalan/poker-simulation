#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <poker_sim/simulation.hpp>

namespace py = pybind11;

PYBIND11_MODULE(poker_sim_cpp, m) {
  m.doc() = "Texas Hold'em Monte Carlo simulation engine (C++ extension)";

  py::class_<poker_sim::SimResult>(m, "SimResult")
    .def_readonly("wins", &poker_sim::SimResult::wins)
    .def_readonly("ties", &poker_sim::SimResult::ties)
    .def_readonly("losses", &poker_sim::SimResult::losses)
    .def_readonly("total", &poker_sim::SimResult::total)
    .def("win_rate", [](const poker_sim::SimResult& r) {
      return r.total > 0 ? static_cast<double>(r.wins) / r.total : 0.0;
    })
    .def("tie_rate", [](const poker_sim::SimResult& r) {
      return r.total > 0 ? static_cast<double>(r.ties) / r.total : 0.0;
    })
    .def("loss_rate", [](const poker_sim::SimResult& r) {
      return r.total > 0 ? static_cast<double>(r.losses) / r.total : 0.0;
    });

  m.def("run_monte_carlo",
        [](const std::vector<int>& hole_cards, const std::vector<int>& board,
           int num_opponents, std::uint32_t num_trials, py::object seed_obj) {
          std::vector<uint8_t> hc, b;
          for (int c : hole_cards) hc.push_back(static_cast<uint8_t>(c));
          for (int c : board) b.push_back(static_cast<uint8_t>(c));
          unsigned seed = 0;
          if (!seed_obj.is_none()) seed = static_cast<unsigned>(py::cast<int>(seed_obj));
          return poker_sim::run_monte_carlo(hc, b, num_opponents, num_trials, seed);
        },
        py::arg("hole_cards"),
        py::arg("board"),
        py::arg("num_opponents") = 1,
        py::arg("num_trials") = 10000,
        py::arg("seed") = py::none(),
        "Run Monte Carlo simulation.");
}
