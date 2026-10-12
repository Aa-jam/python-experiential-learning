
import tkinter as tk
import random

# ---------- COLOURS ----------
BG = "#09152F"
PANEL = "#122447"
CELL_BG = "#1B3157"
CYAN = "#28D7FF"
PINK = "#FF5C93"
YELLOW = "#FFE66D"
GREEN = "#20E3A2"
WHITE = "#F4F7FF"
PURPLE = "#9B6BFF"

WINNING_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Tic Tac Toe - Phase 3")
        self.root.geometry("760x850")
        self.root.minsize(580, 700)
        self.root.configure(bg=BG)

        self.board = [" "] * 9
        self.current = "X"
        self.game_over = False
        self.mode = "Player vs Computer"
        self.difficulty = tk.StringVar(value="Medium")

        self.name_x = tk.StringVar(value="Player X")
        self.name_o = tk.StringVar(value="Player O")

        self.scores = {"X": 0, "O": 0, "Draws": 0}
        self.history = []
        self.ai_job = None
        self.winning_cells = []

        self.build_ui()
        self.new_round()

    # ---------- INTERFACE ----------
    def build_ui(self):
        tk.Label(
            self.root,
            text="✦ TIC TAC TOE ✦",
            font=("Arial", 29, "bold"),
            fg=CYAN, bg=BG
        ).pack(pady=(18, 3))

        tk.Label(
            self.root,
            text="ENHANCED EDITION  •  PHASE 3",
            font=("Arial", 11, "bold"),
            fg=YELLOW, bg=BG
        ).pack(pady=(0, 15))

        settings = tk.Frame(self.root, bg=PANEL)
        settings.pack(fill="x", padx=22, pady=5)

        tk.Label(
            settings, text="Game Mode", fg=WHITE, bg=PANEL,
            font=("Arial", 11, "bold")
        ).grid(row=0, column=0, padx=8, pady=10)

        self.mode_box = tk.StringVar(value="Player vs Computer")

        tk.OptionMenu(
            settings, self.mode_box,
            "Player vs Player", "Player vs Computer",
            command=self.change_mode
        ).grid(row=0, column=1, padx=5, pady=8)

        tk.Label(
            settings, text="Difficulty", fg=WHITE, bg=PANEL
        ).grid(row=0, column=2, padx=8)

        self.difficulty_box = tk.OptionMenu(
            settings, self.difficulty,
            "Easy", "Medium", "Hard",
            command=lambda _: self.new_round()
        )
        self.difficulty_box.grid(row=0, column=3, padx=5)

        names = tk.Frame(self.root, bg=BG)
        names.pack(pady=7)

        tk.Label(
            names, text="X Name:", fg=CYAN, bg=BG
        ).grid(row=0, column=0, padx=5)

        tk.Entry(
            names, textvariable=self.name_x, width=13,
            bg=CELL_BG, fg=WHITE, insertbackground=WHITE
        ).grid(row=0, column=1, padx=5)

        self.o_label = tk.Label(
            names, text="O Name:", fg=PINK, bg=BG
        )
        self.o_label.grid(row=0, column=2, padx=5)

        self.o_entry = tk.Entry(
            names, textvariable=self.name_o, width=13,
            bg=CELL_BG, fg=WHITE, insertbackground=WHITE
        )
        self.o_entry.grid(row=0, column=3, padx=5)

        self.status = tk.Label(
            self.root, text="", font=("Arial", 15, "bold"),
            fg=YELLOW, bg=BG, wraplength=550
        )
        self.status.pack(pady=14)

        # Game board
        board_frame = tk.Frame(self.root, bg=BG)
        board_frame.pack(pady=5)

        self.buttons = []

        for i in range(9):
            button = tk.Button(
                board_frame,
                text="",
                font=("Arial", 35, "bold"),
                width=4, height=1,
                bg=CELL_BG, fg=WHITE,
                activebackground="#294775",
                relief="flat",
                bd=0,
                command=lambda pos=i: self.player_move(pos)
            )

            button.grid(
                row=i // 3, column=i % 3,
                padx=5, pady=5, ipadx=5, ipady=5
            )

            self.buttons.append(button)

        # Scoreboard
        score_frame = tk.Frame(self.root, bg=PANEL)
        score_frame.pack(fill="x", padx=25, pady=14)

        self.score_labels = {}

        for key, color in [
            ("X", CYAN), ("O", PINK), ("Draws", YELLOW)
        ]:
            label = tk.Label(
                score_frame,
                text="",
                font=("Arial", 12, "bold"),
                fg=color, bg=PANEL
            )
            label.pack(side="left", expand=True, pady=12)
            self.score_labels[key] = label

        # Controls
        controls = tk.Frame(self.root, bg=BG)
        controls.pack(pady=6)

        tk.Button(
            controls, text="↩ Undo",
            bg=PURPLE, fg=WHITE, font=("Arial", 11, "bold"),
            relief="flat", padx=15, pady=8,
            command=self.undo
        ).pack(side="left", padx=6)

        tk.Button(
            controls, text="🔄 New Round",
            bg=GREEN, fg=BG, font=("Arial", 11, "bold"),
            relief="flat", padx=15, pady=8,
            command=self.new_round
        ).pack(side="left", padx=6)

        tk.Button(
            controls, text="Reset Scores",
            bg=PINK, fg=WHITE, font=("Arial", 11, "bold"),
            relief="flat", padx=15, pady=8,
            command=self.reset_scores
        ).pack(side="left", padx=6)

        tk.Label(
            self.root,
            text="✨ Play Smart • Think Ahead • Have Fun ✨",
            fg=CYAN, bg=BG, font=("Arial", 12, "italic")
        ).pack(pady=12)

    # ---------- PLAYER NAMES ----------
    def get_name(self, player):
        if player == "X":
            return self.name_x.get().strip() or "Player X"

        if self.mode == "Player vs Computer":
            return "Computer"

        return self.name_o.get().strip() or "Player O"

    def change_mode(self, choice):
        self.mode = choice

        if choice == "Player vs Computer":
            self.o_label.grid_remove()
            self.o_entry.grid_remove()
            self.difficulty_box.config(state="normal")
        else:
            self.o_label.grid()
            self.o_entry.grid()
            self.difficulty_box.config(state="disabled")

        self.new_round()

    # ---------- GAME LOGIC ----------
    def get_winner(self, board=None):
        board = board if board is not None else self.board

        for combo in WINNING_COMBINATIONS:
            a, b, c = combo

            if board[a] == board[b] == board[c] != " ":
                return board[a], combo

        return None

    def player_move(self, position):
        if self.game_over:
            return

        if self.mode == "Player vs Computer" and self.current == "O":
            return

        if self.board[position] != " ":
            return

        self.make_move(position)

    def make_move(self, position):
        # Save the previous board for undo
        self.history.append(
            (self.board.copy(), self.current)
        )

        self.board[position] = self.current
        self.animate_move(position)

        result = self.get_winner()

        if result:
            self.finish_game(result[0], result[1])
            return

        if " " not in self.board:
            self.game_over = True
            self.scores["Draws"] += 1
            self.status.config(
                text="🤝 It's a draw!", fg=YELLOW
            )
            self.update_scores()
            self.update_board()
            return

        self.current = "O" if self.current == "X" else "X"
        self.update_status()
        self.update_board()

        if (
            self.mode == "Player vs Computer"
            and self.current == "O"
        ):
            self.status.config(
                text="🤖 Computer is thinking...", fg=PURPLE
            )

            self.ai_job = self.root.after(
                500, self.computer_turn
            )

    # ---------- ANIMATIONS ----------
    def animate_move(self, position):
        button = self.buttons[position]
        symbol = self.board[position]

        button.config(
            text=symbol,
            fg=CYAN if symbol == "X" else PINK,
            font=("Arial", 10, "bold")
        )

        # Grow the symbol in stages
        sizes = [18, 26, 34, 40]

        def grow(step=0):
            if step < len(sizes):
                button.config(
                    font=("Arial", sizes[step], "bold")
                )
                self.root.after(
                    45, lambda: grow(step + 1)
                )

        grow()

    def animate_winner(self, combo, step=0):
        if step >= 6:
            return

        color = GREEN if step % 2 == 0 else YELLOW

        for position in combo:
            self.buttons[position].config(
                bg=color if step % 2 == 0 else "#174C49"
            )

        self.root.after(
            180, lambda: self.animate_winner(combo, step + 1)
        )

    # ---------- COMPUTER AI ----------
    def computer_turn(self):
        self.ai_job = None

        if self.game_over or self.current != "O":
            return

        position = self.choose_computer_move()
        self.make_move(position)

    def choose_computer_move(self):
        empty = [
            i for i in range(9)
            if self.board[i] == " "
        ]

        difficulty = self.difficulty.get()

        if difficulty == "Easy":
            return random.choice(empty)

        # First try to win, then block X
        for symbol in ["O", "X"]:
            for position in empty:
                self.board[position] = symbol
                result = self.get_winner()
                self.board[position] = " "

                if result and result[0] == symbol:
                    return position

        if difficulty == "Medium":
            if self.board[4] == " ":
                return 4

            corners = [
                i for i in [0, 2, 6, 8]
                if self.board[i] == " "
            ]

            if corners:
                return random.choice(corners)

            return random.choice(empty)

        # Hard difficulty uses Minimax
        best_score = -float("inf")
        best_move = empty[0]

        for position in empty:
            self.board[position] = "O"
            score = self.minimax(False, 0)
            self.board[position] = " "

            if score > best_score:
                best_score = score
                best_move = position

        return best_move

    def minimax(self, maximizing, depth):
        result = self.get_winner()

        if result:
            if result[0] == "O":
                return 10 - depth
            return depth - 10

        if " " not in self.board:
            return 0

        if maximizing:
            best = -float("inf")

            for i in range(9):
                if self.board[i] == " ":
                    self.board[i] = "O"
                    score = self.minimax(False, depth + 1)
                    self.board[i] = " "
                    best = max(best, score)

            return best

        best = float("inf")

        for i in range(9):
            if self.board[i] == " ":
                self.board[i] = "X"
                score = self.minimax(True, depth + 1)
                self.board[i] = " "
                best = min(best, score)

        return best

    # ---------- WINNER / DRAW ----------
    def finish_game(self, winner, combo):
        self.game_over = True
        self.scores[winner] += 1

        if winner == "O" and self.mode == "Player vs Computer":
            message = "🤖 Computer wins!"
        else:
            message = f"🎉 {self.get_name(winner)} wins!"

        self.status.config(text=message, fg=GREEN)

        self.update_board()
        self.update_scores()
        self.animate_winner(combo)

    # ---------- UNDO ----------
    def undo(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        if not self.history:
            self.status.config(
                text="Nothing to undo!", fg=YELLOW
            )
            return

        # Undo the last move in PvP.
        # In PvC, undo both the computer and human moves
        # when the computer has already responded.
        count = 1

        if self.mode == "Player vs Computer":
            if self.current == "X" and len(self.history) >= 2:
                count = 2

        for _ in range(min(count, len(self.history))):
            old_board, old_player = self.history.pop()
            self.board = old_board
            self.current = old_player

        self.game_over = False
        self.update_board()
        self.update_status()

    # ---------- NEW ROUND ----------
    def new_round(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        self.board = [" "] * 9
        self.current = "X"
        self.game_over = False
        self.history = []
        self.winning_cells = []

        for button in self.buttons:
            button.config(
                text="", bg=CELL_BG, fg=WHITE,
                font=("Arial", 35, "bold"),
                state="normal"
            )

        self.update_status()
        self.update_scores()

    def update_board(self):
        for i, button in enumerate(self.buttons):
            symbol = self.board[i]

            button.config(
                text="" if symbol == " " else symbol,
                fg=(
                    CYAN if symbol == "X"
                    else PINK if symbol == "O"
                    else WHITE
                ),
                state=(
                    "disabled"
                    if self.game_over or symbol != " "
                    or (
                        self.mode == "Player vs Computer"
                        and self.current == "O"
                    )
                    else "normal"
                )
            )

    def update_status(self):
        if not self.game_over:
            self.status.config(
                text=f"✨ {self.get_name(self.current)}'s turn!",
                fg=CYAN if self.current == "X" else PINK
            )

    def update_scores(self):
        self.score_labels["X"].config(
            text=f"❌ {self.get_name('X')}: {self.scores['X']}"
        )
        self.score_labels["O"].config(
            text=f"⭕ {self.get_name('O')}: {self.scores['O']}"
        )
        self.score_labels["Draws"].config(
            text=f"🤝 Draws: {self.scores['Draws']}"
        )

    def reset_scores(self):
        self.scores = {"X": 0, "O": 0, "Draws": 0}
        self.update_scores()
        self.new_round()


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
