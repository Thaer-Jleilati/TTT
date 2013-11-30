import socket, subprocess, sys
from constants import *

PLAY_AGAIN_INSTRUCTIONS = "R to play again, Q to quit"

def clear():
	subprocess.call('clear')

def get_move(board, available_moves):
	inp = raw_input().lower()
	while inp not in available_moves or len(inp) != 1:
		inp = raw_input().lower()
	else:
		return inp

def other_p(my_tag):
	return 'X' if my_tag == 'O' else 'O'

def main():
	print "Connecting to server..."
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		conn.connect(("127.0.0.1", SERVER_PORT))
	except:
		print "Could not connect to server. Are you sure it's running?"

	print "Waiting for server to be ready..."
	my_tag = conn.recv(1)

	running = True
	while running:
		data = conn.recv(DATA_LEN)
		tag = data[0]
		if len(data) > 1: rest = data[1:]

		if tag == TAG_QUIT:
			print "Other player quit. Sorry!"
			running = False
		elif tag != TAG_NORMAL:
			clear()
			board = rest
			print 'Game over!\n'
			print board

			if tag == TAG_WIN:
				print "Congrats! You win! (%s)" % PLAY_AGAIN_INSTRUCTIONS
			elif tag == TAG_LOSS:
				print "You lose. Aww shucks. (%s)" % PLAY_AGAIN_INSTRUCTIONS
			elif tag == TAG_DRAW:
				print "It's a draw! Meh. (%s)" % PLAY_AGAIN_INSTRUCTIONS

			inp = raw_input().lower()
			if inp and inp[0] == 'r':
				conn.sendall(TAG_RESTART)
				print "Waiting for other player's choice..."
				resp = conn.recv(1)
				if resp != TAG_RESTART:
					print "Sorry, other player doesn't want to play again."
					running = False
				else:
					my_tag = conn.recv(1)
			else:
				conn.sendall(TAG_QUIT)
				running = False

		else:
			board, turn, available_moves = rest.split(DELIM)
			clear()
			print 'Welcome to Tic-Tac-Toe! You are player %s. Q to quit\n' % my_tag
			print board

			if turn == my_tag:
				print 'Your turn! Move:'
				move = get_move(board, available_moves)
				conn.sendall(move)
				if move == 'q':
					print "Thanks for playing!"
					running = False
			else:
				print 'Waiting for player %s to make his move...' % other_p(my_tag)
	conn.close()

if __name__ == '__main__':
	main()