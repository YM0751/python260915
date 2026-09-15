"""A small, dependency-free Tetris game using tkinter."""

import random
import tkinter as tk
from tkinter import messagebox


BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
PREVIEW_SIZE = 4

COLORS = {
    "I": "#27c9d9",
    "J": "#3f6de0",
    "L": "#ed942b",
    "O": "#e6c92f",
    "S": "#4fbd54",
    "T": "#a85bd8",
    "Z": "#e05252",
}

SHAPES = {
    "I": [
        ["....", "IIII", "....", "...."],
        ["..I.", "..I.", "..I.", "..I."],
    ],
    "J": [
        ["J..", "JJJ", "..."],
        [".JJ", ".J.", ".J."],
        ["...", "JJJ", "..J"],
        [".J.", "J..", "J.."],
    ],
    "L": [
        ["..L", "LLL", "..."],
        [".L.", ".L.", ".LL"],
        ["...", "LLL", "L.."],
        ["LL.", ".L.", ".L."],
    ],
    "O": [
        ["OO", "OO"],
    ],
    "S": [
        [".SS", "SS.", "..."],
        ["S..", "SS.", ".S."],
    ],
    "T": [
        [".T.", "TTT", "..."],
        [".T.", ".TT", ".T."],
        ["...", "TTT", ".T."],
        [".T.", "TT.", ".T."],
    ],
    "Z": [
        ["ZZ.", ".ZZ", "..."],
        [".Z.", "ZZ.", "Z.."],
    ],
}


class Tetris:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tetris")
        self.root.resizable(False, False)
        self.root.configure(bg="#20242b")

        self.board_canvas = tk.Canvas(
            root,
            width=BOARD_WIDTH * CELL_SIZE,
            height=BOARD_HEIGHT * CELL_SIZE,
            bg="#11151a",
            highlightthickness=0,
        )
        self.board_canvas.grid(row=0, column=0, rowspan=2, padx=(12, 6), pady=12)

        side_panel = tk.Frame(root, bg="#20242b", width=150)
        side_panel.grid(row=0, column=1, sticky="n", padx=(6, 12), pady=12)
        side_panel.grid_propagate(False)

        tk.Label(
            side_panel,
            text="NEXT",
            font=("Segoe UI", 12, "bold"),
            fg="#f3f5f7",
            bg="#20242b",
        ).pack(pady=(0, 6))
        self.preview_canvas = tk.Canvas(
            side_panel,
            width=PREVIEW_SIZE * CELL_SIZE,
            height=PREVIEW_SIZE * CELL_SIZE,
            bg="#11151a",
            highlightthickness=0,
        )
        self.preview_canvas.pack()

        self.score_label = tk.Label(side_panel, fg="#f3f5f7", bg="#20242b", justify="left")
        self.score_label.pack(anchor="w", pady=(18, 0))
        self.status_label = tk.Label(
            side_panel,
            text="",
            fg="#f0c75e",
            bg="#20242b",
            justify="left",
        )
        self.status_label.pack(anchor="w", pady=(14, 0))

        tk.Label(
            side_panel,
            text="Arrows: move / rotate\nSpace: hard drop\nP: pause   R: restart",
            font=("Segoe UI", 9),
            fg="#aeb6c0",
            bg="#20242b",
            justify="left",
        ).pack(anchor="w", pady=(22, 0))

        self.root.bind("<KeyPress>", self.handle_key)
        self.reset_game()

    def reset_game(self) -> None:
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.paused = False
        self.game_over = False
        self.current = self.new_piece()
        self.next_type = random.choice(list(SHAPES))
        self.spawn_piece()
        self.update_screen()
        self.schedule_fall()

    def new_piece(self) -> dict[str, object]:
        piece_type = self.next_type if hasattr(self, "next_type") else random.choice(list(SHAPES))
        shape = SHAPES[piece_type][0]
        return {
            "type": piece_type,
            "rotation": 0,
            "x": (BOARD_WIDTH - len(shape[0])) // 2,
            "y": 0,
        }

    def spawn_piece(self) -> None:
        self.current = self.new_piece()
        self.next_type = random.choice(list(SHAPES))
        if not self.is_valid(self.current["x"], self.current["y"], self.current["rotation"]):
            self.game_over = True

    def cells_for(self, piece: dict[str, object], rotation: int | None = None) -> list[tuple[int, int]]:
        piece_type = piece["type"]
        rotation_index = piece["rotation"] if rotation is None else rotation
        shape = SHAPES[piece_type][rotation_index % len(SHAPES[piece_type])]
        return [
            (column, row)
            for row, line in enumerate(shape)
            for column, value in enumerate(line)
            if value != "."
        ]

    def is_valid(self, x: int, y: int, rotation: int) -> bool:
        for column, row in self.cells_for(self.current, rotation):
            board_x = x + column
            board_y = y + row
            if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:
                return False
            if board_y >= 0 and self.board[board_y][board_x] is not None:
                return False
        return True

    def move(self, delta_x: int, delta_y: int) -> bool:
        new_x = self.current["x"] + delta_x
        new_y = self.current["y"] + delta_y
        if self.is_valid(new_x, new_y, self.current["rotation"]):
            self.current["x"] = new_x
            self.current["y"] = new_y
            return True
        return False

    def rotate(self) -> None:
        new_rotation = self.current["rotation"] + 1
        x = self.current["x"]
        if self.is_valid(x, self.current["y"], new_rotation):
            self.current["rotation"] = new_rotation
        elif self.is_valid(x - 1, self.current["y"], new_rotation):
            self.current["x"] = x - 1
            self.current["rotation"] = new_rotation
        elif self.is_valid(x + 1, self.current["y"], new_rotation):
            self.current["x"] = x + 1
            self.current["rotation"] = new_rotation

    def lock_piece(self) -> None:
        piece_type = self.current["type"]
        for column, row in self.cells_for(self.current):
            board_x = self.current["x"] + column
            board_y = self.current["y"] + row
            if board_y >= 0:
                self.board[board_y][board_x] = piece_type

        completed = [row for row in self.board if all(cell is not None for cell in row)]
        if completed:
            self.board = [row for row in self.board if not all(cell is not None for cell in row)]
            self.board = [[None] * BOARD_WIDTH for _ in completed] + self.board
            self.lines += len(completed)
            self.score += {1: 100, 2: 300, 3: 500, 4: 800}[len(completed)] * self.level
            self.level = self.lines // 10 + 1

        self.spawn_piece()

    def hard_drop(self) -> None:
        distance = 0
        while self.move(0, 1):
            distance += 1
        self.score += distance * 2
        self.lock_piece()

    def tick(self) -> None:
        if not self.paused and not self.game_over:
            if not self.move(0, 1):
                self.lock_piece()
            self.update_screen()
        self.schedule_fall()

    def schedule_fall(self) -> None:
        delay = max(80, 650 - (self.level - 1) * 55)
        self.timer_id = self.root.after(delay, self.tick)

    def handle_key(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        if key == "r":
            self.reset_game()
            return
        if key == "p" and not self.game_over:
            self.paused = not self.paused
            self.update_screen()
            return
        if self.paused or self.game_over:
            return
        if key == "left":
            self.move(-1, 0)
        elif key == "right":
            self.move(1, 0)
        elif key == "down":
            if self.move(0, 1):
                self.score += 1
        elif key == "up":
            self.rotate()
        elif key == "space":
            self.hard_drop()
        self.update_screen()

    def update_screen(self) -> None:
        self.draw_board()
        self.draw_preview()
        self.score_label.config(
            text=f"Score  {self.score}\nLines  {self.lines}\nLevel  {self.level}"
        )
        if self.game_over:
            self.status_label.config(text="GAME OVER\nPress R to restart")
        elif self.paused:
            self.status_label.config(text="PAUSED\nPress P to resume")
        else:
            self.status_label.config(text="")

    def draw_board(self) -> None:
        self.board_canvas.delete("all")
        for row in range(BOARD_HEIGHT):
            for column in range(BOARD_WIDTH):
                color = self.board[row][column]
                self.draw_cell(self.board_canvas, column, row, color)

        if not self.game_over:
            piece_type = self.current["type"]
            for column, row in self.cells_for(self.current):
                board_x = self.current["x"] + column
                board_y = self.current["y"] + row
                if board_y >= 0:
                    self.draw_cell(self.board_canvas, board_x, board_y, COLORS[piece_type])

    def draw_cell(self, canvas: tk.Canvas, column: int, row: int, color: str | None) -> None:
        x1 = column * CELL_SIZE
        y1 = row * CELL_SIZE
        canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE, outline="#252c34")
        if color:
            canvas.create_rectangle(
                x1 + 2,
                y1 + 2,
                x1 + CELL_SIZE - 2,
                y1 + CELL_SIZE - 2,
                fill=color,
                outline="#ffffff",
                width=1,
            )

    def draw_preview(self) -> None:
        self.preview_canvas.delete("all")
        shape = SHAPES[self.next_type][0]
        offset_x = (PREVIEW_SIZE - len(shape[0])) // 2
        offset_y = (PREVIEW_SIZE - len(shape)) // 2
        for row, line in enumerate(shape):
            for column, value in enumerate(line):
                if value != ".":
                    self.draw_cell(
                        self.preview_canvas,
                        offset_x + column,
                        offset_y + row,
                        COLORS[self.next_type],
                    )


def main() -> None:
    root = tk.Tk()
    Tetris(root)
    root.mainloop()


if __name__ == "__main__":
    main()
