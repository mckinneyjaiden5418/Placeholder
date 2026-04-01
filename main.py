import tkinter as tk
from tkinter import font as tkfont
import threading
import time
from twilio.rest import Client

# Config
ACCOUNT_SID: str = ""
AUTH_TOKEN: str = ""
PHONE_NUMBER: str = ""
TO_NUMBER: str = ""
MESSAGE: str = "write later."
starting_time: int = 60

class PlaceHolderName:
    """Main class."""
    def __init__(self) -> None:
        pass

    def create_ui(self) -> None:
        """Create the UI"""
        pass

    def load_data(self) -> None:
        """Load text data."""
        pass

    def start_round(self) -> None:
        """Start a new round."""
        pass

    def run_timer(self) -> int:
        """Run the timer.

        Returns:
            int: The time in seconds.
        """
        pass

    def on_type(self, event: tk.Event) -> None:
        """Handle the typing event.

        Args:
            event (tk.Event): The typing event.
        """
        pass

    def round_win(self) -> None:
        """Handle the round win."""
        pass

    def round_lose(self) -> None:
        """Handle the round lose."""
        pass

    def flash_red(self) -> None:
        """Flash the screen red."""
        pass

    def send_sms(self) -> None:
        """Send SMS."""
        pass


if __name__ == "__main__":
    pass
