#!/usr/bin/env python3
import random
import tkinter as tk
from fractions import Fraction


CARD_WIDTH = 150
CARD_HEIGHT = 220
CARD_GAP = 24
TABLE_BG = "#0f5132"
PIP_X_FOR_COUNT = {
    1: [0.50],
    2: [0.35, 0.65],
}

# Row patterns are expressed top->bottom to match the reference deck.
# Format: (pip_count_in_row, y_position_ratio)
ROW_LAYOUTS = {
    1: [(1, 0.50)],
    2: [(1, 0.30), (1, 0.70)],
    3: [(1, 0.28), (1, 0.50), (1, 0.72)],
    4: [(2, 0.31), (2, 0.69)],
    5: [(2, 0.31), (1, 0.50), (2, 0.69)],
    6: [(2, 0.27), (2, 0.50), (2, 0.73)],
    7: [(2, 0.21), (1, 0.31), (2, 0.47), (2, 0.67)],
    8: [(2, 0.20), (1, 0.30), (2, 0.43), (1, 0.57), (2, 0.70)],
    9: [(2, 0.20), (2, 0.34), (1, 0.50), (2, 0.66), (2, 0.80)],
    10: [(2, 0.20), (1, 0.30), (2, 0.40), (2, 0.60), (1, 0.70), (2, 0.80)],
}

PIP_SIZE_BY_RANK = {
    1: 72,
    2: 24,
    3: 24,
    4: 24,
    5: 24,
    6: 23,
    7: 22,
    8: 22,
    9: 21,
    10: 20,
}


def build_pip_positions(rank):
    positions = []
    for row_count, y_ratio in ROW_LAYOUTS[rank]:
        for x_ratio in PIP_X_FOR_COUNT[row_count]:
            positions.append((x_ratio, y_ratio))
    return positions


def rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)


def draw_card(canvas, x, y, rank, suit):
    suit_symbols = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}
    is_red = suit in ("Hearts", "Diamonds")
    color = "#c1121f" if is_red else "#111111"
    rank_text = "A" if rank == 1 else str(rank)
    symbol = suit_symbols[suit]

    rounded_rect(
        canvas,
        x,
        y,
        x + CARD_WIDTH,
        y + CARD_HEIGHT,
        radius=16,
        fill="white",
        outline="#d9d9d9",
        width=2,
    )

    canvas.create_text(
        x + 14,
        y + 16,
        text=rank_text,
        fill=color,
        anchor="nw",
        font=("Georgia", 20, "bold"),
    )
    canvas.create_text(
        x + 17,
        y + 44,
        text=symbol,
        fill=color,
        anchor="nw",
        font=("Georgia", 12, "bold"),
    )
    pip_size = PIP_SIZE_BY_RANK[rank]
    for x_ratio, y_ratio in build_pip_positions(rank):
        px = x + CARD_WIDTH * x_ratio
        py = y + CARD_HEIGHT * y_ratio
        angle = 180 if y_ratio > 0.5 else 0
        canvas.create_text(
            px,
            py,
            text=symbol,
            fill=color,
            font=("Georgia", pip_size, "bold"),
            angle=angle,
        )
    canvas.create_text(
        x + CARD_WIDTH - 14,
        y + CARD_HEIGHT - 16,
        text=rank_text,
        fill=color,
        anchor="se",
        font=("Georgia", 20, "bold"),
    )
    canvas.create_text(
        x + CARD_WIDTH - 17,
        y + CARD_HEIGHT - 44,
        text=symbol,
        fill=color,
        anchor="se",
        font=("Georgia", 12, "bold"),
    )


def trim_outer_parentheses(expr):
    while expr.startswith("(") and expr.endswith(")"):
        depth = 0
        balanced = True
        for idx, ch in enumerate(expr):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if depth == 0 and idx < len(expr) - 1:
                balanced = False
                break
        if not balanced:
            break
        expr = expr[1:-1]
    return expr


def combine_pairs(a_value, a_expr, b_value, b_expr, positive_only):
    pairs = []

    def add_candidate(value, expr):
        if positive_only and value <= 0:
            return
        pairs.append((value, expr))

    add_candidate(a_value + b_value, f"({a_expr}+{b_expr})")
    add_candidate(a_value - b_value, f"({a_expr}-{b_expr})")
    add_candidate(b_value - a_value, f"({b_expr}-{a_expr})")
    add_candidate(a_value * b_value, f"({a_expr}*{b_expr})")
    if b_value != 0:
        add_candidate(a_value / b_value, f"({a_expr}/{b_expr})")
    if a_value != 0:
        add_candidate(b_value / a_value, f"({b_expr}/{a_expr})")
    return pairs


def search_24(items, positive_only):
    if len(items) == 1:
        return items[0][1] if items[0][0] == Fraction(24, 1) else None

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a_value, a_expr = items[i]
            b_value, b_expr = items[j]
            rest = [items[k] for k in range(len(items)) if k not in (i, j)]
            for new_value, new_expr in combine_pairs(
                a_value, a_expr, b_value, b_expr, positive_only
            ):
                found = search_24(rest + [(new_value, new_expr)], positive_only)
                if found is not None:
                    return found
    return None


def solve_24(values):
    items = [(Fraction(value), str(value)) for value in values]
    positive_result = search_24(items, positive_only=True)
    if positive_result is not None:
        return trim_outer_parentheses(positive_result), True

    any_result = search_24(items, positive_only=False)
    if any_result is not None:
        return trim_outer_parentheses(any_result), False

    return None, False


def main():
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    deck = [(rank, suit) for suit in suits for rank in range(1, 11)]
    current_hand = []
    root = tk.Tk()
    root.title("Poker Hand (1-10, No Face Cards, No Jokers)")
    root.configure(bg=TABLE_BG)

    total_width = CARD_GAP + (CARD_WIDTH + CARD_GAP) * 4
    total_height = CARD_HEIGHT + 2 * CARD_GAP

    label = tk.Label(
        root,
        text="24 Points Game",
        bg=TABLE_BG,
        fg="white",
        font=("Helvetica", 18, "bold"),
    )
    label.pack(pady=(14, 6))

    canvas = tk.Canvas(
        root,
        width=total_width,
        height=total_height,
        bg=TABLE_BG,
        highlightthickness=0,
    )
    canvas.pack(padx=14, pady=8)

    answer_var = tk.StringVar(value="")
    root.minsize(total_width + 28, total_height + 260)

    def deal():
        canvas.delete("all")
        current_hand[:] = random.sample(deck, 4)
        for idx, (rank, suit) in enumerate(current_hand):
            x = CARD_GAP + idx * (CARD_WIDTH + CARD_GAP)
            y = CARD_GAP
            draw_card(canvas, x, y, rank, suit)
        answer_var.set("")

    def show_answer():
        suit_symbols = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}
        rank_text = lambda value: "A" if value == 1 else str(value)
        values = [rank for rank, _ in current_hand]
        cards_text = "  ".join(f"{rank_text(rank)}{suit_symbols[suit]}" for rank, suit in current_hand)
        formula, all_positive = solve_24(values)

        if formula is None:
            answer_var.set("No Answer")
            return
        elif all_positive:
            msg = f"{formula} = 24"
        else:
            msg = (
                f"{formula} = 24\n"
                "(No solution found with all-positive intermediate results.)"
            )
        answer_var.set(f"Cards: {cards_text}\n{msg}")

    button_frame = tk.Frame(root, bg=TABLE_BG)
    button_frame.pack(fill="x", padx=14, pady=(0, 14))
    button_frame.grid_columnconfigure(0, weight=1, uniform="actions")
    button_frame.grid_columnconfigure(1, weight=1, uniform="actions")

    deal_button = tk.Button(
        button_frame,
        text="Deal New Hand",
        command=deal,
        font=("Helvetica", 12, "bold"),
        bg="#f7f7f7",
        activebackground="#e6e6e6",
        padx=12,
        pady=8,
        relief="raised",
        bd=2,
        cursor="hand2",
    )
    deal_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

    answer_button = tk.Button(
        button_frame,
        text="Show Me Answer",
        command=show_answer,
        font=("Helvetica", 12, "bold"),
        bg="#f7f7f7",
        activebackground="#e6e6e6",
        padx=12,
        pady=8,
        relief="raised",
        bd=2,
        cursor="hand2",
    )
    answer_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    answer_frame = tk.Frame(root, bg=TABLE_BG)
    answer_frame.pack(fill="x", padx=14, pady=(0, 14))

    answer_title = tk.Label(
        answer_frame,
        text="24-Point Answer",
        bg=TABLE_BG,
        fg="white",
        anchor="w",
        font=("Helvetica", 14, "bold"),
    )
    answer_title.pack(fill="x", pady=(0, 6))

    answer_label = tk.Label(
        answer_frame,
        textvariable=answer_var,
        bg="#123d2b",
        fg="white",
        justify="left",
        anchor="nw",
        padx=12,
        pady=10,
        wraplength=total_width - 16,
        font=("Helvetica", 12, "bold"),
        relief="solid",
        bd=1,
        height=4,
    )
    answer_label.pack(fill="x")

    deal()
    root.mainloop()

if __name__ == "__main__":
    main()
