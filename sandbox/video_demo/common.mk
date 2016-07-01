ifneq (,$(shell which icpc))
	CXX= icpc
	CXX_FLAGS= -qopenmp -xhost
else
	CXX= g++
	CXX_FLAGS= -fopenmp -march=native
endif


CXX_FLAGS+= -O3 -fPIC -shared

LIB_SRC=../simple_pool_allocator.cpp

all: $(APP)

polymage: $(APP)_opt.so
naive: $(APP)_naive.so

$(APP)_opt.so: $(APP)_polymage.cpp
	$(CXX) $(CXX_FLAGS) $(LIB_SRC) $< -o $@

$(APP)_naive.so: $(APP)_naive.cpp
	$(CXX) $(CXX_FLAGS) $(LIB_SRC) $< -o $@

clean:
	rm -rf *.pyc *.so __pycache__
