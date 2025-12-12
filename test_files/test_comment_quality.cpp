/*
 * test_comment_quality.cpp
 *
 * Test file for demonstrating improper indentation detection
 * This file contains subtle indentation issues that the analyzer detects
 *
 * Expected violations: 4 improper_indentation (WARNING)
 * - Lines 72, 74, 76, 78: Indentation level mismatches
 */

#include <iostream>
#include <string>

const int MAX_STUDENTS = 50;
const double PASSING_GRADE = 60.0;

// Calculate student's final grade based on assignments and exams
double calculateFinalGrade(double assignments, double exams) {
    double weighted = (assignments * 0.4) + (exams * 0.6);
    double final = weighted;
    return final;
}

// Process grades for all students in the class
void processGrades() {
    double grades[MAX_STUDENTS];

    // Initialize array
    for (int i = 0; i < MAX_STUDENTS; i++) {
        grades[i] = 0.0;
    }

    // Check each student's grade
    for (int i = 0; i < MAX_STUDENTS; i++) {
        if (grades[i] >= PASSING_GRADE) {
            std::cout << "Pass" << std::endl;
        }
    }
}

// This function validates that a student ID is within valid range
bool isValidStudentId(int id) {
    if (id > 0 && id <= MAX_STUDENTS) {
        return true;
    }
    return false;
}

// Display the results to the console
void displayResults() {
    std::cout << "Displaying results..." << std::endl;
    std::cout << "Done" << std::endl;
}

// Calculates letter grade from numerical score
char getLetterGrade(double score) {
    if (score >= 90) {
        return 'A';
    } else if (score >= 80) {
        return 'B';
    } else if (score >= 70) {
        return 'C';
    } else if (score >= 60) {
        return 'D';
    } else {
        return 'F';
    }
}

int main() {
    // Main function
    processGrades();
    displayResults();

    return 0;
}
