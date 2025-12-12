/*
 * test_algorithmic.cpp
 *
 * Test file for algorithmic style checks
 * This file intentionally contains violations to test the analyzer
 *
 * Expected violations:
 * - Inconsistent indentation (tabs vs spaces)
 * - Missing braces on single-line if statements
 */

#include <iostream>

// Test 1: Inconsistent indentation (this section uses TABS)
void testTabs() {
	int x = 5;
	if (x > 0) {
		std::cout << "Positive" << std::endl;
	}
}

// Test 2: Inconsistent indentation (this section uses SPACES - should trigger violation)
void testSpaces() {
    int y = 10;
    if (y > 0) {
        std::cout << "Positive" << std::endl;
    }
}

// Test 3: Missing braces on single-line if statements
void testMissingBraces() {
    int x = 5;
    if (x > 0)
        x++;  // Missing braces

    // Another violation
    if (x < 10) x--;

    // This is OK - has braces
    if (x == 5) {
        x *= 2;
    }

    // Violation - for loop without braces
    for (int i = 0; i < 5; i++)
        std::cout << i;

    // Violation - while loop without braces
    while (x > 0)
        x--;
}

// Test 4: Comment frequency (20+ lines without comment)
void testCommentFrequency() {
    int a = 1;
    int b = 2;
    int c = 3;
    int d = 4;
    int e = 5;
    int f = 6;
    int g = 7;
    int h = 8;
    int i = 9;
    int j = 10;
    int k = 11;
    int l = 12;
    int m = 13;
    int n = 14;
    int o = 15;
    int p = 16;
    int q = 17;
    int r = 18;
    int s = 19;
    int t = 20;
    int u = 21;  // Should trigger violation around here
}
