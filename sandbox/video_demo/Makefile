DIRS = bilateral_grid harris_corner local_laplacian unsharp_mask

all: naive opt

naive:
	    @-for d in $(DIRS); do \
			        make -C $$d naive; \
					        done

opt:
	    @-for d in $(DIRS); do \
			        make -C $$d opt; \
					        done

clean:
	    @-for d in $(DIRS); do \
			        make -C $$d clean; \
					        done
		rm -rf *.pyc __pycache__
