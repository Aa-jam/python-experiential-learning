# Tic Tac Toe Game
# Python Experiential Learning Project

def display_board(board):
    print("\n")
    print(" " + board[0] + " | " + board[1] + " | " + board[2])
    print("---+---+---")
    print(" " + board[3] + " | " + board[4] + " | " + board[5])
    print("---+---+---")
    print(" " + board[6] + " | " + board[7] + " | " + board[8])
    print()


def get_move(board, player):
    while True:
        try:
            position = int(input(f"Player {player}, enter position (1-9): "))

            if position < 1 or position > 9:
                print("Invalid position! Enter a number from 1 to 9.")
            elif board[position - 1] != " ":
                print("Position already occupied! Choose another position.")
            else:
                return position - 1

        except ValueError:
            print("Invalid input! Please enter a number.")


def check_winner(board):
    winning_combinations = [
        (0, 1, 2),   # Row 1
        (3, 4, 5),   # Row 2
        (6, 7, 8),   # Row 3
        (0, 3, 6),   # Column 1
        (1, 4, 7),   # Column 2
        (2, 5, 8),   # Column 3
        (0, 4, 8),   # Diagonal
        (2, 4, 6)    # Diagonal
    ]

    for a, b, c in winning_combinations:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]

    return None


def board_full(board):
    return " " not in board


def play_game():
    board = [" "] * 9
    current_player = "X"

    print("\n===== TIC TAC TOE GAME =====")
    print("Positions are numbered from 1 to 9.")

    while True:
        display_board(board)

        # Get valid player move
        position = get_move(board, current_player)

        # Update board
        board[position] = current_player

        # Check winner
        winner = check_winner(board)

        if winner:
            display_board(board)
            print(f"Player {winner} wins!")
            break

        # Check draw
        if board_full(board):
            display_board(board)
            print("It's a Draw!")
            break

        # Switch player
        if current_player == "X":
            current_player = "O"
        else:
            current_player = "X"


def main():
    while True:
        play_game()

        choice = input("\nPlay again? (Y/N): ")

        if choice.upper() != "Y":
            print("Thank you for playing!")
            break


# Start the game
main()