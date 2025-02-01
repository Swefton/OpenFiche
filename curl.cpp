#include <iostream>
#include <string>
#include <curl/curl.h>

size_t writeCallback(void* data, size_t size, size_t nmemb, void* userp) {
    std::string* str = static_cast<std::string*>(userp);
    str->append(static_cast<char*>(data), size * nmemb);
    return size * nmemb;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <url>\n";
        return 1;
    }

    std::string url = argv[1];
    std::string content;
    CURL* curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &content);
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
        if (curl_easy_perform(curl) != CURLE_OK) {
            std::cerr << "Error fetching URL\n";
        } else {
            std::cout << content;
        }
        curl_easy_cleanup(curl);
    }
    return 0;
}
