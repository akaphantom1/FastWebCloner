# core/processor.py
# -*- coding: utf-8 -*-
"""
Procesarea si adaptarea continutului HTML/CSS pentru salvare offline.

<OUTPUT>/
    __res__/
        images/  styles/  scripts/  other/
    www.example.com/           # doar paginile .html rescrise
        index.html
        about/index.html
        contact.html

Pentru orice resursa statica, URI‑ul din HTML/CSS devine:
/__res__/subfolder/fisier.ext
"""

from __future__ import annotations

import logging
import os
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment

from utils.constants import EXCLUDED_EXTENSIONS, RESOURCE_TYPES
from utils.helpers import ensure_dir, ext_from_url, write_text_file
from utils.pathmap import PathMapper

logger = logging.getLogger(__name__)

# Scheme pe care le ignoram complet
_IGNORE_SCHEMES = (
    "mailto:", "tel:", "javascript:", "data:", "#",
    "about:", "chrome:", "edge:", "file:",
)


def _choose_subdir(ext: str) -> str:
    """Întoarce subfolderul din __res__ in functie de extensie."""
    for name, exts in RESOURCE_TYPES.items():
        if ext in exts:
            return name
    return "other"

def _is_external(url: str, base_url: str) -> bool:
    """True daca url este in alt domeniu fata de base_url."""
    try:
        pu = urlparse(url)
        pb = urlparse(base_url)
        return pu.netloc.lower().lstrip("www.") != pb.netloc.lower().lstrip("www.")
    except Exception:
        return True

def _rewrite_css_urls(css_text: str, source_url: str, convert_func) -> str:
    """Rescrie url() si @import din CSS."""
    def _repl_url(m):
        raw = m.group(1).strip('\'"')
        return f'url("{convert_func(raw, source_url, False)}")'

    css_text = re.sub(
        r"url\s*\(\s*['\"]?([^'\"()]+)['\"]?\s*\)",
        _repl_url,
        css_text,
        flags=re.IGNORECASE,
    )

    def _repl_import(m):
        raw = m.group(1).strip('\'"')
        return f'@import "{convert_func(raw, source_url, False)}"'

    css_text = re.sub(
        r"@import\s+['\"]([^'\"]+)['\"]",
        _repl_import,
        css_text,
        flags=re.IGNORECASE,
    )
    return css_text


class ContentProcessor:
    """
    Proceseaza pagini HTML si fisiere CSS pentru snapshot offline.
    """

    def __init__(
        self,
        output_dir: str,
        base_url: Optional[str] = None,
        pathmap: Optional[PathMapper] = None,
        inject_base: bool = False,
    ):
        self.output_dir = ensure_dir(output_dir)
        self.base_url = base_url
        self.pathmap = pathmap
        self.inject_base = inject_base

        # setat la fiecare process_pages()
        self.site_folder: str | None = None
        self.res_folder = "__res__"               # <‑‑ folder unic pt resurse

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def process_pages(self, pages: dict[str, str], domain_root: str) -> dict[str, str]:
        """
        Proceseaza si salveaza toate paginile HTML.
        """
        self.site_folder = urlparse(domain_root).netloc or "site"
        saved: dict[str, str] = {}
        for url, html in pages.items():
            processed_html = self.process_html(html, url, domain_root)
            dest_path = self._local_html_path(url)
            ensure_dir(os.path.dirname(dest_path))
            write_text_file(dest_path, processed_html)
            saved[url] = dest_path
            logger.debug("Page saved %s -> %s", url, dest_path)
        return saved

    def process_html(
        self,
        html_content: str,
        source_url: str,
        new_base_url: Optional[str] = None,
    ) -> str:
        """Proceseaza o singura pagina HTML."""
        soup = BeautifulSoup(html_content, "html.parser")

        if self.inject_base and new_base_url:
            self._ensure_base_tag(soup, new_base_url)

        self._rewrite_links_and_resources(soup, source_url)
        soup.insert(0, Comment(f" Cloned from: {source_url} "))
        return str(soup)

    def process_css(self, css_content: str, source_url: str) -> str:
        return _rewrite_css_urls(css_content, source_url, self._convert_url)

    # ------------------------------------------------------------------ #
    # Path helpers
    # ------------------------------------------------------------------ #
    def _local_html_path(self, url: str) -> str:
        assert self.site_folder is not None
        p = urlparse(url)
        path = p.path or "/"
        if path.endswith("/"):
            path += "index.html"
        return os.path.join(self.output_dir, self.site_folder, path.lstrip("/"))

    # ------------------------------------------------------------------ #
    # HTML rewrite
    # ------------------------------------------------------------------ #
    def _ensure_base_tag(self, soup: BeautifulSoup, href: str):
        base_tag = soup.find("base")
        if base_tag:
            base_tag["href"] = href
        else:
            base = soup.new_tag("base", href=href)
            (soup.head or soup.insert(0, soup.new_tag("head"))).insert(0, base)

    def _rewrite_links_and_resources(self, soup: BeautifulSoup, source_url: str):
        # linkuri pagini
        for tag in soup.find_all(["a", "area", "form"]):
            attr = "href" if tag.name != "form" else "action"
            if tag.get(attr):
                tag[attr] = self._convert_url(tag[attr], source_url, is_page=True)

        # resurse statice
        for tag in soup.find_all(["img", "input", "source", "link", "script"]):
            attr = "src" if tag.name in ("img", "input", "source", "script") else "href"
            if tag.get(attr):
                tag[attr] = self._convert_url(tag[attr], source_url, is_page=False)
            # srcset special
            if tag.name in ("img", "source") and tag.get("srcset"):
                tag["srcset"] = self._rewrite_srcset(tag["srcset"], source_url)

        # stil inline + <style>
        for tag in soup.find_all(style=True):
            tag["style"] = _rewrite_css_urls(tag["style"], source_url, self._convert_url)
        for style_tag in soup.find_all("style"):
            if style_tag.string:
                style_tag.string = _rewrite_css_urls(style_tag.string, source_url, self._convert_url)

    def _rewrite_srcset(self, srcset: str, source_url: str) -> str:
        out = []
        for part in srcset.split(","):
            p = part.strip()
            if not p:
                continue
            if " " in p:
                u, desc = p.split(" ", 1)
                out.append(f"{self._convert_url(u, source_url, False)} {desc}")
            else:
                out.append(self._convert_url(p, source_url, False))
        return ", ".join(out)

    # ------------------------------------------------------------------ #
    # Convertor URL -> link local
    # ------------------------------------------------------------------ #
    def _convert_url(self, raw_url: str, source_url: str, is_page: bool) -> str:
        if not raw_url:
            return raw_url
        if raw_url.lower().startswith(_IGNORE_SCHEMES):
            return raw_url

        abs_url = urljoin(source_url, raw_url)
        ext = ext_from_url(abs_url)            # ① <‑‑ adaugi linia asta

        # ----- resursa statica ------------------------------------------
        if not is_page and ext:                # ② modifici condiţia
            if ext in EXCLUDED_EXTENSIONS:     # fişiere pe care NU le vrei (.zip, .exe…)
                return raw_url

            sub  = _choose_subdir(ext)
            name = os.path.basename(urlparse(abs_url).path) or f"file{ext}"
            abs_dest = os.path.join(self.output_dir, self.res_folder, sub, name)

            page_dir = os.path.dirname(self._local_html_path(source_url))
            return os.path.relpath(abs_dest, page_dir).replace(os.sep, "/")



        # link pagina interna (daca avem PathMapper)
        if self.pathmap and not _is_external(abs_url, self.base_url or source_url):
            try:
                return self.pathmap.rel_href(source_url, abs_url, is_page=True)
            except Exception:
                pass

        # fallback: absolut
        return abs_url
