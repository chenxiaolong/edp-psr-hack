KDIR ?= /lib/modules/`uname -r`/build

.PHONY: clean

default:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
