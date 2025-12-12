/*
 * test_clean.cpp
 *
 * Clean test file with no violations
 * Should pass all algorithmic and semantic checks
 *
 * Author: Test Suite
 */

#include <iostream>
#include <memory>

// Named constants instead of magic numbers
const int MAX_SIZE = 100;
const int LEGAL_AGE = 18;
const double TAX_RATE = 1.15;

// Good class with proper naming conventions
class BankAccount {
private:
    double balance;

public:
    // Constructor with proper initialization
    BankAccount(double initialBalance) {
        balance = initialBalance;
    }

    // Getter method - proper camelCase naming
    double getBalance() {
        return balance;
    }

    // Setter method with proper parameter naming
    void setBalance(double newBalance) {
        balance = newBalance;
    }
};

// Function with proper error handling and braces
void processData() {
    // Use smart pointers instead of raw new/delete
    std::unique_ptr<int[]> data(new int[MAX_SIZE]);

    // Initialize array
    for (int i = 0; i < MAX_SIZE; i++) {
        data[i] = i * 2;
    }

    // Process data with proper braces on all control structures
    if (data[0] > 0) {
        std::cout << "First element is positive" << std::endl;
    }
}

// Function with proper switch statement including default
void handleChoice(int choice) {
    switch (choice) {
        case 1:
            std::cout << "Option 1" << std::endl;
            break;
        case 2:
            std::cout << "Option 2" << std::endl;
            break;
        default:
            std::cout << "Invalid choice" << std::endl;
            break;
    }
}

// Function using nullptr instead of NULL
void pointerExample() {
    int* ptr = nullptr;

    if (ptr == nullptr) {
        std::cout << "Pointer is null" << std::endl;
    }
}

// Main function with proper structure
int main() {
    // Create account with named constant
    BankAccount account(1000.0);

    // Process data
    processData();

    // Handle user choice
    handleChoice(1);

    // Demonstrate pointer usage
    pointerExample();

    return 0;
}
