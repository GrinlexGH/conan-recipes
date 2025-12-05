cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(SteamworksSDK CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example SteamworksSDK::SteamworksSDK)

add_custom_command(TARGET example POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy -t $<TARGET_FILE_DIR:example> $<TARGET_RUNTIME_DLLS:example>
    COMMAND_EXPAND_LISTS
)
