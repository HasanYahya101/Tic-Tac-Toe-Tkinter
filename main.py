import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple


class Player(NamedTuple):
    label: str
    color: str


class Move(NamedTuple):
    row: int
    col: int
    label: str = ""


BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="royalblue"),
    Player(label="O", color="forestgreen"),
)


class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self._setup_board()

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [[(move.row, move.col) for move in row] for row in self._current_moves]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def toggle_player(self):
        """Return a toggled player."""
        self.current_player = next(self._players)

    def is_valid_move(self, move):
        """Return True if move is valid, and False otherwise."""
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    def process_move(self, move):
        """Process the current move and check if it's a win."""
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(self._current_moves[n][m].label for n, m in combo)
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break

    def has_winner(self):
        """Return True if the game has a winner, and False otherwise."""
        return self._has_winner

    def is_tied(self):
        """Return True if the game is tied, and False otherwise."""
        no_winner = not self._has_winner
        played_moves = (move.label for row in self._current_moves for move in row)
        return no_winner and all(played_moves)

    def reset_game(self):
        """Reset the game state to play again."""
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []


class TicTacToeBoard(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Tic-Tac-Toe!")
        self.resizable(False, False)
        self._cells = {}
        self._game = game
        self._create_menu()
        self._create_board_display()
        self._create_board_grid(background="lightgray")  # Set background color

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add
        menu_bar.add_cascade(label="Options", menu=file_menu)
        file_menu.add_command(label="Restart", command=self._restart_game)
        file_menu.add_command(label="Quit", command=self.quit)

    def _create_board_display(self):
        for row, row_content in enumerate(self._game._current_moves):
            for col, move in enumerate(row_content):
                cell = tk.Label(
                    master=self,
                    text=move.label,
                    font=font.Font(size=32),
                    width=4,
                    height=2,
                    relief="groove",
                    bg="white",
                    fg="black",
                    borderwidth=2,
                )
                cell.grid(row=row, column=col)
                cell.bind("<Button-1>", self._on_cell_clicked)
                self._cells[move] = cell  # Store the cell reference

    def _create_board_grid(self, background):
        for i in range(self._game.board_size):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)
            for j in range(self._game.board_size):
                self._cells[Move(i, j)].config(bg=background)

    def _on_cell_clicked(self, event):
        if self._game.has_winner() or self._game.is_tied():
            return
        cell = event.widget
        row, col = cell.grid_info()["row"], cell.grid_info()["column"]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            cell.config(text=move.label, fg=self._game.current_player.color)
            self._game.process_move(move)
            if self._game.has_winner():
                self._highlight_winner()
            elif self._game.is_tied():
                self._show_tie()
            else:
                self._game.toggle_player()

    def _highlight_winner(self):
        for row, col in self._game.winner_combo:
            self._cells[Move(row, col)].config(bg="yellow")

    def _show_tie(self):
        for move, cell in self._cells.items():
            cell.config(bg="orange")

    def _restart_game(self):
        for cell in self._cells.values():
            cell.config(text="", bg="white")
        self._game.reset_game()


if __name__ == "__main__":
    game = TicTacToeGame()
    board = TicTacToeBoard(game)
    board.mainloop()
