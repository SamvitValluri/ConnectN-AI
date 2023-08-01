#
# MCTS algorithm implementation
#
# packages

import numpy as np
import random

# tree node class definition
class TreeNode():
    # class constructor (create tree node class instance)
    def __init__(self, board, move, parent = None):
        # init associated board state
        self.board = board
        self.move = move

        # init is node terminal flag
        if self.board.is_win() or self.board.is_draw():
            # we have a terminal node
            self.is_terminal = True

        # otherwise
        else:
            # we have a non-terminal node
            self.is_terminal = False

        # init is fully expanded flag
        self.is_fully_expanded = self.is_terminal

        # init parent node if available
        self.parent = parent

        # init the number of node visits
        self.visits = 0

        # init the total score of the node
        self.score = 0

        # init current node's children
        self.children = {}

# MCTS class definition
class MCTS():
    # search for the best move in the current position
    def search(self, initial_state):
        # create root node
        self.root = TreeNode(initial_state, None)
        self.current_side = initial_state.player1

        # walk through 1000 iterations
        for iteration in range(1000):
            # select a node (selection phase)
            node = self.select(self.root)

            # scrore current node (simulation phase)
            score = self.rollout(node.board)

            # backpropagate results
            self.backpropagate(node, score)

        # pick up the best move in the current position
        return self.get_best_move(self.root, 0)



    # select most promising node
    def select(self, node):
        # make sure that we're dealing with non-terminal nodes
        while not node.is_terminal:
            # case where the node is fully expanded
            if node.is_fully_expanded:
                node = self.get_best_move(node, 1)

            # case where the node is not fully expanded
            else:
                # otherwise expand the node
                return self.expand(node)

        # return node
        return node

    # expand node
    def expand(self, node):
        # generate legal states (moves) for the given node
        moves = node.board.generate_states()

        # loop over generated states (moves)
        for move in moves:
            # make sure that current state (move) is not present in child nodes
            if move not in node.children:   
                # create a new node
                state = node.board.make_move(move) 
                new_node = TreeNode(state, move, node)

                # add child node to parent's node children list (dict)
                node.children[move] = new_node

                # case when node is fully expanded
                if len(moves) == len(node.children):
                    node.is_fully_expanded = True

                # return newly created node
                return new_node


    # simulate the game via making random moves until reach end of the game
    def rollout(self, board):
        # make random moves for both sides until terminal state of the game is reached
        while not board.is_win():
            # try to make a move
            try:
                # make the on board
                board = board.make_move(random.choice(board.generate_states()))

            # no moves available
            except:
                # return a draw score
                return 0

        # return score from the player "x" perspective
        if board.player2 == 1: return 1
        elif board.player2 == -1: return -1

    # backpropagate the number of visits and score up to the root node
    def backpropagate(self, node, score):
        # update nodes's up to root node
        while node is not None:
            # update node's visits
            node.visits += 1

            # update node's score
            if self.current_side == node.board.player2:
                node.score += score

            # set node to parent
            node = node.parent

    # select the best node basing on UCB1 formula
    def get_best_move(self, node, exploration_constant):
        # define best score & best moves
        best_score = float('-inf')
        best_moves = []

        # loop over child nodes
        for child_node in node.children.values():
            # define current player
            # get move score using UCT formula
            move_score = child_node.board.player2 * child_node.score / child_node.visits + exploration_constant * np.sqrt(np.log(node.visits / child_node.visits))

            # better move has been found
            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]

            # found as good move as already available
            elif move_score == best_score:
                best_moves.append(child_node)
        # return one of the best moves randomly
        return random.choice(best_moves)
