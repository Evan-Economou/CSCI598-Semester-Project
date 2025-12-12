#include <iostream>

void noCommentsFunction() {
    int x = 5;
    int y = 10;
    int z = x + y;
    std::cout << z << std::endl;
}

int main() {
    noCommentsFunction();
    return 0;
}
