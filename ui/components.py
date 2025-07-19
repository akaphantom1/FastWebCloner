# ui/components.py
# -*- coding: utf-8 -*-
"""
Componente reutilizabile pentru interfata utilizator
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from utils.constants import TEXTS, COLORS
from config import UI_PADDING, CARD_PADDING, BUTTON_HEIGHT, ENTRY_HEIGHT

# Tema globala
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# --------------------------------------------------------------------------- #
# Elemente UI de baza
# --------------------------------------------------------------------------- #
def create_card_frame(parent, title: str | None = None):
    """Frame stil card."""
    if title:
        frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=COLORS.get("card_bg", COLORS["secondary_bg"]))
        title_frame = ctk.CTkFrame(frame, fg_color="transparent", height=40)
        title_frame.pack(fill="x", padx=15, pady=(10, 0))
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=("Arial", 14, "bold"),
            text_color=COLORS.get("accent", COLORS["button"]),
            anchor="w",
        ).pack(side="left")
        return frame
    return ctk.CTkFrame(parent, corner_radius=12, fg_color=COLORS.get("card_bg", COLORS["secondary_bg"]))


def create_label(parent, text: str, font=("Arial", 11), **kwargs):
    # Daca apelantul da text_color, nu vrem dublare.
    txt_color = kwargs.pop("text_color", COLORS["text"])
    anchor = kwargs.pop("anchor", "w")
    return ctk.CTkLabel(
        parent,
        text=text,
        font=font,
        text_color=txt_color,
        anchor=anchor,
        **kwargs,
    )


def create_entry(parent, textvariable=None, placeholder: str = "", **kwargs):
    return ctk.CTkEntry(
        parent,
        textvariable=textvariable,
        placeholder_text=placeholder,
        font=("Arial", 11),
        fg_color=COLORS["entry_bg"],
        corner_radius=8,
        **kwargs,
    )


def create_button(parent, text: str, command=None, style: str = "primary", **kwargs):
    """
    Buton modern cu efecte de hover. Permite override din kwargs.
    Eliminam orice parametri potential dubli (height, width, text_color, fg_color, hover_color etc.)
    pentru a evita eroarea "multiple values for keyword argument".
    """
    color_map = {
        "primary": COLORS["button"],
        "success": COLORS["success"],
        "warning": COLORS["warning"],
        "error": COLORS["error"],
    }
    hover_map = {
        "primary": COLORS["hover"],
        "success": "#0E9D6E",
        "warning": "#E58B0B",
        "error": "#DC3A3A",
    }

    fg_color = kwargs.pop("fg_color", color_map.get(style, COLORS["button"]))
    hover_color = kwargs.pop("hover_color", hover_map.get(style, COLORS["hover"]))
    txt_color = kwargs.pop("text_color", COLORS["button_text"])
    h = kwargs.pop("height", BUTTON_HEIGHT)
    w = kwargs.pop("width", None)

    # parametri nesuportati in unele versiuni
    kwargs.pop("border_width", None)
    kwargs.pop("border_color", None)

    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        font=("Arial", 11, "bold"),
        fg_color=fg_color,
        hover_color=hover_color,
        text_color=txt_color,
        corner_radius=8,
        height=h,
        width=w,
        **kwargs,
    )


def create_checkbox(parent, text: str, variable, **kwargs):
    # parametri nesuportati eliminati
    kwargs.pop("border_width", None)
    kwargs.pop("border_color", None)
    kwargs.pop("checkbox_width", None)
    kwargs.pop("checkbox_height", None)
    return ctk.CTkCheckBox(
        parent,
        text=text,
        variable=variable,
        font=("Arial", 11),
        fg_color=COLORS["button"],
        hover_color=COLORS["hover"],
        **kwargs,
    )


def create_radiobutton(parent, text: str, variable, value, **kwargs):
    kwargs.pop("border_width", None)
    kwargs.pop("border_color", None)
    kwargs.pop("radiobutton_width", None)
    kwargs.pop("radiobutton_height", None)
    return ctk.CTkRadioButton(
        parent,
        text=text,
        variable=variable,
        value=value,
        font=("Arial", 11),
        fg_color=COLORS["button"],
        hover_color=COLORS["hover"],
        **kwargs,
    )


def create_progress_bar(parent, **kwargs):
    style = ttk.Style()
    style.configure(
        "Modern.Horizontal.TProgressbar",
        background=COLORS["progress"],
        troughcolor=COLORS["secondary_bg"],
        bordercolor=COLORS["secondary_bg"],
        thickness=12,
        troughrelief="flat",
        relief="flat",
    )
    return ttk.Progressbar(parent, style="Modern.Horizontal.TProgressbar", **kwargs)


def create_scrolled_text(parent, height=5, **kwargs):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="both", expand=True)

    text = tk.Text(
        frame,
        height=height,
        font=("Arial", 10),
        bg=COLORS["entry_bg"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["border"],
        **kwargs,
    )
    text.pack(side="left", fill="both", expand=True, padx=(0, 2))

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
    scrollbar.pack(side="right", fill="y")
    text.config(yscrollcommand=scrollbar.set)
    return text


# --------------------------------------------------------------------------- #
# Sectiuni compuse
# --------------------------------------------------------------------------- #
def create_header_section(parent, about_callback):
    header = ctk.CTkFrame(parent, height=80, corner_radius=0, fg_color=COLORS["button"])
    header.pack_propagate(False)

    canvas = tk.Canvas(header, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_rectangle(0, 0, 2000, 80, fill=COLORS["button"], outline="")

    title = ctk.CTkLabel(
        header,
        text=TEXTS["title"],
        font=("Arial", 24, "bold"),
        text_color="#FFFFFF",
    )
    title.place(relx=0.5, rely=0.5, anchor="center")

    # hover_color trebuie sa fie un nume de culoare valid (nu cu alpha).
    about_btn = create_button(
        header,
        TEXTS["about"],
        command=about_callback,
        width=100,
        fg_color="transparent",
        hover_color="#FFFFFF",
    )
    about_btn.place(relx=0.95, rely=0.5, anchor="e")
    return header


def create_input_section(parent, url_var, base_url_var, output_folder_var, clone_type_var, on_type_change):
    card = create_card_frame(parent, "📝 Date de Intrare")
    card.pack(fill="x", padx=UI_PADDING, pady=UI_PADDING)

    body = ctk.CTkFrame(card, fg_color="transparent")
    body.pack(fill="x", padx=CARD_PADDING, pady=CARD_PADDING)

    create_label(body, TEXTS["url_label"]).pack(fill="x", pady=(0, 5))
    create_entry(body, textvariable=url_var, placeholder=TEXTS["url_placeholder"]).pack(fill="x", pady=(0, 15))

    create_label(body, TEXTS["base_url_label"]).pack(fill="x", pady=(0, 5))
    create_entry(body, textvariable=base_url_var, placeholder=TEXTS["base_url_placeholder"]).pack(fill="x", pady=(0, 15))

    create_label(body, TEXTS["output_folder_label"]).pack(fill="x", pady=(0, 5))
    create_entry(body, textvariable=output_folder_var, placeholder=TEXTS["output_folder_placeholder"]).pack(fill="x", pady=(0, 15))

    type_frame = ctk.CTkFrame(body, fg_color="transparent")
    type_frame.pack(fill="x", pady=(10, 0))

    create_label(type_frame, TEXTS["clone_type"]).pack(side="left", padx=(0, 20))
    create_radiobutton(type_frame, TEXTS["single_page"], clone_type_var, "single", command=on_type_change).pack(side="left", padx=10)
    create_radiobutton(type_frame, TEXTS["entire_domain"], clone_type_var, "domain", command=on_type_change).pack(side="left", padx=10)

    return card


def create_crawl_section(parent, depth_var, pages_var, same_domain_var, subdomains_var):
    card = create_card_frame(parent, TEXTS["crawl_settings"])
    card.pack(fill="x", padx=UI_PADDING, pady=UI_PADDING)

    body = ctk.CTkFrame(card, fg_color="transparent")
    body.pack(fill="x", padx=CARD_PADDING, pady=CARD_PADDING)

    numeric_frame = ctk.CTkFrame(body, fg_color="transparent")
    numeric_frame.pack(fill="x", pady=(0, 15))

    depth_wrap = ctk.CTkFrame(numeric_frame, fg_color="transparent")
    depth_wrap.pack(side="left", padx=(0, 30))
    create_label(depth_wrap, TEXTS["max_depth"]).pack(anchor="w")
    depth_spin = ctk.CTkOptionMenu(
        depth_wrap,
        values=[str(i) for i in range(1, 21)],
        variable=depth_var,
        width=100,
        corner_radius=8,
        fg_color=COLORS["entry_bg"],
        button_color=COLORS["button"],
        button_hover_color=COLORS["hover"],
        state="disabled",
    )
    depth_spin.pack(pady=5)

    pages_wrap = ctk.CTkFrame(numeric_frame, fg_color="transparent")
    pages_wrap.pack(side="left")
    create_label(pages_wrap, TEXTS["max_pages"]).pack(anchor="w")
    pages_spin = ctk.CTkOptionMenu(
        pages_wrap,
        values=["100", "500", "1000", "5000", "10000"],
        variable=pages_var,
        width=100,
        corner_radius=8,
        fg_color=COLORS["entry_bg"],
        button_color=COLORS["button"],
        button_hover_color=COLORS["hover"],
        state="disabled",
    )
    pages_spin.pack(pady=5)

    domain_frame = ctk.CTkFrame(body, fg_color="transparent")
    domain_frame.pack(fill="x", pady=(0, 15))
    same_check = create_checkbox(domain_frame, TEXTS["same_domain_only"], same_domain_var, state="disabled")
    same_check.pack(side="left", padx=(0, 20))
    subdomain_check = create_checkbox(domain_frame, TEXTS["include_subdomains"], subdomains_var, state="disabled")
    subdomain_check.pack(side="left")

    create_label(body, TEXTS["exclude_patterns"], anchor="w").pack(fill="x", pady=(0, 5))
    exclude_text = create_scrolled_text(body, height=4)
    exclude_text.insert("1.0", TEXTS["exclude_placeholder"])

    widgets = {
        "depth_spin": depth_spin,
        "pages_spin": pages_spin,
        "same_check": same_check,
        "subdomain_check": subdomain_check,
        "exclude_text": exclude_text,
    }
    return card, widgets


def create_resource_section(parent, resource_vars):
    card = create_card_frame(parent, TEXTS["resource_settings"])
    card.pack(fill="x", padx=UI_PADDING, pady=UI_PADDING)

    body = ctk.CTkFrame(card, fg_color="transparent")
    body.pack(fill="x", padx=CARD_PADDING, pady=CARD_PADDING)

    resources = [
        ("images", TEXTS["include_images"]),
        ("css", TEXTS["include_css"]),
        ("js", TEXTS["include_js"]),
        ("fonts", TEXTS["include_fonts"]),
        ("videos", TEXTS["include_videos"]),
    ]

    for idx, (key, label) in enumerate(resources):
        row = idx // 2
        col = idx % 2
        create_checkbox(body, label, resource_vars[key]).grid(row=row, column=col, sticky="w", padx=10, pady=5)

    body.grid_columnconfigure(0, weight=1)
    body.grid_columnconfigure(1, weight=1)
    return card


def create_output_section(parent, zip_var, folder_var, on_change):
    card = create_card_frame(parent, TEXTS["output_settings"])
    card.pack(fill="x", padx=UI_PADDING, pady=UI_PADDING)

    body = ctk.CTkFrame(card, fg_color="transparent")
    body.pack(fill="x", padx=CARD_PADDING, pady=CARD_PADDING)

    create_checkbox(body, TEXTS["create_zip"], zip_var, command=on_change).pack(anchor="w", padx=10, pady=5)
    create_checkbox(body, TEXTS["keep_folder"], folder_var, command=on_change).pack(anchor="w", padx=10, pady=5)
    return card


def create_progress_section(parent):
    card = create_card_frame(parent, "📊 Progres")
    card.pack(fill="x", padx=UI_PADDING, pady=UI_PADDING)

    body = ctk.CTkFrame(card, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=CARD_PADDING, pady=CARD_PADDING)

    bar = create_progress_bar(body, length=400, mode="determinate")
    bar.pack(fill="x", pady=(0, 10))

    label = create_label(body, TEXTS["status_idle"], font=("Arial", 12))
    label.pack(pady=(0, 5))

    current = create_label(body, "", font=("Arial", 9))
    current.pack()
    return card, {"bar": bar, "label": label, "current": current}


def create_stats_section(parent):
    card = create_card_frame(parent, TEXTS["stats_title"])
    card.pack(fill="x", padx=UI_PADDING, pady=UI_PADDING)

    body = ctk.CTkFrame(card, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=CARD_PADDING, pady=CARD_PADDING)

    stats_frame = ctk.CTkFrame(body, fg_color=COLORS["secondary_bg"], corner_radius=8)
    stats_frame.pack(fill="both", expand=True)

    stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
    stats_grid.pack(padx=10, pady=10)

    stats_labels = {
        "pages": create_label(stats_grid, "📄 Pagini: 0/0", font=("Arial", 11)),
        "resources": create_label(stats_grid, "📦 Resurse: 0/0", font=("Arial", 11)),
        "errors": create_label(stats_grid, "⚠️ Erori: 0", font=("Arial", 11)),
        "time": create_label(stats_grid, "⏱️ Timp: 0s", font=("Arial", 11)),
    }

    stats_labels["pages"].grid(row=0, column=0, sticky="w", padx=10, pady=5)
    stats_labels["resources"].grid(row=0, column=1, sticky="w", padx=10, pady=5)
    stats_labels["errors"].grid(row=1, column=0, sticky="w", padx=10, pady=5)
    stats_labels["time"].grid(row=1, column=1, sticky="w", padx=10, pady=5)

    details_btn = create_button(stats_frame, "Detalii Complete", width=150, height=30)
    details_btn.pack(pady=(0, 10))

    return card, {"labels": stats_labels, "details_btn": details_btn}
