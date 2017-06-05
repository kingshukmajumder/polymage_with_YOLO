APPS = conv \
	   dropout \
	   relu \
	   softmax \
	   maxpool \
	   flatten \
	   fullyconnected \
	   conv_relu_pool

all: 
	@-for d in $(APPS); do \
		make -C $$d $@; \
		done

clean:
	@-for d in $(APPS); do \
		make -C $$d clean; \
		done

cleaner:
	@-for d in $(APPS); do \
		make -C $$d cleaner; \
		done
