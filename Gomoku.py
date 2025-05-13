import math
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
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
    """True if move at (x,y) completes a 5-in-a-row for <player>."""
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
    """Return BLACK / WHITE on win, 'draw' on full board, else None."""
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
                # Check the two ends
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
    """Return empty cells adjacent to at least one stone (for efficiency)."""
    moves = set()
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] != EMPTY:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and board[nx][ny] == EMPTY:
                            moves.add((nx, ny))
    if not moves:                                    # opening move → centre
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
    moves.sort(key=lambda m: abs(m[0] - BOARD_SIZE // 2) + abs(m[1] - BOARD_SIZE // 2))  # centre first

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

def ai_move(board, player, depth=2):  # depth is always fixed at 2
    move, _ = minimax(board, depth, -math.inf, math.inf, True, player)
    return move or random.choice(get_valid_moves(board))

class GomokuGUI:
    CELL   = 42
    MARGIN = 40
    RADIUS = CELL // 2 - 2

    def __init__(self, human_vs_ai: bool):
        self.human_vs_ai = human_vs_ai
        self.depth   = 2  # Fixed depth for AI moves
        self.board   = create_board()
        self.current = WHITE if human_vs_ai else BLACK   # human starts as White
        self.finished = False

        # Tk setup
        self.root = tk.Tk()
        self.root.title("Gomoku – Five in a Row")

        self.status = tk.Label(self.root, font=("Helvetica", 14, "bold"))
        self.status.pack(pady=4)

        side = self.MARGIN * 2 + self.CELL * (BOARD_SIZE - 1)
        self.canvas = tk.Canvas(self.root, width=side, height=side, bg="#deb887")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_grid()
        self.update_status()

        # If AI vs AI and Black starts, kick off first move
        if not self.human_vs_ai:
            self.root.after(400, self.ai_turn)

    def draw_grid(self):
        for i in range(BOARD_SIZE):
            pos = self.MARGIN + i * self.CELL
            self.canvas.create_line(self.MARGIN, pos,
                                    self.MARGIN + self.CELL * (BOARD_SIZE - 1), pos)
            self.canvas.create_line(pos, self.MARGIN,
                                    pos, self.MARGIN + self.CELL * (BOARD_SIZE - 1))

        for i in (3, 7, 11):
            for j in (3, 7, 11):
                cx = self.MARGIN + i * self.CELL
                cy = self.MARGIN + j * self.CELL
                self.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="black")

    def draw_stone(self, x, y, player):
        cx = self.MARGIN + y * self.CELL
        cy = self.MARGIN + x * self.CELL
        fill = "black" if player == BLACK else "white"
        outline = "white" if player == BLACK else "black"
        self.canvas.create_oval(cx - self.RADIUS, cy - self.RADIUS, cx + self.RADIUS, cy + self.RADIUS,fill=fill, outline=outline, width=2)

    def pixel_to_cell(self, px, py):
        col = round((px - self.MARGIN) / self.CELL)
        row = round((py - self.MARGIN) / self.CELL)
        if in_bounds(row, col):
            return row, col
        return None, None

    def on_click(self, event):
        if self.finished or not self.human_vs_ai or self.current != WHITE:
            return
        row, col = self.pixel_to_cell(event.x, event.y)
        if row is None or self.board[row][col] != EMPTY:
            return
        self.place_move(row, col)

    def place_move(self, x, y):
        self.board[x][y] = self.current
        self.draw_stone(x, y, self.current)

        winner = game_over(self.board)
        if winner:
            self.finished = True
            self.update_status(winner)
            return

        self.current = BLACK if self.current == WHITE else WHITE
        self.update_status()

        if self.finished:
            return
        if (self.human_vs_ai and self.current == BLACK) or (not self.human_vs_ai):
            self.root.after(200, self.ai_turn)

    def ai_turn(self):
        if self.finished:
            return
        move = ai_move(self.board, self.current, self.depth)
        if move:
            self.place_move(*move)

    def update_status(self, winner=None):
        if winner == 'draw':
            self.status.config(text="Draw!")
        elif winner == BLACK:
            self.status.config(text="Black wins!")
        elif winner == WHITE:
            self.status.config(text="White wins!")
        else:
            if self.human_vs_ai:
                if self.current == WHITE:
                    self.status.config(text="Your move (White)")
                else:
                    self.status.config(text="AI thinking… (Black)")
            else:
                self.status.config(text="AI vs AI – " +
                                   ("Black's move" if self.current == BLACK else "White's move"))

    def run(self):
        self.root.mainloop()

def main():
    root = tk.Tk()
    root.withdraw()

    mode = simpledialog.askstring("Choose mode",
                                  "Enter H for Human vs AI, A for AI vs AI:",
                                  parent=root)
    if not mode:
        return
    mode = mode.strip().lower()
    human_vs_ai = (mode != 'a')

    root.destroy()
    gui = GomokuGUI(human_vs_ai=human_vs_ai)
    gui.run()

if __name__ == "__main__":
    main()
