/*
 * test_semantic.cpp
 *
 * Test file for LLM semantic analysis
 * This file intentionally contains semantic violations
 *
 * Expected LLM violations:
 * - Memory leaks (new without delete)
 * - Naming convention violations (snake_case vs camelCase/PascalCase)
 * - Magic numbers
 * - NULL vs nullptr
 * - Missing default in switch
 * - Variable shadowing
 * - Deep nesting
 */

#include <iostream>
#include <string>

// Test 1: CRITICAL - Memory leak (new without delete)
void memoryLeakExample() {
    int* data = new int[100];
    // Process data...
    data[0] = 42;
    // VIOLATION: Missing delete[] - memory leak!
}

// Test 2: CRITICAL - Wrong delete type
void wrongDeleteType() {
    int* arr = new int[50];
    // ... use array ...
    delete arr;  // VIOLATION: Should be delete[] for array
}

// Test 3: WARNING - Naming convention violations
class my_bad_class {  // VIOLATION: Should be MyBadClass (PascalCase)
    int value;

    void Calculate_Sum() {  // VIOLATION: Should be calculateSum (camelCase)
        int result = 0;
    }
};

// Test 4: WARNING - Magic numbers
void calculatePrice() {
    int age = 25;

    if (age > 18) {  // VIOLATION: Magic number 18
        std::cout << "Adult" << std::endl;
    }

    double price = 100 * 1.15;  // VIOLATION: Magic number 1.15
    int maxUsers = 500;  // VIOLATION: Magic number 500
}

// Test 5: WARNING - NULL vs nullptr
void nullPointerExample() {
    int* ptr = NULL;  // VIOLATION: Use nullptr in modern C++
    char* str = 0;    // VIOLATION: Use nullptr instead of 0

    int* goodPtr = nullptr;  // OK
}

// Test 6: CRITICAL - Missing default case in switch
void switchExample(int choice) {
    switch (choice) {
        case 1:
            std::cout << "One" << std::endl;
            break;
        case 2:
            std::cout << "Two" << std::endl;
            break;
        // VIOLATION: Missing default case
    }
}

// Test 7: CRITICAL - Variable shadowing
class MyClass {
    int value;

    void setValue(int value) {  // VIOLATION: Parameter shadows member variable
        value = value;  // Ambiguous - which value?
    }
};

// Test 8: WARNING - Deep nesting (>3 levels)
void deeplyNested(int x) {
    if (x > 0) {
        if (x < 100) {
            if (x % 2 == 0) {
                if (x % 3 == 0) {  // VIOLATION: 4 levels deep
                    std::cout << "Divisible by 6" << std::endl;
                }
            }
        }
    }
}

// Test 9: CRITICAL - Uninitialized variable usage
void uninitializedVariable() {
    int x;
    std::cout << x;  // VIOLATION: x is uninitialized
}

// Test 10: WARNING - Long function (>50 lines) with multiple issues
void longFunctionWithIssues() {
    int data1 = 1;
    int data2 = 2;
    int data3 = 3;
    int data4 = 4;
    int data5 = 5;
    int data6 = 6;
    int data7 = 7;
    int data8 = 8;
    int data9 = 9;
    int data10 = 10;
    int data11 = 11;
    int data12 = 12;
    int data13 = 13;
    int data14 = 14;
    int data15 = 15;
    int data16 = 16;
    int data17 = 17;
    int data18 = 18;
    int data19 = 19;
    int data20 = 20;
    int data21 = 21;
    int data22 = 22;
    int data23 = 23;
    int data24 = 24;
    int data25 = 25;
    int data26 = 26;
    int data27 = 27;
    int data28 = 28;
    int data29 = 29;
    int data30 = 30;
    int data31 = 31;
    int data32 = 32;
    int data33 = 33;
    int data34 = 34;
    int data35 = 35;
    int data36 = 36;
    int data37 = 37;
    int data38 = 38;
    int data39 = 39;
    int data40 = 40;
    int data41 = 41;
    int data42 = 42;
    int data43 = 43;
    int data44 = 44;
    int data45 = 45;
    int data46 = 46;
    int data47 = 47;
    int data48 = 48;
    int data49 = 49;
    int data50 = 50;
    int data51 = 51;  // VIOLATION: Function is too long
}

// Test 11: Multiple memory issues
void multipleMemoryIssues() {
    int* p1 = new int(10);
    int* p2 = new int(20);

    delete p1;
    delete p1;  // VIOLATION: Double delete

    // VIOLATION: p2 never deleted - memory leak
}

// Test 12: Good example (no violations)
void goodExample() {
    const int LEGAL_AGE = 18;  // Named constant instead of magic number
    int* data = new int[100];

    // ... use data ...

    delete[] data;  // Properly freed
    data = nullptr;  // Set to nullptr after deletion
}
