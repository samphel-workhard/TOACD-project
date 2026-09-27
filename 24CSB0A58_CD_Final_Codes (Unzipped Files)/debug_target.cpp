
    #include <iostream>

    int main() {
        int numbers[3] = {10, 20, 30};
        
        // BUG: Looping too far (i <= 3 means it accesses numbers[3] which doesn't exist)
        for(int i = 0; i <= 3; i++) {
            numbers[i] = numbers[i] * 2;
        }
        
        return 0;
    }
    