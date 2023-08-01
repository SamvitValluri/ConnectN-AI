from copy import deepcopy
import numpy as np
from mctsNN import *
#from MonteCarloTS import *
import traceback
import time

class Board():
    def __init__(self, board = None):
        self.size = 3
        self.connect_n = 3

        self.player1 = int(1)
        self.player2 = int(-1)
        self.empty_square = int(0)

        self.position = np.zeros((self.size, self.size))

        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)

    def make_move(self, move):
        board = Board(self)

        row = move % self.size

        col = int(move / self.size)

        board.position[row, col] = self.player1

        count = (board.position == self.empty_square).sum()
        placed_tiles = self.size**2 - count
        if placed_tiles % 2:
            (board.player1, board.player2) = (board.player2, board.player1)
        return board

    def is_draw(self):
        if self.empty_square in self.position:
            return False
        else:
            return True


    def is_win(self):
        ##################################
        # vertical sequence detection
        ##################################
        for col in range(self.size):
            prev_position = None
            count = 0
            for row in range(self.size):
                if self.position[row, col] == self.player2 and self.position[row, col] == prev_position:
                    count += 1
                else:
                    count = 1
                    prev_position = self.position[row, col]
                if count == self.connect_n:
                    return True

        ##################################
        # horizontal sequence detection
        ##################################


        for row in range(self.size):
            prev_position = None
            count = 0
            for col in range(self.size):
                if self.position[row, col] == self.player2 and self.position[row, col] == prev_position:
                    count += 1
                else:
                    count = 1
                    prev_position = self.position[row, col]
                if count == self.connect_n:
                    return True

        #############################
        #diagonal sequence detection
        #############################
        diags = []
        diag = []
        anti_diag = []
        for p in range(2*self.size - 1):

            for q in range( max(0, p - self.size + 1), min(p + 1, self.size)):
                diag.append(self.position[self.size - p + q - 1  , q ])
                anti_diag.append(self.position[p - q  , q ])
            diags.append(diag)
            diags.append(anti_diag)
            diag = []
            anti_diag = []

        for i in range(len(diags)):
            if len(diags[i]) >= self.connect_n:
                prev_position = None
                count = 0
                for j in range(len(diags[i])):
                    if diags[i][j] == self.player2 and diags[i][j] == prev_position:
                        count += 1
                    else:
                        count = 1
                        prev_position = diags[i][j]
                    if count == self.connect_n:
                        return True

        return False


    def generate_states(self):

        # define states list (move list - list of available actions to consider)
        actions = []
        moves = []

        # loop over board rows
        for row in range(self.size):
            # loop over board columns
            for col in range(self.size):
                # make sure that current square is empty
                if self.position[row, col] == self.empty_square:
                    # append available action/board state to action list
                    move = row + self.size*col
                    moves.append(move)
                    actions.append(self.make_move(move))

        return moves
        ##returns a 1D array in the form of row + col / 100
        #row, col = np.where(self.position == 0)
        #actions = row + col / 100
        #return actions


    def human_move(self):
        while True:
            user_input = input('> ')

            # escape condition
            if user_input == 'exit': pass


            # skip empty input
            if user_input == '': pass

            try:
                # parse user input (move format [col, row]: 1,2)
                row = int(user_input.split(',')[1]) - 1
                col = int(user_input.split(',')[0]) - 1

                # check move legality
                if self.position[row, col] != self.empty_square:
                    print(' Illegal move!')
                    continue

                move = row + col*self.size 
                # make move on board
                return(move)

            except Exception as e:
                #traceback.print_exc()
                print('  Error:', e)
                print('  Illegal command!')
                print('  Move format [x,y]: 1,2 where 1 is column and 2 is row')


    def ai_move(self):
        mcts = MCTS()
        tick = time.time()
        best_move = mcts.search(self)
        tock = time.time()
        print(tock - tick)
        return(best_move)


    def game_loop(self):
        print('  Type "exit" to quit the game')
        print('  Move format [x,y]: 1,2 where 1 is column and 2 is row')

        # print board
        print(self)


        # game loop
        while True:
            # get user input
            if self.player1 == -1:
                move = self.human_move()
                self = self.make_move(move)
                print(self)
            # check if the game is won
            if self.is_win():
                print('player "%s" has won the game!\n' % self.player2)
                break

                # check if the game is drawn
            elif self.is_draw():
                print('Game is drawn!\n')
                break

            if self.player1 == 1:
                #move = self.human_move()
                #self = self.make_move(move)
                #print(self)

                best_move = self.ai_move()
                self = best_move.board
                print(self)

            # check if the game is won
            if self.is_win():
                if self.player2 == 1:
                    print('player "x" has won the game!\n')
                elif self.player2 == -1:
                    print('player "o" has won the game!\n')
                break

                # check if the game is drawn
            elif self.is_draw():
                print('Game is drawn!\n')
                break


    def __str__(self):

        board_string = ''
        xo_board = self.position
        xo_board = xo_board.astype(object)
        xo_board[ xo_board == 0] = '.'
        xo_board[ xo_board == 1] = 'x'
        xo_board[ xo_board == -1] = 'o'


        for row in range(self.size):
            for col in range(self.size):
                board_string += ' %s' % xo_board[row, col]
        # print new line every row
            board_string += '\n'

        # prepend side to move
        if self.player1 == 1:
            board_string = '\n--------------\n "x" to move:\n--------------\n\n' + board_string

        elif self.player1 == -1:
            board_string = '\n--------------\n "o" to move:\n--------------\n\n' + board_string

        # return board string
        return board_string

if __name__ == '__main__':
    # create board instance
    board = Board()
    #board = board.make_move(1,1) 
    #board = board.make_move(1,2)
    #states = board.generate_states()
    #for state in states:
    #    print(state)
    #    print(state.player2)
    board.game_loop()
