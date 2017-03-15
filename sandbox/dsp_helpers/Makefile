CXX=icc
CXX_FLAGS=-O3 -ipo -xhost -ansi-alias
#CXX=gcc
#CXX_FLAGS=-O3 -march=native

all: test

test: test.out
	./test.out

test.out: dsp_helpers_test.c
	$(CXX) $(CXX_FLAGS) dsp_helpers.c dsp_helpers_test.c -o test.out

clean:
	rm -rf test.out
