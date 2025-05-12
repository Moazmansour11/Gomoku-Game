import sys
import math
import random
from copy import deepcopy

# -----------------------------
# Game constants
# -----------------------------
EMPTY = 0
BLACK = 1   # AI by default
WHITE = 2   # Human or second AI

BOARD_SIZE = 15
WIN_LEN = 5

DIRECTIONS = [
    (1, 0),  # horizontal
    (0, 1),  # vertical
    (1, 1),  # diag down-right
    (1, -1)  # diag up-right
]

# -----------------------------
# Board handling
# -----------------------------
def create_board():
    '''Return empty board'''
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def in_bounds(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def print_board(board):
    header = '   ' + ' '.join(f'{i:2d}' for i in range(BOARD_SIZE))
    print(header)
    for i,row in enumerate(board):
        line = f'{i:2d} ' + ' '.join({EMPTY:'.', BLACK:'X', WHITE:'O'}[cell] for cell in row)
        print(line)
    print()

def get_valid_moves(board):
    '''Return list of (x,y) empty cells adjacent to existing stones, to narrow search.'''
    moves = set()
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] != EMPTY:
                for dx in (-1,0,1):
                    for dy in (-1,0,1):
                        nx, ny = x+dx, y+dy
                        if in_bounds(nx, ny) and board[nx][ny] == EMPTY:
                            moves.add((nx, ny))
    if not moves:  # board empty
        moves.add((BOARD_SIZE//2, BOARD_SIZE//2))
    return list(moves)

def check_five(board, x, y, player):
    for dx,dy in DIRECTIONS:
        count=1
        for step in (1,-1):
            nx, ny = x+dx*step, y+dy*step
            while in_bounds(nx,ny) and board[nx][ny]==player:
                count +=1
                nx += dx*step
                ny += dy*step
        if count >= WIN_LEN:
            return True
    return False

def game_over(board):
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y]!=EMPTY and check_five(board,x,y,board[x][y]):
                return board[x][y]
    if all(cell!=EMPTY for row in board for cell in row):
        return 'draw'
    return None

# -----------------------------
# Evaluation
# -----------------------------

def line_score(count, open_ends):
    '''assign heuristic scores'''
    if count>=WIN_LEN:
        return 100000
    if count==4:
        if open_ends==2:
            return 10000
        if open_ends==1:
            return 1000
    if count==3:
        if open_ends==2:
            return 500
        if open_ends==1:
            return 100
    if count==2:
        return 10 if open_ends==2 else 2
    return 0

def evaluate(board, player):
    opponent = BLACK if player==WHITE else WHITE
    return evaluate_player(board, player) - evaluate_player(board, opponent)

def evaluate_player(board, player):
    score=0
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            for dx,dy in DIRECTIONS:
                count=0
                open_ends=0
                for i in range(WIN_LEN):
                    nx,ny = x+dx*i, y+dy*i
                    if not in_bounds(nx,ny):
                        count=-1
                        break
                    cell = board[nx][ny]
                    if cell==player:
                        count+=1
                    elif cell!=EMPTY:
                        count=-1
                        break
                if count==-1:
                    continue
                # check ends
                bx,by = x-dx, y-dy
                if in_bounds(bx,by) and board[bx][by]==EMPTY:
                    open_ends +=1
                ex,ey = x+dx*WIN_LEN, y+dy*WIN_LEN
                if in_bounds(ex,ey) and board[ex][ey]==EMPTY:
                    open_ends +=1
                score += line_score(count, open_ends)
    return score

# -----------------------------
# Minimax with alpha-beta
# -----------------------------

def minimax(board, depth, alpha, beta, maximizing, player):
    winner = game_over(board)
    if winner==player:
        return None, 1000000
    elif winner and winner!='draw':
        return None, -1000000
    elif winner=='draw':
        return None, 0
    if depth==0:
        return None, evaluate(board, player)

    best_move = None
    moves = get_valid_moves(board)
    # Simple move ordering: center first
    moves.sort(key=lambda m: (abs(m[0]-BOARD_SIZE//2)+abs(m[1]-BOARD_SIZE//2)))
    if maximizing:
        value=-math.inf
        for move in moves:
            x,y=move
            board[x][y]=player
            _,score=minimax(board, depth-1, alpha, beta, False, player)
            board[x][y]=EMPTY
            if score>value:
                value=score
                best_move=move
            alpha=max(alpha,value)
            if alpha>=beta:
                break
        return best_move,value
    else:
        opponent = BLACK if player==WHITE else WHITE
        value=math.inf
        for move in moves:
            x,y=move
            board[x][y]=opponent
            _,score=minimax(board, depth-1, alpha, beta, True, player)
            board[x][y]=EMPTY
            if score<value:
                value=score
                best_move=move
            beta=min(beta,value)
            if beta<=alpha:
                break
        return best_move,value

def ai_move(board, player, depth=3):
    move,_=minimax(board, depth, -math.inf, math.inf, True, player)
    if move is None:
        move=random.choice(get_valid_moves(board))
    return move

# -----------------------------
# CLI Game loop
# -----------------------------

def human_turn(board):
    while True:
        try:
            raw=input("Enter your move as row col (e.g., 7 7): ")
            x,y = map(int, raw.strip().split())
            if in_bounds(x,y) and board[x][y]==EMPTY:
                return x,y
            else:
                print("Invalid move, try again.")
        except Exception:
            print("Format error, try again.")

def play(human_vs_ai=True, depth=3):
    board=create_board()
    current=BLACK  # Black starts
    human_color=WHITE if human_vs_ai else None
    while True:
        print_board(board)
        if current==human_color:
            x,y=human_turn(board)
        else:
            print("AI thinking...")
            x,y = ai_move(board, current, depth)
            print(f"AI plays {x} {y}")
        board[x][y]=current
        winner=game_over(board)
        if winner:
            print_board(board)
            if winner=='draw':
                print("Game drawn!")
            else:
                print("Black" if winner==BLACK else "White","wins!")
            break
        current = BLACK if current==WHITE else WHITE

def main():
    print("Gomoku Solver - Human vs AI (H) or AI vs AI (A)?")
    mode=input("Choose (H/A): ").strip().lower()
    depth = int(input("Search depth (default 3): ") or "3")
    if mode=='h':
        play(True, depth)
    else:
        play(False, depth)

if __name__ == "__main__":
    main()
