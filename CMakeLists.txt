cmake_minimum_required(VERSION 3.20)

project(threeup3down VERSION 0.1.0 LANGUAGES CXX)

# Always generate compile_commands.json for clangd (symlink/ copy into root if desired).
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_subdirectory(engine)

add_executable(threeup3down_smoke tests/smoke.cpp)
target_link_libraries(threeup3down_smoke PRIVATE threeup3down_engine)

