import sys
import tkinter as tk
import threading
import time
from twilio.rest import Client

sys.stdout.reconfigure(encoding="utf-8")

# Config
MOCK_MODE: bool = True  # Set to False to send real text

ACCOUNT_SID: str = ""
AUTH_TOKEN: str = ""
FROM_NUMBER: str = ""
TO_NUMBER: str = ""
MESSAGE: str = (
    "hey... i know it's been a while but i've been doing a lot of thinking "
    "and i really miss you. i miss us. i think i still love you and i was "
    "wondering if maybe we could talk? i'm sorry for everything 💔"
)
START_SECONDS: int = 60

# Colors
BG      = "#0a0a0f"
CARD    = "#12121c"
ACCENT  = "#dc3232"
GREEN   = "#32c878"
DIM     = "#8c8ca0"
WHITE   = "#f0f0f5"
NEUTRAL = "#505064"

# Passages
PASSAGES: list[str] = [
    "The mitochondria is the powerhouse of the cell. Adenosine triphosphate, commonly known as ATP, is synthesized through a process called oxidative phosphorylation within the inner mitochondrial membrane.",
    "In computer science, a Turing machine is a mathematical model of computation describing an abstract machine that manipulates symbols on a strip of tape according to a table of rules. Despite the model's simplicity, it is capable of implementing any computer algorithm.",
    "The Heisenberg uncertainty principle states that the more precisely the position of a particle is determined, the less precisely its momentum can be predicted from initial conditions, and vice versa. This is not a statement about measurement limitations, but a fundamental property of quantum systems.",
    "Polymorphism in object-oriented programming refers to the ability of a variable, function, or object to take on multiple forms. It allows methods to do different things based on the object that is acting upon them, enabling one interface to be used for a general class of actions.",
    "The Krebs cycle, also known as the citric acid cycle, is a series of chemical reactions used by all aerobic organisms to release stored energy through the oxidation of acetyl-CoA derived from carbohydrates, fats, and proteins into adenosine triphosphate and carbon dioxide.",
    "Fourier analysis is the study of the way general functions may be represented or approximated by sums of simpler trigonometric functions. It plays a central role in signal processing, quantum mechanics, and solving differential equations in physics and engineering.",
]


class TypeOrDie:
    """Main game class."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("TYPE OR DIE")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.round: int = 0
        self.seconds_left: int = START_SECONDS
        self.game_active: bool = False
        self.timer_thread: threading.Thread | None = None
        self.stop_timer: threading.Event = threading.Event()

    def create_ui(self) -> None:
        """Create the UI."""

        # Top Bar
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=40, pady=(30, 10))

        tk.Label(
            top, text="TYPE OR DIE", bg=BG, fg=ACCENT,
            font=("Courier New", 20, "bold"),
        ).pack(side="left")

        self.round_label = tk.Label(
            top, text="ROUND 1", bg=BG, fg=DIM,
            font=("Courier New", 13, "bold"),
        )
        self.round_label.pack(side="left", padx=20)

        self.timer_label = tk.Label(
            top, text="60", bg=BG, fg=WHITE,
            font=("Courier New", 46, "bold"),
        )
        self.timer_label.pack(side="right")

        # Passage Box
        passage_frame = tk.Frame(self.root, bg="#282838", bd=1)
        passage_frame.pack(fill="x", padx=40, pady=(10, 0))

        self.passage_text = tk.Text(
            passage_frame, height=5, wrap="word", bg=CARD, fg=DIM,
            font=("Courier New", 14), bd=0, padx=16, pady=14,
            state="disabled", cursor="arrow",
        )
        self.passage_text.pack(fill="x")
        self.passage_text.tag_config("correct", foreground=GREEN)
        self.passage_text.tag_config("wrong", foreground=ACCENT, background="#3c0a0a")
        self.passage_text.tag_config("neutral", foreground=NEUTRAL)

        # Input Box
        input_frame = tk.Frame(self.root, bg=ACCENT, bd=1)
        input_frame.pack(fill="x", padx=40, pady=(10, 0))

        self.input_box = tk.Text(
            input_frame, height=5, wrap="word",
            bg="#0e0e16", fg=WHITE, insertbackground=ACCENT,
            font=("Courier New", 14), bd=0, padx=16, pady=14,
            state="disabled",
        )
        self.input_box.pack(fill="x")
        self.input_box.bind("<KeyRelease>", self.on_type)

        # Status Label
        self.status_label = tk.Label(
            self.root,
            text="Press START to begin. Don't stop typing or the text goes out.",
            bg=BG, fg=DIM, font=("Courier New", 12),
        )
        self.status_label.pack(pady=(10, 0))

        # Start Button
        btn = tk.Button(
            self.root, text="START GAME", bg=ACCENT, fg="white",
            font=("Courier New", 15, "bold"), bd=0, padx=30, pady=10,
            activebackground="#ff5050", activeforeground="white",
            cursor="hand2", command=self.start_round,
        )
        btn.pack(pady=(16, 30))

        self.root.geometry("860x580")
        self.load_passage()

    def load_passage(self) -> None:
        """Load the passage for the current round."""
        passage: str = PASSAGES[min(self.round, len(PASSAGES) - 1)]
        secs: int = max(20, START_SECONDS - self.round * 8)

        self.round_label.config(text=f"ROUND {self.round + 1}")
        self.timer_label.config(text=str(secs), fg=WHITE)
        self.passage_text.config(state="normal")
        self.passage_text.delete("1.0", "end")
        self.passage_text.insert("end", passage, "neutral")
        self.passage_text.config(state="disabled")

    def start_round(self) -> None:
        """Start a new round."""
        self.game_active = True
        self.stop_timer.clear()
        self.seconds_left = max(20, START_SECONDS - self.round * 8)

        self.timer_label.config(text=str(self.seconds_left), fg=WHITE)
        self.status_label.config(text="TYPE! Don't stop...", fg=DIM)

        self.input_box.config(state="normal")
        self.input_box.delete("1.0", "end")
        self.input_box.focus_set()

        self.load_passage()

        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()

    def run_timer(self) -> None:
        """Run the countdown timer on a background thread."""
        while self.seconds_left > 0 and not self.stop_timer.is_set():
            time.sleep(1)
            if self.stop_timer.is_set():
                return
            self.seconds_left -= 1
            color: str = ACCENT if self.seconds_left <= 10 else WHITE
            self.root.after(
                0,
                lambda s=self.seconds_left, c=color: self.timer_label.config(text=str(s), fg=c),
            )

        if not self.stop_timer.is_set():
            self.root.after(0, self.round_lose)

    def on_type(self, event: tk.Event) -> None:
        """Handle keystrokes and update passage coloring.

        Args:
            event (tk.Event): The key release event.
        """
        if not self.game_active:
            return

        passage: str = PASSAGES[min(self.round, len(PASSAGES) - 1)]
        typed: str = self.input_box.get("1.0", "end-1c")

        self.passage_text.config(state="normal")
        self.passage_text.delete("1.0", "end")

        for i, ch in enumerate(passage):
            if i < len(typed):
                tag: str = "correct" if typed[i] == ch else "wrong"
            else:
                tag = "neutral"
            self.passage_text.insert("end", ch, tag)

        self.passage_text.config(state="disabled")

        if typed == passage:
            self.stop_timer.set()
            self.game_active = False
            self.round += 1
            self.root.after(0, self.round_win)

    def round_win(self) -> None:
        """Handle a round win."""
        self.input_box.config(state="disabled")
        self.status_label.config(
            text=f"✓ ROUND {self.round} COMPLETE! Next round starts in 3s...",
            fg=GREEN,
        )
        self.timer_label.config(fg=GREEN)
        self.root.after(3000, lambda: (
            self.load_passage(),
            self.input_box.delete("1.0", "end"),
            self.status_label.config(
                text=(
                    f"Press START for Round {self.round + 1} — "
                    f"{max(20, START_SECONDS - self.round * 8)}s. Harder passage, less time."
                ),
                fg=DIM,
            ),
            self.timer_label.config(fg=WHITE),
        ))

    def round_lose(self) -> None:
        """Handle a round loss."""
        self.game_active = False
        self.input_box.config(state="disabled")
        self.timer_label.config(text="0", fg=ACCENT)
        self.status_label.config(text="⚠  TIME'S UP. Sending the text...", fg=ACCENT)
        self.flash_red()
        threading.Thread(target=self.send_sms, daemon=True).start()

    def flash_red(self, count: int = 0) -> None:
        """Flash the background red on failure.

        Args:
            count (int): Current flash iteration.
        """
        if count >= 6:
            self.root.configure(bg=BG)
            return
        color: str = "#3c0000" if count % 2 == 0 else BG
        self.root.configure(bg=color)
        self.root.after(150, lambda: self.flash_red(count + 1))

    def send_sms(self) -> None:
        """Send the punishment SMS via Twilio and reset to round 1."""
        if MOCK_MODE:
            print(f"[MOCK] Would have texted {TO_NUMBER!r}: {MESSAGE}")
            self.root.after(
                0,
                lambda: self.status_label.config(
                    text="💀 [MOCK] Text would have been sent. Resetting to Round 1...",
                    fg=ACCENT,
                ),
            )
        else:
            try:
                client = Client(ACCOUNT_SID, AUTH_TOKEN)
                client.messages.create(body=MESSAGE, from_=FROM_NUMBER, to=TO_NUMBER)
                self.root.after(
                    0,
                    lambda: self.status_label.config(
                        text="💀 Text sent. You have failed. Resetting to Round 1...",
                        fg=ACCENT,
                    ),
                )
            except Exception as e:
                self.root.after(
                    0,
                    lambda err=e: self.status_label.config(
                        text=f"Text failed (check config): {err}",
                        fg=ACCENT,
                    ),
                )

        self.round = 0
        self.root.after(3500, lambda: (
            self.load_passage(),
            self.input_box.delete("1.0", "end"),
            self.status_label.config(
                text="Restarting from Round 1. Don't fail again.",
                fg=DIM,
            ),
            self.timer_label.config(fg=WHITE),
        ))


if __name__ == "__main__":
    root = tk.Tk()
    app = TypeOrDie(root)
    app.create_ui()
    root.mainloop()