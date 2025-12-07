cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(fmt CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_compile_features(example PRIVATE cxx_std_14)
target_link_libraries(example PRIVATE fmt::fmt)

add_executable(test_ranges src/test_ranges.cpp)
target_compile_features(test_ranges PRIVATE cxx_std_14)
target_link_libraries(test_ranges PRIVATE fmt::fmt)
