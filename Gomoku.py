import math
import random
from copy import deepcopy

BOARD_SIZE = 15
WIN_LEN     = 5
EMPTY, BLACK, WHITE = 0, 1, 2
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def check_five(board, x, y, player) -> bool:
    for dx, dy in DIRECTIONS:
        cnt = 1
        for sign in (1, -1):
            nx, ny = x + dx * sign, y + dy * sign
            while in_bounds(nx, ny) and board[nx][ny] == player:
                cnt += 1
                nx += dx * sign
                ny += dy * sign
        if cnt >= WIN_LEN:
            return True
    return False

def game_over(board):
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            p = board[x][y]
            if p != EMPTY and check_five(board, x, y, p):
                return p
    if all(cell != EMPTY for row in board for cell in row):
        return 'draw'
    return None

def line_score(cnt: int, open_ends: int) -> int:
    if cnt >= WIN_LEN:
        return 100_000
    if cnt == 4:
        return 10_000 if open_ends == 2 else 1_000
    if cnt == 3:
        return 500 if open_ends == 2 else 100
    if cnt == 2:
        return 10 if open_ends == 2 else 2
    return 0

def evaluate_player(board, player) -> int:
    score = 0
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            for dx, dy in DIRECTIONS:
                cnt = 0
                open_ends = 0
                for i in range(WIN_LEN):
                    nx, ny = x + dx * i, y + dy * i
                    if not in_bounds(nx, ny):
                        cnt = -1
                        break
                    cell = board[nx][ny]
                    if cell == player:
                        cnt += 1
                    elif cell != EMPTY:
                        cnt = -1
                        break
                if cnt == -1:
                    continue
                bx, by = x - dx, y - dy
                ex, ey = x + dx * WIN_LEN, y + dy * WIN_LEN
                if in_bounds(bx, by) and board[bx][by] == EMPTY:
                    open_ends += 1
                if in_bounds(ex, ey) and board[ex][ey] == EMPTY:
                    open_ends += 1
                score += line_score(cnt, open_ends)
    return score

def evaluate(board, player) -> int:
    opponent = BLACK if player == WHITE else WHITE
    return evaluate_player(board, player) - evaluate_player(board, opponent)

def get_valid_moves(board):
    moves = set()
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] != EMPTY:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and board[nx][ny] == EMPTY:
                            moves.add((nx, ny))
    if not moves:
        moves.add((BOARD_SIZE // 2, BOARD_SIZE // 2))
    return list(moves)

def minimax(board, depth, alpha, beta, maximizing, player):
    winner = game_over(board)
    if winner == player:
        return None, 1_000_000
    if winner and winner != 'draw':
        return None, -1_000_000
    if winner == 'draw':
        return None, 0
    if depth == 0:
        return None, evaluate(board, player)

    best_move = None
    moves = get_valid_moves(board)
    moves.sort(key=lambda m: abs(m[0] - BOARD_SIZE // 2) + abs(m[1] - BOARD_SIZE // 2))

    if maximizing:
        value = -math.inf
        for x, y in moves:
            board[x][y] = player
            _, val = minimax(board, depth - 1, alpha, beta, False, player)
            board[x][y] = EMPTY
            if val > value:
                value, best_move = val, (x, y)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_move, value
    else:
        opponent = BLACK if player == WHITE else WHITE
        value = math.inf
        for x, y in moves:
            board[x][y] = opponent
            _, val = minimax(board, depth - 1, alpha, beta, True, player)
            board[x][y] = EMPTY
            if val < value:
                value, best_move = val, (x, y)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return best_move, value

def ai_move(board, player, depth=2):
    move, _ = minimax(board, depth, -math.inf, math.inf, True, player)
    return move or random.choice(get_valid_moves(board))

