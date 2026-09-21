WINNING_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

def display_board(board):
    print("\n")
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print()

def check_winner(board):
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

def board_full(board):
    return all(cell != " " for cell in board)

def get_move(board, player):
    while True:
        try:
            position = int(input(f"Player {player}, choose a position (1-9): "))
            if position < 1 or position > 9:
                print("Invalid position. Enter a number from 1 to 9.")
            elif board[position - 1] != " ":
                print("That position is already occupied.")
            else:
                return position - 1
        except ValueError:
            print("Please enter a valid number.")

def computer_move(board):
    # Try to win
    for a, b, c in WINNING_COMBINATIONS:
        line = [board[a], board[b], board[c]]
        if line.count("O") == 2 and line.count(" ") == 1:
            return [a, b, c][line.index(" ")]

    # Try to block X
    for a, b, c in WINNING_COMBINATIONS:
        line = [board[a], board[b], board[c]]
        if line.count("X") == 2 and line.count(" ") == 1:
            return [a, b, c][line.index(" ")]

    # Take center
    if board[4] == " ":
        return 4

    # Take a corner
    for position in [0, 2, 6, 8]:
        if board[position] == " ":
            return position

    # Take any remaining position
    for position in range(9):
        if board[position] == " ":
            return position

def play_game(mode, score):
    board = [" "] * 9
    current_player = "X"

    while True:
        display_board(board)

        if mode == 2 and current_player == "O":
            move = computer_move(board)
            print(f"Computer chooses position {move + 1}")
        else:
            move = get_move(board, current_player)

        board[move] = current_player

        winner = check_winner(board)
        if winner:
            display_board(board)
            if mode == 2 and winner == "O":
                print("Computer wins!")
                score["Computer"] += 1
            else:
                print(f"Player {winner} wins!")
                score[f"Player {winner}"] += 1
            break

        if board_full(board):
            display_board(board)
            print("It's a draw!")
            score["Draws"] += 1
            break

        current_player = "O" if current_player == "X" else "X"

def main():
    score = {
        "Player X": 0,
        "Player O": 0,
        "Computer": 0,
        "Draws": 0
    }

    print("================================")
    print("      ENHANCED TIC TAC TOE")
    print("================================")

    while True:
        print("\nChoose game mode:")
        print("1. Player vs Player")
        print("2. Player vs Computer")

        try:
            mode = int(input("Enter choice (1 or 2): "))
        except ValueError:
            print("Please enter 1 or 2.")
            continue

        if mode not in (1, 2):
            print("Please enter 1 or 2.")
            continue

        play_game(mode, score)

        print("\nScoreboard")
        print(f"Player X : {score['Player X']}")
        if mode == 1:
            print(f"Player O : {score['Player O']}")
        else:
            print(f"Computer : {score['Computer']}")
        print(f"Draws    : {score['Draws']}")

        again = input("\nPlay another round? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing Tic Tac Toe!")
            break

if __name__ == "__main__":
    main()
