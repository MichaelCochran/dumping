#include <iostream>
#include <vector>
#include <string>
#include <boost/version.hpp>
#include <boost/algorithm/string.hpp>
#include <opencv2/core.hpp>
#include <curl/curl.h>

int main() {
    std::cout << "Test application" << std::endl;
    std::cout << "Boost version: " << BOOST_VERSION << std::endl;
    
    std::vector<std::string> data;
    cv::Mat image;
    
    CURL* curl = curl_easy_init();
    if (curl) {
        curl_easy_cleanup(curl);
    }
    
    return 0;
}
