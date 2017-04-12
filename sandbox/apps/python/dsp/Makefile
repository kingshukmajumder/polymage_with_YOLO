APPS = vuvuzela \
	   unwanted_spectral \
	   upfirdn

all: 
	@-for d in $(APPS); do \
		make -C $$d $@; \
		done

clean:
	@-for d in $(APPS); do \
		make -C $$d clean; \
		done
