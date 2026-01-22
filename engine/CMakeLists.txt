add_library(threeup3down_engine STATIC
  engine.cpp
)

target_include_directories(threeup3down_engine
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/..
)

target_compile_features(threeup3down_engine PUBLIC cxx_std_17)

