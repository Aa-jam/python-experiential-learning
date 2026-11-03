
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

# (symbol, colour) for up to 4 players
PLAYER_STYLES = [("X", CYAN), ("O", PINK), ("▲", YELLOW), ("■", GREEN)]

# players -> (board size, how many in a row to win)
BOARD_CONFIG = {2: (3, 3), 3: (5, 4), 4: (6, 4)}
CELL_PX = {3: 90, 5: 66, 6: 56}
CELL_FONT = {3: 32, 5: 22, 6: 18}
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


def lerp_color(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(
        int(a[k] + (b[k] - a[k]) * t) for k in range(3)
    )


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Multiplayer Edition")
        self.root.geometry("760x780")
        self.root.minsize(700, 720)
        self.root.configure(bg=BG)

        self.nplayers = tk.IntVar(value=2)
        self.difficulty = tk.StringVar(value="Medium")
        self.names = [tk.StringVar(value=f"Player {i + 1}") for i in range(4)]
        self.cpu = [tk.BooleanVar(value=False) for _ in range(4)]

        self.scores = [0] * 4
        self.draws = 0
        self.board = []
        self.buttons = []
        self.size = 3
        self.win_len = 3
        self.current = 0
        self.starter = 0
        self.game_over = False
        self.history = []
        self.ai_job = None
        self.round_id = 0
        self.turn_color = CYAN
        self.score_labels = []
        self.count_btns = {}

        self.build_ui()
        for var in self.names:
            var.trace_add("write", lambda *a: self.update_scores())

        self.apply_players()
        self.root.after(400, self.show_welcome)

    # ================= HELPERS =================
    def make_button(self, parent, text, bg, cmd, fg=BG,
                    font=("Arial", 11, "bold"), padx=14, pady=7):
        """Label-based button: colours work on Windows, Mac and Linux."""
        lbl = tk.Label(
            parent, text=text, bg=bg, fg=fg, font=font,
            padx=padx, pady=pady, cursor="hand2"
        )
        lbl.bind("<Button-1>", lambda e: cmd())
        return lbl

    def fade(self, widget, prop, c1, c2, steps=8, delay=25, i=0):
        """Smooth colour transition for any widget property."""
        try:
            widget.config(**{prop: lerp_color(c1, c2, i / steps)})
        except tk.TclError:
            return
        if i < steps:
            self.root.after(
                delay,
                lambda: self.fade(widget, prop, c1, c2, steps, delay, i + 1)
            )

    def is_cpu(self, i):
        return self.cpu[i].get()

    def get_name(self, i):
        name = self.names[i].get().strip() or f"Player {i + 1}"
        if self.is_cpu(i) and name == f"Player {i + 1}":
            name = f"CPU {i + 1}"
        return name

    # ================= INTERFACE =================
    def build_ui(self):
        tk.Label(
            self.root, text="✦ TIC TAC TOE ✦",
            font=("Arial", 26, "bold"), fg=CYAN, bg=BG
        ).pack(pady=(12, 0))

        tk.Label(
            self.root, text="MULTIPLAYER EDITION  •  2 TO 4 PLAYERS",
            font=("Arial", 10, "bold"), fg=YELLOW, bg=BG
        ).pack(pady=(0, 8))

        # Settings bar
        settings = tk.Frame(self.root, bg=PANEL)
        settings.pack(fill="x", padx=22, pady=4)

        tk.Label(
            settings, text="Players", fg=WHITE, bg=PANEL,
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=(12, 6), pady=8)

        for n in (2, 3, 4):
            b = self.make_button(
                settings, str(n), CELL_BG,
                lambda n=n: self.set_players(n),
                fg=WHITE, padx=12, pady=3
            )
            b.pack(side="left", padx=3)
            self.count_btns[n] = b
        self.refresh_count_buttons()

        tk.Label(
            settings, text="CPU Level", fg=WHITE, bg=PANEL,
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=(20, 6))

        tk.OptionMenu(
            settings, self.difficulty, "Easy", "Medium", "Hard",
            command=lambda _: self.new_round()
        ).pack(side="left")

        self.board_info = tk.Label(
            settings, text="", fg=YELLOW, bg=PANEL, font=("Arial", 10, "bold")
        )
        self.board_info.pack(side="right", padx=12)

        # Player rows (name + CPU toggle)
        self.players_frame = tk.Frame(self.root, bg=BG)
        self.players_frame.pack(pady=6)
        self.player_rows = []

        for i, (sym, col) in enumerate(PLAYER_STYLES):
            row = tk.Frame(self.players_frame, bg=BG)
            tk.Label(
                row, text=sym, font=("Arial", 14, "bold"),
                fg=col, bg=BG, width=2
            ).pack(side="left")
            tk.Entry(
                row, textvariable=self.names[i], width=15,
                bg=CELL_BG, fg=WHITE, insertbackground=WHITE, relief="flat"
            ).pack(side="left", padx=6, ipady=3)
            tk.Checkbutton(
                row, text="🤖 CPU", variable=self.cpu[i],
                command=self.new_round, fg=WHITE, bg=BG,
                selectcolor=CELL_BG, activebackground=BG,
                activeforeground=WHITE, cursor="hand2"
            ).pack(side="left")
            row.grid(row=i // 2, column=i % 2, padx=14, pady=3)
            self.player_rows.append(row)

        # Turn indicator
        self.turn_bar = tk.Frame(self.root, height=5, bg=CYAN)
        self.turn_bar.pack(fill="x", padx=60, pady=(8, 0))

        self.status = tk.Label(
            self.root, text="", font=("Arial", 15, "bold"),
            fg=YELLOW, bg=BG, wraplength=600
        )
        self.status.pack(pady=8)

        # Board
        self.board_frame = tk.Frame(self.root, bg=BG)
        self.board_frame.pack(pady=4)

        # Scoreboard
        self.score_frame = tk.Frame(self.root, bg=PANEL)
        self.score_frame.pack(fill="x", padx=25, pady=12)

        # Controls
        controls = tk.Frame(self.root, bg=BG)
        controls.pack(pady=4)

        for text, color, cmd in [
            ("↩ Undo", PURPLE, self.undo),
            ("🔄 New Round", GREEN, self.new_round),
            ("Reset Scores", PINK, self.confirm_reset),
            ("📖 Rules", YELLOW, self.show_rules),
        ]:
            self.make_button(controls, text, color, cmd).pack(
                side="left", padx=5
            )

    def set_players(self, n):
        self.nplayers.set(n)
        self.refresh_count_buttons()
        self.apply_players()

    def refresh_count_buttons(self):
        for n, b in self.count_btns.items():
            if n == self.nplayers.get():
                b.config(bg=PURPLE, fg=WHITE)
            else:
                b.config(bg=CELL_BG, fg=WHITE)

    def build_board(self):
        for w in self.board_frame.winfo_children():
            w.destroy()

        px = CELL_PX[self.size]
        self.buttons = []

        for i in range(self.size * self.size):
            cell = tk.Frame(self.board_frame, width=px, height=px, bg=BG)
            cell.grid(
                row=i // self.size, column=i % self.size, padx=3, pady=3
            )
            cell.pack_propagate(False)

            button = tk.Label(
                cell, text="", font=("Arial", CELL_FONT[self.size], "bold"),
                bg=PANEL, fg=WHITE, cursor="hand2"
            )
            button.pack(fill="both", expand=True)
            button.bind("<Button-1>", lambda e, p=i: self.player_move(p))
            self.buttons.append(button)

            # Cells light up one by one (intro transition)
            self.root.after(
                12 * i,
                lambda b=button: self.fade(b, "bg", PURPLE, CELL_BG, 6, 30)
            )

    def rebuild_scoreboard(self):
        for w in self.score_frame.winfo_children():
            w.destroy()

        self.score_labels = []
        for i in range(self.nplayers.get()):
            lbl = tk.Label(
                self.score_frame, font=("Arial", 11, "bold"),
                fg=PLAYER_STYLES[i][1], bg=PANEL
            )
            lbl.pack(side="left", expand=True, pady=10)
            self.score_labels.append(lbl)

        self.draw_label = tk.Label(
            self.score_frame, font=("Arial", 11, "bold"),
            fg=WHITE, bg=PANEL
        )
        self.draw_label.pack(side="left", expand=True, pady=10)

    # ================= SETUP / ROUNDS =================
    def apply_players(self):
        n = self.nplayers.get()

        for i, row in enumerate(self.player_rows):
            if i < n:
                row.grid()
            else:
                row.grid_remove()

        self.scores = [0] * 4
        self.draws = 0
        self.starter = 0
        self.rebuild_scoreboard()
        self.new_round()

    def new_round(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        n = self.nplayers.get()
        self.size, self.win_len = BOARD_CONFIG[n]
        self.board = [None] * (self.size * self.size)
        self.current = self.starter % n
        self.game_over = False
        self.history = []
        self.round_id += 1

        self.board_info.config(
            text=f"{self.size}×{self.size} board • {self.win_len} in a row"
        )

        self.build_board()
        self.update_board()
        self.update_status()
        self.update_scores()
        self.maybe_cpu_turn()

    def update_board(self):
        for i, button in enumerate(self.buttons):
            owner = self.board[i]

            if owner is None:
                text, col = "", WHITE
            else:
                text, col = PLAYER_STYLES[owner]

            locked = (
                self.game_over or owner is not None
                or self.is_cpu(self.current)
            )

            button.config(
                text=text, fg=col,
                cursor="arrow" if locked else "hand2"
            )

    def update_status(self):
        if self.game_over:
            return

        sym, col = PLAYER_STYLES[self.current]
        name = self.get_name(self.current)

        if self.is_cpu(self.current):
            text = f"🤖 {name} ({sym}) is thinking..."
        else:
            text = f"✨ {name} ({sym}) — your turn!"

        self.status.config(text=text)
        self.fade(self.status, "fg", self.turn_color, col)
        self.fade(self.turn_bar, "bg", self.turn_color, col)
        self.turn_color = col

    def update_scores(self):
        if len(self.score_labels) != self.nplayers.get():
            return

        for i, lbl in enumerate(self.score_labels):
            lbl.config(
                text=f"{PLAYER_STYLES[i][0]} {self.get_name(i)[:10]}\n"
                     f"{self.scores[i]}"
            )
        self.draw_label.config(text=f"🤝 Draws\n{self.draws}")

    # ================= GAME LOGIC =================
    def runs(self, pos, player):
        """Return the connected cells through pos in all 4 directions."""
        n = self.size
        r, c = divmod(pos, n)
        result = []

        for dr, dc in DIRECTIONS:
            cells = [pos]
            for sign in (1, -1):
                rr, cc = r + dr * sign, c + dc * sign
                while (
                    0 <= rr < n and 0 <= cc < n
                    and self.board[rr * n + cc] == player
                ):
                    cells.append(rr * n + cc)
                    rr += dr * sign
                    cc += dc * sign
            result.append(cells)

        return result

    def get_line(self, pos, player):
        for cells in self.runs(pos, player):
            if len(cells) >= self.win_len:
                return cells
        return None

    def player_move(self, position):
        if self.game_over or self.is_cpu(self.current):
            return
        if self.board[position] is not None:
            return
        self.make_move(position)

    def make_move(self, position):
        n = self.nplayers.get()
        self.history.append((position, self.current))
        self.board[position] = self.current
        self.animate_move(position)

        line = self.get_line(position, self.current)
        if line:
            self.finish_game(self.current, line)
            return

        if None not in self.board:
            self.finish_draw()
            return

        self.current = (self.current + 1) % n
        self.update_board()
        self.update_status()
        self.maybe_cpu_turn()

    def maybe_cpu_turn(self):
        if not self.game_over and self.is_cpu(self.current):
            self.ai_job = self.root.after(600, self.computer_turn)

    # ================= ANIMATIONS =================
    def animate_move(self, position):
        button = self.buttons[position]
        sym, col = PLAYER_STYLES[self.board[position]]

        button.config(text=sym, fg=col, font=("Arial", 10, "bold"))

        full = CELL_FONT[self.size]
        sizes = [int(full * f) for f in (0.5, 0.75, 1.0, 1.25, 1.0)]

        def grow(step=0):
            if step < len(sizes):
                try:
                    button.config(font=("Arial", sizes[step], "bold"))
                except tk.TclError:
                    return
                self.root.after(40, lambda: grow(step + 1))

        grow()
        self.fade(button, "bg", col, CELL_BG, 8, 30)

    def animate_winner(self, cells, step=0):
        try:
            if step >= 10:
                for p in cells:
                    self.buttons[p].config(bg="#1D6B55")
                return

            color = GREEN if step % 2 == 0 else "#174C49"
            for p in cells:
                self.buttons[p].config(bg=color)
        except tk.TclError:
            return

        self.root.after(160, lambda: self.animate_winner(cells, step + 1))

    # ================= COMPUTER AI =================
    def computer_turn(self):
        self.ai_job = None

        if self.game_over or not self.is_cpu(self.current):
            return

        self.make_move(self.choose_computer_move())

    def choose_computer_move(self):
        me = self.current
        n = self.nplayers.get()
        empty = [i for i, v in enumerate(self.board) if v is None]
        level = self.difficulty.get()

        if level == "Easy":
            return random.choice(empty)

        # 1) Win if possible
        for p in empty:
            self.board[p] = me
            line = self.get_line(p, me)
            self.board[p] = None
            if line:
                return p

        # 2) Block any opponent's winning move
        for p in empty:
            for other in range(n):
                if other == me:
                    continue
                self.board[p] = other
                line = self.get_line(p, other)
                self.board[p] = None
                if line:
                    return p

        # 3) Perfect play for the classic 2-player 3x3 game on Hard
        if level == "Hard" and n == 2 and self.size == 3:
            if len(empty) == 9:
                return random.choice([0, 2, 4, 6, 8])

            best_score, best_move = -float("inf"), empty[0]
            for p in empty:
                self.board[p] = me
                score = self.minimax(p, me, 1 - me, me, 1)
                self.board[p] = None
                if score > best_score:
                    best_score, best_move = score, p
            return best_move

        # 4) Heuristic scoring (Medium has more randomness)
        noise = 6.0 if level == "Medium" else 0.5
        centre = (self.size - 1) / 2
        best_score, best_move = -float("inf"), empty[0]

        for p in empty:
            self.board[p] = me
            mine = max(len(c) for c in self.runs(p, me))
            self.board[p] = None
            score = mine ** 2 * 4

            for other in range(n):
                if other == me:
                    continue
                self.board[p] = other
                theirs = max(len(c) for c in self.runs(p, other))
                self.board[p] = None
                score += theirs ** 2 * 3

            r, c = divmod(p, self.size)
            score -= abs(r - centre) + abs(c - centre)
            score += random.random() * noise

            if score > best_score:
                best_score, best_move = score, p

        return best_move

    def minimax(self, last_pos, last_player, to_move, me, depth):
        if self.get_line(last_pos, last_player):
            return 10 - depth if last_player == me else depth - 10

        if None not in self.board:
            return 0

        scores = []
        for p in range(len(self.board)):
            if self.board[p] is None:
                self.board[p] = to_move
                scores.append(
                    self.minimax(p, to_move, 1 - to_move, me, depth + 1)
                )
                self.board[p] = None

        return max(scores) if to_move == me else min(scores)

    # ================= WIN / DRAW =================
    def finish_game(self, winner, line):
        self.game_over = True
        self.scores[winner] += 1
        self.starter = (self.starter + 1) % self.nplayers.get()

        sym, col = PLAYER_STYLES[winner]
        self.status.config(
            text=f"🎉 {self.get_name(winner)} ({sym}) wins!", fg=GREEN
        )
        self.fade(self.turn_bar, "bg", self.turn_color, GREEN)
        self.turn_color = GREEN

        self.update_board()
        self.update_scores()
        self.animate_winner(line)

        rid = self.round_id
        self.root.after(1500, lambda: self.show_result(winner, rid))

    def finish_draw(self):
        self.game_over = True
        self.draws += 1
        self.starter = (self.starter + 1) % self.nplayers.get()

        self.status.config(text="🤝 It's a draw!", fg=YELLOW)
        self.fade(self.turn_bar, "bg", self.turn_color, YELLOW)
        self.turn_color = YELLOW

        self.update_board()
        self.update_scores()

        rid = self.round_id
        self.root.after(700, lambda: self.show_draw(rid))

    # ================= UNDO =================
    def undo(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        if self.game_over:
            self.status.config(
                text="Round is over — start a new round!", fg=YELLOW
            )
            return

        if not self.history:
            self.status.config(text="Nothing to undo!", fg=YELLOW)
            self.root.after(1200, self.update_status)
            return

        # Remove moves until a human player's move has been undone
        while self.history:
            pos, player = self.history.pop()
            self.board[pos] = None
            self.buttons[pos].config(text="", bg=CELL_BG)
            self.current = player
            if not self.is_cpu(player):
                break

        self.update_board()
        self.update_status()
        self.maybe_cpu_turn()

    # ================= RESET =================
    def confirm_reset(self):
        self.show_popup(
            "⚠️", "Reset Scores?",
            "All scores will be set back to zero.\nThis cannot be undone.",
            PINK,
            [("Yes, reset", self.do_reset, PINK),
             ("Cancel", None, CYAN)]
        )

    def do_reset(self):
        self.scores = [0] * 4
        self.draws = 0
        self.starter = 0
        self.new_round()

    # ================= POPUPS =================
    def show_welcome(self):
        self.show_popup(
            "🎮", "Welcome!",
            "Choose 2, 3 or 4 players.\nAny player can be a CPU 🤖\n\n"
            "More players = bigger board!",
            CYAN, [("Let's Play!", None, GREEN)]
        )

    def show_rules(self):
        n = self.nplayers.get()
        size, win = BOARD_CONFIG[n]
        self.show_popup(
            "📖", "Rules",
            f"{n} players  →  {size}×{size} board\n"
            f"Get {win} symbols in a row (horizontal,\n"
            f"vertical or diagonal) to win the round.\n\n"
            f"Starting player rotates every round.",
            YELLOW, [("Got it", None, GREEN)]
        )

    def show_result(self, winner, rid):
        if rid != self.round_id:
            return

        sym, col = PLAYER_STYLES[winner]
        board = "   |   ".join(
            f"{PLAYER_STYLES[i][0]} {self.scores[i]}"
            for i in range(self.nplayers.get())
        )
        self.show_popup(
            "🏆", "We Have a Winner!",
            f"{self.get_name(winner)} ({sym}) wins this round!\n\n"
            f"Scores:  {board}",
            col,
            [("▶ Next Round", self.new_round, GREEN),
             ("Close", None, PINK)],
            confetti=True
        )

    def show_draw(self, rid):
        if rid != self.round_id:
            return

        self.show_popup(
            "🤝", "It's a Draw!",
            "The board is full and nobody won.\nReady for another go?",
            YELLOW,
            [("▶ Next Round", self.new_round, GREEN),
             ("Close", None, PINK)]
        )

    def show_popup(self, emoji, title, message, color, buttons,
                   confetti=False):
        top = tk.Toplevel(self.root)
        top.title(title)
        top.configure(bg=color)
        top.resizable(False, False)
        top.protocol("WM_DELETE_WINDOW", lambda: self.fade_out(top))
        top.closing = False
        try:
            top.attributes("-alpha", 0.0)
            top.attributes("-topmost", True)
        except tk.TclError:
            pass

        inner = tk.Frame(top, bg=PANEL)
        inner.pack(padx=3, pady=3)

        canvas = tk.Canvas(
            inner, width=400, height=130, bg=PANEL, highlightthickness=0
        )
        canvas.pack()
        canvas.create_text(200, 42, text=emoji, font=("Arial", 38))
        canvas.create_text(
            200, 100, text=title, font=("Arial", 20, "bold"), fill=color
        )

        tk.Label(
            inner, text=message, font=("Arial", 12), fg=WHITE, bg=PANEL,
            wraplength=360, justify="center"
        ).pack(padx=20, pady=(4, 14))

        row = tk.Frame(inner, bg=PANEL)
        row.pack(pady=(0, 18))

        for text, cmd, bg_color in buttons:
            self.make_button(
                row, text, bg_color,
                lambda c=cmd: self.fade_out(top, c),
                padx=16, pady=7
            ).pack(side="left", padx=6)

        top.update_idletasks()
        w, h = top.winfo_reqwidth(), top.winfo_reqheight()
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2

        top.geometry(f"+{x}+{y + 50}")
        top.lift()
        top.focus_force()
        self.animate_popup_in(top, x, y)

        try:
            top.wait_visibility()
            top.grab_set()
        except tk.TclError:
            pass

        if confetti:
            self.start_confetti(canvas, [CYAN, PINK, YELLOW, GREEN, PURPLE])

    def animate_popup_in(self, top, x, y, step=0, steps=10):
        t = (step + 1) / steps
        ease = 1 - (1 - t) ** 3  # ease-out slide + fade

        try:
            top.geometry(f"+{x}+{y + int(50 * (1 - ease))}")
            top.attributes("-alpha", ease)
        except tk.TclError:
            return

        if step + 1 < steps:
            self.root.after(
                20, lambda: self.animate_popup_in(top, x, y, step + 1, steps)
            )

    def fade_out(self, top, cmd=None, step=0, steps=6):
        if step == 0:
            if getattr(top, "closing", False):
                return
            top.closing = True

        try:
            top.attributes("-alpha", 1 - (step + 1) / steps)
        except tk.TclError:
            pass

        if step + 1 < steps:
            self.root.after(
                18, lambda: self.fade_out(top, cmd, step + 1, steps)
            )
        else:
            try:
                top.grab_release()
            except tk.TclError:
                pass
            try:
                top.destroy()
            except tk.TclError:
                pass
            if cmd:
                cmd()

    def start_confetti(self, canvas, colors):
        parts = []
        for _ in range(45):
            x = random.randint(5, 395)
            y = random.randint(-120, 0)
            s = random.randint(4, 8)
            item = canvas.create_rectangle(
                x, y, x + s, y + s, fill=random.choice(colors), outline=""
            )
            parts.append((item, random.uniform(2, 5), random.uniform(-1, 1)))

        def tick():
            try:
                for item, vy, vx in parts:
                    canvas.move(item, vx, vy)
                    if canvas.coords(item)[1] > 130:
                        canvas.move(item, 0, -150)
                canvas.after(30, tick)
            except tk.TclError:
                return

        tick()


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()