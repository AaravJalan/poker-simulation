cmake_minimum_required(VERSION 3.15)
project(poker_simulation LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

# pybind11 via FetchContent (no system install required)
include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.11.1
)
set(PYBIND11_FINDPYTHON ON)
FetchContent_MakeAvailable(pybind11)

# C++ simulation library (static)
add_subdirectory(cpp)

# Python extension module (links against simulation lib)
pybind11_add_module(poker_sim_cpp
  cpp/src/bindings.cpp
)
target_link_libraries(poker_sim_cpp PRIVATE poker_sim)
target_include_directories(poker_sim_cpp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/cpp/include)

# Install extension into python/poker_sim for development (run from build: cmake --install . --prefix ..)
install(TARGETS poker_sim_cpp LIBRARY DESTINATION python/poker_sim RUNTIME DESTINATION python/poker_sim)
