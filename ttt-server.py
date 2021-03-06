import socket, sys
from constants import *

DRAW = -1
NOT_OVER = 0
WIN = 1

GUIDELINES = ['[q|x|e]', '[a|s|d]', '[z|x|c]']
INDEX_DICT={'q':(0, 0), 'x':(0, 1), 'e':(0, 2),
		    'a':(1, 0), 's':(1, 1), 'd':(1, 2),
		    'z':(2, 0), 'x':(2, 1), 'c':(2, 2)}

def stringify_raw_board(board):
	s = ''
	s += '[%s]' % '|'.join(board[0]) + '\n'
	s += '[%s]' % '|'.join(board[1]) + '\n'
	s += '[%s]' % '|'.join(board[2]) + '\n'
	return s

def stringify_board(board):
	s = ''
	s += '[%s]' % '|'.join(board[0]) + " " + GUIDELINES[0] + '\n'
	s += '[%s]' % '|'.join(board[1]) + " " + GUIDELINES[1] + '\n'
	s += '[%s]' % '|'.join(board[2]) + " " + GUIDELINES[2] + '\n'
	return s

def check_state(b):
	wins = ['XXX', 'OOO']

	if ''.join(b[0]) in wins or\
		''.join(b[1]) in wins or\
		''.join(b[2]) in wins or\
		''.join((b[0][0], b[1][0], b[2][0])) in wins or\
		''.join((b[0][1], b[1][1], b[2][1])) in wins or\
		''.join((b[0][2], b[1][2], b[2][2])) in wins or\
		''.join((b[0][0], b[1][1], b[2][2])) in wins or\
		''.join((b[0][2], b[1][1], b[2][0])) in wins:
		return WIN

	if ' ' not in b[0] and\
		' ' not in b[1] and\
		' ' not in b[2]:
		return DRAW

	return NOT_OVER

def get_p(turn):
	return 'X' if turn else 'O'

def apply_move_to_board(board, move, turn):
	x, y = INDEX_DICT[move]
	board[x][y] = get_p(turn)

def get_play_again(players):
	print "Getting 'play again?'' from other clients"
	play1 = players[0].recv(2)
	play2 = players[1].recv(2)

	if play1 == play2 == TAG_RESTART:
		print "Restarting game"
		for player in players:
			player.sendall(TAG_RESTART)
		return True
	else:
		print "Ending game"
		for player in players:
			player.sendall(TAG_QUIT)
		return False

def play_game(X, O, starting_turn):
	print "Sending tags to players"
	X.sendall('X')
	O.sendall('O')

	#init game data
	players = [X, O]
	X_turn = starting_turn
	board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
	available_moves = 'qweasdzxcp'

	#run game
	while True:
		print "Sending game data to players"
		for player in players:
			player.sendall(TAG_NORMAL + stringify_board(board) + DELIM + get_p(X_turn) + DELIM + available_moves)

		current_player = X if X_turn else O
		other_player = O if X_turn else X

		print "Getting move from player %s" % get_p(X_turn)
		move = current_player.recv(1)

		print "Got move", move
		if move == QUIT_KEY:
			other_player.sendall(TAG_QUIT)
			return False

		apply_move_to_board(board, move, X_turn)
		available_moves.replace(move, "")

		state = check_state(board)

		#next turn starts
		if state == NOT_OVER:
			print "Next turn"
			X_turn = not X_turn

		#handle game over	
		else:
			print "Game over. Sending result to clients"
			raw_board = stringify_raw_board(board)

			if state == DRAW:
				for player in players:
					player.sendall(TAG_DRAW + raw_board)

			elif state == WIN:
				print "WIN for %s" % get_p(X_turn)
				current_player.sendall(TAG_WIN + raw_board)
				other_player.sendall(TAG_LOSS + raw_board)

			play_again = get_play_again(players)
			return play_again

def host_clients(server):
	print "Waiting for players to connect..."
	X, _ = server.accept()
	print "P1 connected"
	O, _ = server.accept()
	print "P2 connected"

	play = True
	turn = True
	while play:
		play = play_game(X, O, turn)
		turn = not turn #swap starting turns
		print "Playing again" if play else "Not playing again"

	X.close()
	O.close()

def main():
	global available_moves

	#create server
	print "Running server"
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try: server.bind(("", SERVER_PORT))
	except: 
		print "Bind error. Is port already in use?"
		sys.exit(1)
	server.listen(5)

	try:
		#try to connect to clients and run game
		while True: host_clients(server)
	except KeyboardInterrupt:
		print "Shutting down server."
		server.close()

if __name__ == '__main__':
	main()