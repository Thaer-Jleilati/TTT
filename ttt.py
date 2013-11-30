import os, sys, subprocess, socket

DRAW = -1
NOT_OVER = 0
WIN = 1
remaining_tiles = 'abcdefghiq'

board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
guidelines = ['[a|b|c]', '[d|e|f]', '[g|h|i]']

def get_p(turn):
	return 'X' if turn else 'O'

def clear():
	subprocess.call('clear')

def display_board_raw():
	print '[%s]' % '|'.join(board[0])
	print '[%s]' % '|'.join(board[1])
	print '[%s]' % '|'.join(board[2])

def display_board():
	print '[%s]' % '|'.join(board[0]) + " " + guidelines[0]
	print '[%s]' % '|'.join(board[1]) + " " + guidelines[1]
	print '[%s]' % '|'.join(board[2]) + " " + guidelines[2]

def process_input(turn):
	global remaining_tiles

	inp = raw_input().lower()
	while inp not in remaining_tiles or len(inp) != 1:
		inp = raw_input().lower()
	if inp == 'q':
		print 'Thanks for playing!'
		sys.exit(0)
	else:
		flat_index = ord(inp) - ord('a')
		x = flat_index/3
		y = flat_index%3
		board[x][y] = get_p(turn)
		remaining_tiles = remaining_tiles.replace(inp, '')

def check_state(turn):
	wins = ['XXX', 'OOO']
	b = board

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

def main():
	running = True
	X_turn = True

	clear()
	while running:
		print 'Welcome to Tic-Tac-Toe! Q to quit.\n'
		print "Player %s's turn." % get_p(X_turn)
		display_board()
		process_input(X_turn)
		state = check_state(X_turn)
		if state == NOT_OVER:
			X_turn = not X_turn
			clear()
		elif state == DRAW:
			clear()
			display_board_raw()
			print "It's a draw!"
			running = False
		elif state == WIN:
			clear()
			display_board_raw()
			print "Player %s wins! Congrats!" % get_p(X_turn)
			running = False

if __name__ == '__main__':
	main()