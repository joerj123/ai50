"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.

    Count the number of X's and O's. If X > O, O otherwise X. X always gets the first move.
    If game has ended, return "the game is over".
    """
    #print("entering player")

    countX = 0
    countO = 0
    countEmpty = 0

    for row in board:
        for cell in row:
            if cell == 'X':
                countX += 1
            elif cell == 'O':
                countO += 1
            else:
                countEmpty +=1
    
    #print(countX, countO, countEmpty)

    if countEmpty == 9:
        #print("Returning X")
        return 'X'
    elif countX > countO:
        #print("Returning O")
        return 'O'
    elif countO >= countX and countEmpty != 0:
        #print("Returning X")
        return 'X'
    else:
        return "the game is over"



def actions(board):
    """
    Returns set of all possible actions in tuple format (i, j) available on the board.
    i represents row, so 0, 1, 2.
    j represents the cell, so 0, 1, 2
    """
    # print("entering actions")
    possible_actions = set()

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                possible_actions.add((i,j))
    return possible_actions



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board, but does NOT modify the original board.

    copy the existing board

    iterate over existing board cells. 
        If cell matches action
            if cell == EMPTY
                add the player
            else
                return raise exception - check out how to handle exceptions. Likely expand the 'base' class to create a custom exception.
                
        else
            return newboard, using deepcopy, which contains a reference to previous versions of the copy.

    """
    if terminal(board):
        return
 
    # print("Entering result. Action is", action, 'Type of action is:', type(action))
    current_player = player(board)

    newboard = copy.deepcopy(board)

    #Iterate over the existing board
    #todo: can make this more efficient as it doesn't need to iterate through every cell (we know the index)

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if action is not None:
                # If the index matches the action.
                if i == action[0] and j == action[1]:
                    if board[i][j] == EMPTY:
                        #print("Added move: ", current_player)
                        newboard[i][j] = current_player
                    else:
                        raise Exception('Invalid action / move - cell full')
            else:
                print("Action is None")


    #print("Returning new board")
    #print("Newboard player == ", player(newboard))
    return newboard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #print("Entering Winner")

    # Check horizontal lines for wins
    for row in board:
        result = winrow([row[0],row[1],row[2]])
        if result != None:
            #print("Winner found horizontal")
            return result
    
    # Check vertical lines for wins
    for i in range(3):
        result = winrow([board[0][i], board[1][i], board[2][i]])
        if result != None:
            return result
    
    # Check diagonal lines for wins
    result = winrow([board[0][0],board[1][1],board[2][2]])
    if result != None:
        return result
    result = winrow([board[0][2],board[1][1],board[2][0]])
    if result != None:
        return result
    
    # If no winner is detected yet, return None
    #print("No winner found so returning None")
    return None

def winrow(numbers):

    """
    Takes 3 numbers from a row and returns a winner if there is one.
    """

    countx = 0
    countO = 0

    for i in numbers:
        if i == 'X':
            countx += 1
        if i == 'O':
            countO += 1

    if countx == 3:
        return('X')
    elif countO == 3:
        return('O')
    else:
        return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    #print("Entering terminal")
    # A game is over when either (a) there is a winner OR (b) there are no turns left & no winner.

    if winner(board):
        return True
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    result = winner(board)
    
    if result == 'X': 
        return 1
    elif result == 'O':
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    Must be an allowable move.
    If multiple are optimal, any are allowable.
    X always wants max score.
    O always wants to minimize the score.

    Takes an initial state.
    Needs to know who is the player
    Need some legal actions.
    Need to see the results.
    Also need to see if it's a terminal state.
    Need a utility that gives a value for terminal state.

    """

    # If board is terminal, return None
    if terminal(board):
        return None
    
    # Get player and possible actions
    playernow = player(board)

    # Define maximum value of a board function
    def maxvalue(board):
        if terminal(board):
            return utility(board)
        
        # We start with the worst possible utility (neg infinite). So in the loop, if we find a better utility, v becomes that.
        v = float('-inf')
        for action in actions(board):
            #print("Action in maxvalue loop: ", action)
            # We check if the next action is better than the last 'best' action, and set v to it if so.
            # I'm interested in the min value because I want to prevent the opponent minimising the value. So I pick the 'max' of those moves.
            v = max(v, minvalue(result(board, action)))
        return v
    
    # Define minimum value of a board function.
    def minvalue(board):
        if terminal(board):
            return utility(board)
        v = float('inf')
        for action in actions(board):
            #print("Action in minvalue loop: ", action)
            v = min(v, maxvalue(result(board, action)))
        return v

    if playernow == 'X':
        #print("entering playernow X")
        bestmovex = None
        bestutility = float('-inf')
        for action in actions(board):
            value = maxvalue(result(board, action))
            if value > bestutility:
                    bestutility = value
                    bestmovex = action
        return bestmovex

    if playernow == 'O':
        #print("entering playernow O")
        bestmovey = None
        bestutility = float('inf')
        for action in actions(board):
            value = minvalue(result(board, action))
            if value < bestutility:
                bestutility = value
                bestmovey = action
        return bestmovey