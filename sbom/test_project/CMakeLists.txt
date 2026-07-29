cmake_minimum_required(VERSION 3.10)
project(TestApp VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)

find_package(Boost 1.70 REQUIRED COMPONENTS algorithm)
find_package(OpenCV 4.0 REQUIRED)
find_package(CURL REQUIRED)

add_executable(test_app main.cpp)

target_link_libraries(test_app
    Boost::algorithm
    ${OpenCV_LIBS}
    CURL::libcurl
)
