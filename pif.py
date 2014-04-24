#!/usr/bin/python

PORT = 50007
MSG = 'pif'
SO_BINDTODEVICE = 25 # not in python socket lib for some reason

import socket
import select
import time
import argparse
from daemon import Daemon

def chime(timeout, iface=None, msg = ''):
	# deamonise and send a pif message at timeout rate
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	if iface != None:
		s.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE, iface)
	s.bind(('', 0))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	while True:
		m = MSG + msg
		s.sendto(m, ('<broadcast>', PORT))
		time.sleep(timeout)

class ChimeDaemon(object,Daemon):
	timeout = 2
	msg = ''
	def run(self):
		chime(self.timeout, self.msg)

def daemon(cmd, timeout, msg):
	daemon = ChimeDaemon('/tmp/chime-daemon.pid')
	daemon.timeout = timeout
	daemon.msg = msg
	print "daemon made"
	if cmd == 'start':
		print "starting"
		daemon.start()
	elif cmd == 'stop':
		daemon.stop()
	elif cmd == 'restart':
		daemon.restart()
	else:
		return False
	print "success"
	return True

def search(timeout, iface=None, console=True):
	# look for pif messages and print out the devices found
	if console:
		print "searching for pif devices"
	end_time = time.time() + timeout
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	if iface != None:
		s.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE, iface)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('', PORT))
	s.setblocking(0)
	found = {}
	while 1:
		try:
			if select.select([s], [], [], 1)[0]:
				msg, addr = s.recvfrom(256)
				if MSG in msg:
					msg = msg.split(MSG)
					if len(msg) > 1 and len(msg[1]) > 0:
						if console and (str(addr[0]) not in found):
							print "pif found: %s: %s" % (str(addr[0]), msg[1])
						found[str(addr[0])] = msg[1]
					else:
						if console and (str(addr[0]) not in found):
							print "pif found: %s" % (str(addr[0]))
						found[str(addr[0])] = ""
			now = time.time()
			if now > end_time:
				break
		except KeyboardInterrupt:
			break
	return found

def main():
	parser = argparse.ArgumentParser('pif, broadcast search tool')
	parser.add_argument('-t', '--timeout', help='timeout for the operation, for search this is the time to search, for chime this is the delay between chimes')
	parser.add_argument('-s', '--search', action='store_true', help='search for pif devices')
	parser.add_argument('-c', '--chime', action='store_true', help='broadcast pif message with ipaddress at regular intervals')
	parser.add_argument('-m', '--message', nargs=1, help='add a message to the pif chime that will be shown with the device when found in a search')
	parser.add_argument('-d', '--daemon', nargs=1, help='[start|stop|restart] chime processes as a deamon')
	parser.add_argument('-i', '--interface', nargs=1, help='interface to listen or broadcast too')
	args = parser.parse_args()
	timeout = 2
	iface = None
	msg = ''
	if args.timeout:
		timeout = int(args.timeout)
	if args.message:
		msg = args.message[0]
	if args.interface:
		iface = args.interface[0]
		print "using interface " + iface
	if args.search:
		search(timeout, iface)
	elif args.daemon:
		if not daemon(args.daemon[0], timeout, msg):
			print "error: daemon options are [start|stop|restart]"
			parser.print_help()
	elif args.chime:
		chime(timeout, iface, msg)
	else:
		print "error: no option specified"
		parser.print_help()

if __name__ == "__main__":
    main()

