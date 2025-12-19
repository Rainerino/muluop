#include <cassert>
#include <iostream>
#include <string>

std::string get_greeting() {
    return "Hello, World!";
}

int main() {
    std::string greeting = get_greeting();
    assert(greeting == "Hello, World!");
    std::cout << "Test passed!" << std::endl;
    return 0;
}
