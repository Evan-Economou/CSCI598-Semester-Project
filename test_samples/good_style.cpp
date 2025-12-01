// Program: Example Calculator
// Author: Test User
// Purpose: Demonstrate good C++ coding style

#include <iostream>
#include <string>

const int ADULT_AGE = 18;
const int MIN_VALUE = 5;

int main() {
    int age = 20;
    int value = 10;
    
    // Check if person is adult
    if (age > ADULT_AGE) {
        std::cout << "Adult" << std::endl;
    }
    
    // Check value threshold
    if (value > MIN_VALUE) {
        std::cout << "Greater than minimum" << std::endl;
    }
    
    return 0;
}
