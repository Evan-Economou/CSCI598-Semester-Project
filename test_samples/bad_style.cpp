// Missing file header comment with author and purpose

#include <iostream>
using namespace std;  // Avoid using namespace std in global scope

int main()
{
	int x=5;  // Tab character used, missing spaces around operator
	int y = 10;   
	
	// Magic number without constant
	if(x>18){
		cout<<"Adult"<<endl;
	}
	
	// Missing braces for single statement
	if (y > 5)
		cout << "Greater than 5" << endl;
	
	// Very long line that exceeds 100 characters limit - this is just to demonstrate the issue with line length violations
	
	return 0;
}
