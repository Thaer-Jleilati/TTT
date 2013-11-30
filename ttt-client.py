import socket, subprocess, sys, os
from constants import *

PLAY_AGAIN_INSTRUCTIONS = "R to play again, Q to quit"

#clear display, only works on unix
def clear():
	if os.name == 'nt':
		os.system('cls')
	else:
		subprocess.call('clear')

def get_move(board, available_moves):
	inp = raw_input().lower()
	while inp not in available_moves or len(inp) != 1:
		inp = raw_input().lower()
	else:
		return inp

def other_p(my_ID):
	return 'X' if my_ID == 'O' else 'O'

def connect_to_server(address):
	print "Connecting to server..."
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		conn.connect((address, SERVER_PORT))
	except:
		print "Could not connect to server. Are you sure it's running?"

	print "Waiting for server to be ready..."
	my_ID = conn.recv(1)
	return conn, my_ID

#each turn we get the new game state
def get_game_state_from_server(conn):
	data = conn.recv(DATA_LEN)
	tag = data[0]
	rest = None
	if len(data) > 1: rest = data[1:]

	return tag, rest

def run_turn(conn, data, my_ID):
	board, turn, available_moves = data.split(DELIM)
	clear()
	print 'Welcome to Tic-Tac-Toe! You are player %s. Q to quit\n' % my_ID
	print board

	if turn == my_ID:
		print 'Your turn! Move:'
		move = get_move(board, available_moves)
		conn.sendall(move)
		if move == 'q':
			print "Thanks for playing!"
			return False
	else:
		print 'Waiting for player %s to make his move...' % other_p(my_ID)
	return True

def get_play_again(conn):
	inp = raw_input().lower()

	if inp and inp[0] == 'r':
		conn.sendall(TAG_RESTART)

		#get other player's choice (can't restart if the other wants to quit)
		print "Waiting for other player's choice..."
		resp = conn.recv(1)

		if resp != TAG_RESTART:
			print "Sorry, other player doesn't want to play again."
			return False
		else:
			my_ID = conn.recv(1) #get tag once more since game restarts
			return True
	else:
		conn.sendall(TAG_QUIT)
		return False

def main():
	if len(sys.argv) > 1:
		conn, my_ID = connect_to_server(sys.argv[1])
	else:
		conn, my_ID = connect_to_server(DEFAULT_ADDRESS)
	

	running = True
	while running:
		tag, rest = get_game_state_from_server(conn)
		run = True #if should continue running after this turn

		#other player quit tag
		if tag == TAG_QUIT:
			print "Other player quit. Sorry!"
			running = False

		#game over tag
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

			run = get_play_again(conn)

		#normal tag, continue running game
		else:
			run = run_turn(conn, rest, my_ID)

		if not run: running = False

	conn.close()

if __name__ == '__main__':
	main()