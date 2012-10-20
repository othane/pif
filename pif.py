#!/usr/bin/python

PORT = 50007
MSG = 'pif'

import socket
import select
import time
import argparse

def chime(timeout):
	# deamonise and send a pif message at timeout rate
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', 0))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	while 1:
		msg = MSG
		s.sendto(msg, ('<broadcast>', PORT))
		time.sleep(timeout)

def search(timeout):
	# look for pif messages and print out the devices found
	print "seraching for pif devices"
	end_time = time.time() + timeout
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('', PORT))
	s.setblocking(0)
	while 1:
		try:
			if select.select([s], [], [], 1)[0]:
				msg, addr = s.recvfrom(32)
				if msg == MSG:
					print "pif found: " + str(addr[0])
			now = time.time()
			if now > end_time:
				break
		except KeyboardInterrupt:
			break

def main():
	parser = argparse.ArgumentParser('pif, raspberrypi find util')
	parser.add_argument('-t', '--timeout', help='timeout for the operation, for search this is the time to search, for chime this is the delay between chimes')
	parser.add_argument('-s', '--search', action='store_true', help='search for pif devices')
	parser.add_argument('-c', '--chime', action='store_true', help='broadcast pif message with ipaddress at regular intervals')
	args = parser.parse_args()
	timeout = 2
	if args.timeout:
		timeout = int(args.timeout)
	if args.search:
		search(timeout)
	elif args.chime:
		chime(timeout)
	else:
		print "error: no option specified"
		parser.print_help()

if __name__ == "__main__":
    main()

