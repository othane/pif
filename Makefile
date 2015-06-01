install:
	pip install daemon
	sudo ln -fs `pwd`/pif.py /usr/bin/pif
	cp init.d/pif /etc/init.d/
	update-rc.d pif defaults
