check: check.cpp
	g++ -O3 -std=c++17 check.cpp -o check
clean:
	rm -f check
all: check

