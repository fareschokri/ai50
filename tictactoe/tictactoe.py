"""
Tic Tac Toe Player
"""
import copy
import math


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
    """
    x_count = 0
    o_count = 0
    for el in board:
        x_count += el.count("X")
        o_count += el.count("O")
    if x_count + o_count == 9:
        return EMPTY
    elif x_count == o_count:
        return X
    elif x_count > o_count:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    empty_cells = []
    for idm, val in enumerate(board):
        for idx, value in enumerate(val):
            if value is None and not (idm, idx) in empty_cells:
                empty_cells.append((idm, idx))
    return empty_cells


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("ILLEGAL MOVE")
    else:
        new_board = copy.deepcopy(board)
        new_raw = new_board[action[0]]
        new_raw[action[1]] = player(board)
        new_board[action[0]] = new_raw
        return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    if board.count([EMPTY, EMPTY, EMPTY]) == 3:
        return None
    elif player(board) == X:
        former_player = O
    else:
        former_player = X

    former_player_cells = []
    winning_combos = [[(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],
                      [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
                      [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]]
    for idm, val in enumerate(board):
        for idx, value in enumerate(val):
            if value == former_player and (idm, idx) not in former_player_cells:
                former_player_cells.append((idm, idx))

    for idc, val in enumerate(winning_combos):
        match_cells = 0
        for idx, value in enumerate(val):
            if value in former_player_cells:
                match_cells += 1
        if match_cells == 3:
            return former_player
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == X or winner(board) == O:
        return True
    elif len(actions(board)) == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        if winner(board) == X:
            return 1
        elif winner(board) == O:
            return -1
        else:
            return 0
    else:
        return None


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    else:
        winning_action_sequence = []
        drawing_action_sequence = []
        losing_action_sequence = []
        if player(board) == O:
            for action in actions(board):
                current_utility = maxvalue(result(board, action))
                if current_utility == 1:
                    winning_action_sequence.append(action)
                elif current_utility == 0:
                    drawing_action_sequence.append(action)
                elif current_utility == -1:
                    losing_action_sequence.append(action)
            if len(losing_action_sequence) > 0:
                return losing_action_sequence[0]
            elif len(drawing_action_sequence) > 0:
                return drawing_action_sequence[0]
            elif len(winning_action_sequence) > 0:
                return winning_action_sequence[0]

        else:
            for action in actions(board):
                current_utility = minvalue(result(board, action))
                if current_utility == 1:
                    winning_action_sequence.append(action)
                elif current_utility == 0:
                    drawing_action_sequence.append(action)
                elif current_utility == -1:
                    losing_action_sequence.append(action)
            if len(winning_action_sequence) > 0:
                return winning_action_sequence[0]
            elif len(drawing_action_sequence) > 0:
                return drawing_action_sequence[0]
            elif len(losing_action_sequence) > 0:
                return losing_action_sequence[0]


def maxvalue(board):
    v = - math.inf
    if terminal(board):
        return utility(board)
    for action in actions(board):
        if v != 1:
            v = max(v, minvalue(result(board, action)))

    return v


def minvalue(board):
    v = math.inf
    if terminal(board):
        return utility(board)
    for action in actions(board):
        if v != -1:
            v = min(v, maxvalue(result(board, action)))

    return v
