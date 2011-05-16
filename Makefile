help:
	cat Makefile

clean:
	-find . -name "*.pyc" -exec rm {} \;
	-rm -rf _trial_temp
