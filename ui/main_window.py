# ui/main_window.py
# -*- coding: utf-8 -*-
"""
Fereastra principala a aplicatiei FastWebCloner
"""

from __future__ import annotations

import logging
import os
import shutil
import threading
import time
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

import config
from config import (
    APP_NAME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_PAGES,
)
from core.crawler import DomainCrawler
from core.downloader import ResourceDownloader
from core.processor import ContentProcessor
from ui.components import (
    create_header_section,
    create_input_section,
    create_crawl_section,
    create_resource_section,
    create_output_section,
    create_progress_section,
    create_stats_section,
)
from ui.dialogs import show_about_dialog
from utils.constants import COLORS, TEXTS
from utils.helpers import format_time, get_unique_folder_name, is_valid_url
from utils.launcher import write_root_index_auto
from utils.pathmap import PathMapper

logger = logging.getLogger(__name__)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class WebClonerApp:
    """Clasa principala pentru interfata FastWebCloner."""

    # --------------------------- init / UI build ---------------------- #
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(TEXTS["window_title"])
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.configure(fg_color=COLORS["bg"])

        self._setup_variables()
        self._build_modern_ui()
        self._center_window()

    def _setup_variables(self):
        self.url_var = ctk.StringVar()
        self.base_url_var = ctk.StringVar()
        self.output_folder_var = ctk.StringVar(value=TEXTS["default_folder"])

        self.clone_type_var = ctk.StringVar(value="single")

        self.depth_var = ctk.StringVar(value=str(DEFAULT_MAX_DEPTH))
        self.pages_var = ctk.StringVar(value=str(DEFAULT_MAX_PAGES))
        self.same_domain_var = ctk.IntVar(value=1)
        self.subdomains_var = ctk.IntVar(value=0)

        self.resource_vars = {
            "images": ctk.IntVar(value=1),
            "css": ctk.IntVar(value=1),
            "js": ctk.IntVar(value=1),
            "fonts": ctk.IntVar(value=1),
            "videos": ctk.IntVar(value=0),
        }

        self.zip_var = ctk.IntVar(value=1)
        self.folder_var = ctk.IntVar(value=1)

        # runtime
        self.crawling_thread: threading.Thread | None = None
        self.start_time: float | None = None

    # ------------------------- build sections ------------------------- #
    def _build_modern_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.header_frame = create_header_section(self.root, self.show_about)
        self.header_frame.grid(row=0, column=0, sticky="ew")

        self._setup_scrollable_area()
        self._create_main_sections()
        self._create_action_buttons()

    def _setup_scrollable_area(self):
        scroll_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_rowconfigure(0, weight=1)

        self.canvas = ctk.CTkCanvas(scroll_frame, bg=COLORS["bg"], highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(
            scroll_frame, orientation="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _create_main_sections(self):
        self.input_section = create_input_section(
            self.scrollable_frame,
            self.url_var,
            self.base_url_var,
            self.output_folder_var,
            self.clone_type_var,
            self.on_clone_type_change,
        )
        self.input_section.pack(fill="x", pady=10)

        self.crawl_section, self.crawl_widgets = create_crawl_section(
            self.scrollable_frame,
            self.depth_var,
            self.pages_var,
            self.same_domain_var,
            self.subdomains_var,
        )
        self.crawl_section.pack(fill="x", pady=10)

        self.resource_section = create_resource_section(
            self.scrollable_frame, self.resource_vars
        )
        self.resource_section.pack(fill="x", pady=10)

        self.output_section = create_output_section(
            self.scrollable_frame, self.zip_var, self.folder_var, self.on_output_change
        )
        self.output_section.pack(fill="x", pady=10)

        self.progress_section, self.progress_widgets = create_progress_section(
            self.scrollable_frame
        )
        self.progress_section.pack(fill="x", pady=10)

        self.stats_section, self.stats_widgets = create_stats_section(self.scrollable_frame)
        self.stats_section.pack(fill="x", pady=10)

    def _create_action_buttons(self):
        btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        self.clone_btn = ctk.CTkButton(
            btn_frame,
            text=TEXTS["clone_button"],
            fg_color=COLORS["success"],
            hover_color="#0E9D6E",
            text_color=COLORS["button_text"],
            command=self.start_cloning,
            width=200,
            height=50,
            corner_radius=8,
        )
        self.clone_btn.pack(side="left", padx=10)

        self.pause_btn = ctk.CTkButton(
            btn_frame,
            text=TEXTS["pause"],
            fg_color=COLORS["warning"],
            hover_color="#E58B0B",
            text_color=COLORS["button_text"],
            command=self.toggle_pause,
            width=150,
            height=50,
            corner_radius=8,
            state="disabled",
        )
        self.pause_btn.pack(side="left", padx=10)

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text=TEXTS["cancel"],
            fg_color=COLORS["error"],
            hover_color="#DC3A3A",
            text_color=COLORS["button_text"],
            command=self.cancel_cloning,
            width=150,
            height=50,
            corner_radius=8,
            state="disabled",
        )
        self.cancel_btn.pack(side="left", padx=10)

    def _center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ------------------------ UI callbacks ---------------------------- #
    def on_clone_type_change(self):
        is_domain = self.clone_type_var.get() == "domain"
        state = "normal" if is_domain else "disabled"
        for wid in ("depth_spin", "pages_spin", "same_check", "subdomain_check"):
            try:
                self.crawl_widgets[wid].configure(state=state)
            except Exception:
                pass

    def on_output_change(self):
        if not self.zip_var.get() and not self.folder_var.get():
            self.zip_var.set(1)

    # ------------------------ progres UI ------------------------------ #
    def update_progress(self, value: int, message: str, current_url: str | None = None):
        """
        value:
            -1 = doar mesaj
             0 = reset
            1..100 = procent
        """
        if value >= 0:
            self.progress_widgets["bar"].configure(value=value)
        self.progress_widgets["label"].configure(text=message)

        if current_url:
            trunc = current_url[:80] + "..." if len(current_url) > 80 else current_url
            self.progress_widgets["current"].configure(text=TEXTS["current_url"].format(trunc))
        self.root.update_idletasks()

    def update_stats(self, **kw):
        lbls = self.stats_widgets["labels"]
        if {"pages_found", "pages_processed"} <= kw.keys():
            lbls["pages"].configure(
                text=f"📄 {kw['pages_processed']}/{kw['pages_found']}"
            )
        if {"resources_downloaded", "total_resources"} <= kw.keys():
            lbls["resources"].configure(
                text=f"📦 {kw['resources_downloaded']}/{kw['total_resources']}"
            )
        if "errors" in kw:
            lbls["errors"].configure(text=f"⚠️ {kw['errors']}")
        if "start_time" in kw and kw["start_time"]:
            elapsed = time.time() - kw["start_time"]
            lbls["time"].configure(text=f"⏱️ {format_time(elapsed)}")
        self.root.update_idletasks()

    # -------------------- control buttons ---------------------------- #
    def start_cloning(self):
        url = self.url_var.get().strip()
        if not is_valid_url(url):
            messagebox.showerror(TEXTS["error"], TEXTS["domain_required"])
            return
        if not self.zip_var.get() and not self.folder_var.get():
            messagebox.showerror(TEXTS["error"], TEXTS["output_option_required"])
            return

        self.clone_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.cancel_btn.configure(state="normal")

        config.PAUSED = False
        config.CANCELLED = False

        self.crawling_thread = threading.Thread(target=self._cloning_worker, daemon=True)
        self.crawling_thread.start()

    def toggle_pause(self):
        config.PAUSED = not config.PAUSED
        self.pause_btn.configure(text=TEXTS["resume" if config.PAUSED else "pause"])
        self.update_progress(-1, TEXTS["process_paused" if config.PAUSED else "process_resumed"])

    def cancel_cloning(self):
        if messagebox.askyesno(TEXTS["confirm"], TEXTS["cancel_confirm"]):
            config.CANCELLED = True
            self.update_progress(0, TEXTS["process_cancelled"])
            self._reset_buttons()

    # ---------------- worker thread (crawl→download→process) ---------- #
    def _cloning_worker(self):
        try:
            # -------------------------------------------------- params
            url = self.url_var.get().strip()
            base_url = self.base_url_var.get().strip() or url
            output_folder = self.output_folder_var.get().strip()

            clone_type = self.clone_type_var.get()
            max_depth = int(self.depth_var.get()) if clone_type == "domain" else 0
            max_pages = int(self.pages_var.get()) if clone_type == "domain" else 1
            same_domain = bool(self.same_domain_var.get())
            include_sub = bool(self.subdomains_var.get())

            exclude_text = self.crawl_widgets["exclude_text"]
            exclude_patterns = [
                p.strip() for p in exclude_text.get("1.0", "end").strip().splitlines() if p.strip()
            ]

            res_types = {k: bool(v.get()) for k, v in self.resource_vars.items()}

            # -------------------------------------------------- run
            self._execute_cloning(
                url,
                base_url,
                output_folder,
                max_depth,
                max_pages,
                same_domain,
                include_sub,
                exclude_patterns,
                res_types,
            )
        except Exception as e:
            logger.error("Eroare în thread‑ul de clonare: %s", e, exc_info=True)
            msg = str(e)                                   # <-- salveaza
            self.root.after(0, lambda m=msg: self._handle_error(m))


    # ---------------- pipeline logic ---------------------------------- #
    def _execute_cloning(
        self,
        url,
        base_url,
        output_folder,
        max_depth,
        max_pages,
        same_domain_only,
        include_subdomains,
        exclude_patterns,
        resource_types,
    ):
        start_time = time.time()
        unique_out = get_unique_folder_name(output_folder)
        os.makedirs(unique_out, exist_ok=True)

        # ---------- Crawl
        self.root.after(
            0, lambda: self.update_progress(10, TEXTS["status_crawling"], current_url=url)
        )
        crawler = DomainCrawler(
            url,
            max_depth,
            max_pages,
            same_domain_only,
            include_subdomains,
            exclude_patterns,
        )

        def crawl_cb(v, m, u):
            self.root.after(0, lambda: self.update_progress(v, m, u))
            self.root.after(
                0,
                lambda: self.update_stats(
                    pages_found=crawler.pages_found,
                    pages_processed=crawler.pages_processed,
                    resources_downloaded=0,
                    total_resources=len(crawler.resources),
                    errors=len(crawler.errors),
                    start_time=start_time,
                ),
            )

        crawl_result = crawler.crawl(crawl_cb)

        # accepta 2 sau 3 valori – compatibil
        if len(crawl_result) == 3:
            pages, resources, res_src = crawl_result
        elif len(crawl_result) == 2:
            pages, resources = crawl_result
            # toate resursele le mapam la pagina de start (fallback simplu);
            # poti construi alta mapare daca ai nevoie.
            res_src = {r: url for r in resources}
        else:
            raise RuntimeError(
                f"DomainCrawler.crawl() a returnat {len(crawl_result)} valori – nu 2 sau 3."
            )


        # ---------- PathMapper si ContentProcessor
        pathmap = PathMapper(unique_out)
        processor = ContentProcessor(unique_out, base_url=base_url, pathmap=pathmap)  # <‑‑ FIX

        from urllib.parse import urlparse
        processor.site_folder = urlparse(base_url).netloc or "site"

        self.root.after(0, lambda: self.update_progress(30, TEXTS["status_processing"]))

        total_pages = len(pages) or 1
        for idx, (page_url, html) in enumerate(pages.items(), start=1):
            if config.CANCELLED:
                break
            html_out = processor.process_html(html, page_url)
            local_path = pathmap.path_for_page(page_url)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(html_out)
            prog_val = 30 + int((idx / total_pages) * 30)
            self.root.after(
                0,
                lambda p=prog_val: self.update_progress(
                    p, TEXTS["status_processing"], current_url=page_url
                ),
            )

        if config.CANCELLED:
            shutil.rmtree(unique_out, ignore_errors=True)
            self.root.after(0, lambda: self.complete_cloning(False, None, None))
            return

        # ---------- Download resurse
        self.root.after(0, lambda: self.update_progress(60, TEXTS["status_downloading"]))
        downloader = ResourceDownloader(unique_out, pathmap=pathmap, resource_types=resource_types)

        def dl_cb(percent, msg):
            bar_val = 60 + int((percent / 100.0) * 30)
            self.root.after(0, lambda: self.update_progress(bar_val, msg))
            self.root.after(
                0,
                lambda: self.update_stats(
                    pages_found=crawler.pages_found,
                    pages_processed=crawler.pages_processed,
                    resources_downloaded=downloader.downloaded_count,
                    total_resources=len(resources),
                    errors=len(crawler.errors) + downloader.failed_count,
                    start_time=start_time,
                ),
            )

        downloader.download_all(resources, res_src, progress_callback=dl_cb)

        if config.CANCELLED:
            shutil.rmtree(unique_out, ignore_errors=True)
            self.root.after(0, lambda: self.complete_cloning(False, None, None))
            return

        # ---------- Index root
        start_page = url if url in pages else next(iter(pages), None)
        if start_page:
            try:
                write_root_index_auto(unique_out, start_page, pathmap=pathmap)
            except Exception as e:
                logger.warning("Nu am putut crea index root: %s", e)

        # ---------- Arhivare ZIP (optional)
        zip_path = None
        if self.zip_var.get():
            self.root.after(0, lambda: self.update_progress(95, TEXTS["status_compressing"]))
            try:
                zip_path = downloader.create_archive(unique_out)
            except Exception as e:
                logger.error("Eroare creare arhiva: %s", e, exc_info=True)

            if not self.folder_var.get():
                folder_ref = None
                shutil.rmtree(unique_out, ignore_errors=True)
            else:
                folder_ref = unique_out
        else:
            folder_ref = unique_out

        # ---------- Success
        self.root.after(0, lambda: self.update_progress(100, TEXTS["status_completed"]))
        self.root.after(0, lambda: self.complete_cloning(True, zip_path, folder_ref))

    # -------------------- finalize / error / states ------------------- #
    def complete_cloning(self, ok: bool, zip_path: str | None, folder_path: str | None):
        self._reset_buttons()
        if ok:
            if self.zip_var.get() and self.folder_var.get():
                message = TEXTS["both_created"].format(zip_path, folder_path)
            elif self.zip_var.get():
                message = TEXTS["zip_created"].format(zip_path)
            else:
                message = TEXTS["folder_kept"].format(folder_path)
            messagebox.showinfo(TEXTS["success"], message)

    def _reset_buttons(self):
        self.clone_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text=TEXTS["pause"])
        self.cancel_btn.configure(state="disabled")

    def _handle_error(self, msg: str):
        self._reset_buttons()
        messagebox.showerror(TEXTS["error"], f"{TEXTS['error']}: {msg}")
        self.update_progress(0, TEXTS["error"])

    # -------------------- about / run mainloop ------------------------ #
    def show_about(self):
        show_about_dialog(self.root)

    def run(self):
        logger.info("Pornire %s", APP_NAME)
        self.root.mainloop()


if __name__ == "__main__":
    WebClonerApp().run()
