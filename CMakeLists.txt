# Windows 環境で Boost を使うときに BOOST_ROOT 環境変数を利用する
# https://cmake.org/cmake/help/latest/policy/CMP0074.html
cmake_minimum_required(VERSION 3.12)

project(MARATHON_MATCH_TEMPLATE)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(Boost REQUIRED)

add_executable(main main.cpp)

target_link_libraries(main Boost::headers)
