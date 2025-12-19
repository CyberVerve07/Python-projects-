import tkinter as tk
from tkinter import messagebox


def caesar_encrypt(text: str, shift: int) -> str:
    result = []
    shift = shift % 26
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            offset = (ord(char) - base + shift) % 26
            result.append(chr(base + offset))
        else:
            result.append(char)
    return "".join(result)


def caesar_decrypt(text: str, shift: int) -> str:
    # Reuse encrypt logic with negative shift
    return caesar_encrypt(text, -shift)


class CaesarCipherApp:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Cryptography App - Caesar Cipher")
        master.geometry("520x260")
        master.resizable(False, False)

        # Variables
        self.message_var = tk.StringVar()
        self.shift_var = tk.StringVar()
        self.result_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        # Use grid for clean layout
        pad_x = 10
        pad_y = 8

        # Message label + entry
        tk.Label(self.master, text="Message:").grid(
            row=0, column=0, sticky="w", padx=pad_x, pady=pad_y
        )
        tk.Entry(self.master, textvariable=self.message_var, width=50).grid(
            row=0, column=1, columnspan=3, sticky="we", padx=pad_x, pady=pad_y
        )

        # Shift label + entry
        tk.Label(self.master, text="Shift key:").grid(
            row=1, column=0, sticky="w", padx=pad_x, pady=pad_y
        )
        tk.Entry(self.master, textvariable=self.shift_var, width=10).grid(
            row=1, column=1, sticky="w", padx=pad_x, pady=pad_y
        )

        # Buttons
        tk.Button(
            self.master,
            text="Encrypt",
            command=self.encrypt_message,
            bg="#4CAF50",
            fg="white",
            width=10,
        ).grid(row=2, column=1, padx=pad_x, pady=pad_y)

        tk.Button(
            self.master,
            text="Decrypt",
            command=self.decrypt_message,
            bg="#2196F3",
            fg="white",
            width=10,
        ).grid(row=2, column=2, padx=pad_x, pady=pad_y)

        tk.Button(
            self.master,
            text="Clear",
            command=self.clear_fields,
            width=10,
        ).grid(row=2, column=3, padx=pad_x, pady=pad_y)

        # Result label
        tk.Label(self.master, text="Result:").grid(
            row=3, column=0, sticky="nw", padx=pad_x, pady=(pad_y, 0)
        )
        tk.Label(
            self.master,
            textvariable=self.result_var,
            font=("Arial", 12),
            fg="blue",
            wraplength=420,
            justify="left",
        ).grid(row=3, column=1, columnspan=3, sticky="w", padx=pad_x, pady=(pad_y, 0))

        # Make columns 1–3 stretch a bit if window is resized
        for col in range(1, 4):
            self.master.grid_columnconfigure(col, weight=1)

    def _get_shift(self) -> int | None:
        raw = self.shift_var.get().strip()
        if not raw:
            messagebox.showerror("Invalid shift", "Shift key is required.")
            return None
        try:
            return int(raw)
        except ValueError:
            messagebox.showerror("Invalid shift", "Shift must be an integer.")
            return None

    def encrypt_message(self) -> None:
        shift = self._get_shift()
        if shift is None:
            return
        msg = self.message_var.get()
        self.result_var.set(caesar_encrypt(msg, shift))

    def decrypt_message(self) -> None:
        shift = self._get_shift()
        if shift is None:
            return
        msg = self.message_var.get()
        self.result_var.set(caesar_decrypt(msg, shift))

    def clear_fields(self) -> None:
        self.message_var.set("")
        self.shift_var.set("")
        self.result_var.set("")


def main() -> None:
    root = tk.Tk()
    app = CaesarCipherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
