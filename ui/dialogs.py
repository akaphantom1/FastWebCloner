# ui/dialogs.py
# -*- coding: utf-8 -*-
"""
Dialoguri pentru aplicatia FastWebCloner
"""

import tkinter as tk
from tkinter import ttk  # doar daca vrei scroll texte
import customtkinter as ctk
import webbrowser
import logging

from config import APP_NAME, APP_VERSION, APP_AUTHOR
from utils.constants import TEXTS, COLORS
from ui.components import create_button, create_label  # fara create_progress_bar -> CTkProgressBar direct

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#  Dialog „Despre”
# --------------------------------------------------------------------------- #
def show_about_dialog(parent):
    """Dialog modern Despre aplicatie."""
    about_window = ctk.CTkToplevel(parent)
    about_window.title(TEXTS['about_title'])
    about_window.geometry("500x450")
    about_window.resizable(False, False)
    about_window.transient(parent)
    about_window.grab_set()

    # Fundal gradient / culoare
    canvas = tk.Canvas(about_window, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_rectangle(0, 0, 500, 150, fill=COLORS["button"], outline="")

    # Logo placeholder (emoji)
    logo_frame = ctk.CTkFrame(about_window, fg_color="transparent")
    logo_frame.place(relx=0.5, rely=0.15, anchor="center")
    ctk.CTkLabel(
        logo_frame,
        text="🌐",
        font=("Arial", 48),
        text_color="#FFFFFF",
    ).pack()

    # Titlu
    ctk.CTkLabel(
        about_window,
        text=f"{APP_NAME} v{APP_VERSION}",
        font=("Arial", 20, "bold"),
        text_color=COLORS["text"],
    ).place(relx=0.5, rely=0.25, anchor="center")

    # Autor
    ctk.CTkLabel(
        about_window,
        text=f"de {APP_AUTHOR}",
        font=("Arial", 12),
        text_color=COLORS["text"],
    ).place(relx=0.5, rely=0.32, anchor="center")

    # Mesaj
    desc_frame = ctk.CTkFrame(about_window, fg_color="transparent")
    desc_frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=200)

    desc_text = tk.Text(
        desc_frame,
        wrap="word",
        font=("Arial", 11),
        bg=COLORS["card_bg"],
        fg=COLORS["text"],
        padx=15,
        pady=15,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
    )
    desc_text.insert("1.0", TEXTS['about_message'])
    desc_text.config(state="disabled")
    desc_text.pack(fill="both", expand=True)

    # Butoane
    button_frame = ctk.CTkFrame(about_window, fg_color="transparent")
    button_frame.place(relx=0.5, rely=0.9, anchor="center")

    web_button = create_button(
        button_frame,
        "Viziteaza Site-ul",
        command=lambda: webbrowser.open("https://webcloner.pro"),
        style="primary",
        width=180,
    )
    web_button.pack(side="left", padx=10)

    ok_button = create_button(
        button_frame,
        "OK",
        command=about_window.destroy,
        style="success",
        width=100,
    )
    ok_button.pack(side="left", padx=10)

    about_window.bind('<Escape>', lambda e: about_window.destroy())


# --------------------------------------------------------------------------- #
#  Dialog de eroare
# --------------------------------------------------------------------------- #
def show_error_dialog(parent, title, message, details=None):
    """Dialog de eroare modern."""
    error_window = ctk.CTkToplevel(parent)
    error_window.title(title)
    error_window.geometry("500x350")
    error_window.resizable(False, False)
    error_window.transient(parent)
    error_window.grab_set()

    main_frame = ctk.CTkFrame(error_window, fg_color=COLORS["card_bg"])
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    icon_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    icon_frame.pack(pady=10)
    ctk.CTkLabel(
        icon_frame,
        text="❌",
        font=("Arial", 48),
        text_color=COLORS["error"],
    ).pack()

    message_label = ctk.CTkLabel(
        main_frame,
        text=message,
        font=("Arial", 12),
        text_color=COLORS["text"],
        wraplength=450,
        justify="center",
    )
    message_label.pack(pady=(0, 20))

    if details:
        details_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["secondary_bg"], corner_radius=8)
        details_frame.pack(fill="both", expand=True, pady=(0, 20))
        details_text = tk.Text(
            details_frame,
            height=5,
            font=("Arial", 10),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"],
            padx=10,
            pady=10,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
        )
        details_text.insert("1.0", details)
        details_text.config(state="disabled")
        details_text.pack(fill="both", expand=True)

    ok_button = create_button(
        main_frame,
        "OK",
        command=error_window.destroy,
        style="error",
        width=100,
    )
    ok_button.pack(pady=10)

    error_window.bind('<Escape>', lambda e: error_window.destroy())


# --------------------------------------------------------------------------- #
#  Dialog de progres (cu posibilitate anulare)
# --------------------------------------------------------------------------- #
def show_progress_dialog(parent, title, message, cancelable=True):
    """Dialog de progres modern."""
    return ProgressDialog(parent, title, message, cancelable)


class ProgressDialog:
    """Dialog pentru afisarea progresului (Modernizat)."""

    def __init__(self, parent, title, message, cancelable=True):
        self.parent = parent
        self.cancelled = False

        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.configure(fg_color=COLORS["card_bg"])

        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        self.message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=("Arial", 12),
            text_color=COLORS["text"],
            wraplength=350,
            justify="center",
        )
        self.message_label.pack(pady=(0, 20))

        # CTkProgressBar (mai usor decat ttk style)
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            width=300,
            height=16,
            progress_color=COLORS["progress"],
            fg_color=COLORS["secondary_bg"],
            corner_radius=8,
            mode="indeterminate",
        )
        self.progress_bar.pack(fill="x", pady=(0, 20))
        self.progress_bar.start()

        if cancelable:
            self.cancel_button = create_button(
                main_frame,
                "Anuleaza",
                command=self.cancel,
                style="error",
                width=100,
            )
            self.cancel_button.pack()
            self.window.protocol("WM_DELETE_WINDOW", self.cancel)
        else:
            self.window.protocol("WM_DELETE_WINDOW", lambda: None)

    def update_message(self, message):
        self.message_label.configure(text=message)

    def update_progress(self, value):
        """
        value < 0 => indeterminate
        value 0..1 => determinat procentual
        """
        if value < 0:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(max(0.0, min(1.0, value)))

    def cancel(self):
        self.cancelled = True
        self.close()

    def close(self):
        try:
            self.progress_bar.stop()
        except Exception:
            pass
        self.window.destroy()

    def is_cancelled(self):
        return self.cancelled


# --------------------------------------------------------------------------- #
#  Dialog de confirmare
# --------------------------------------------------------------------------- #
def ask_confirmation(parent, title, message):
    """Dialog de confirmare modern. Returneaza True/False."""
    confirm_window = ctk.CTkToplevel(parent)
    confirm_window.title(title)
    confirm_window.geometry("400x250")
    confirm_window.resizable(False, False)
    confirm_window.transient(parent)
    confirm_window.grab_set()

    main_frame = ctk.CTkFrame(confirm_window, fg_color=COLORS["card_bg"])
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    icon_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    icon_frame.pack(pady=10)
    ctk.CTkLabel(
        icon_frame,
        text="❓",
        font=("Arial", 48),
        text_color=COLORS["warning"],
    ).pack()

    ctk.CTkLabel(
        main_frame,
        text=message,
        font=("Arial", 12),
        text_color=COLORS["text"],
        wraplength=350,
        justify="center",
    ).pack(pady=(0, 30))

    result = [False]

    def on_yes():
        result[0] = True
        confirm_window.destroy()

    def on_no():
        result[0] = False
        confirm_window.destroy()

    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack()

    yes_button = create_button(
        button_frame,
        "Da",
        command=on_yes,
        style="success",
        width=80,
    )
    yes_button.pack(side="left", padx=10)

    no_button = create_button(
        button_frame,
        "Nu",
        command=on_no,
        style="error",
        width=80,
    )
    no_button.pack(side="left", padx=10)

    no_button.focus_set()

    confirm_window.bind('<Return>', lambda e: on_yes())
    confirm_window.bind('<Escape>', lambda e: on_no())

    confirm_window.wait_window()
    return result[0]
