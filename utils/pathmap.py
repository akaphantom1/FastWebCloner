"""
PathMapper: mapare URL-uri (pagini si resurse) la cai locale / linkuri relative.

Scop:
    * fiecare pagina -> folder/INDEX.html (friendly, Windows safe)
    * fiecare resursa -> director __res__/<tip>/... (sau structura originala)
    * curatare segmente: inlocuieste caractere invalide Windows (< > : " | ? *)
    * optional hash pentru segmente lungi sau cu alt URL inauntru (ex: u_https://...)
    * generare link relativ intre doua pagini locale (pentru rescriere in HTML)

Integrare cu:
    - ContentProcessor (foloseste rel_href() pentru rescriere linkuri interne)
    - ResourceDownloader (foloseste path_for_resource() pentru fisiere)
    - write_root_index_auto() (trecere directa la pagina start)
"""

from __future__ import annotations

import os
import hashlib
from urllib.parse import urlparse, unquote, urlsplit, urlunsplit
from typing import Optional

# caractere invalide Windows
_INVALID_CHARS = '<>:"|?*'
_MAX_SEG_LEN = 80


def _clean_segment(seg: str, max_len: int = _MAX_SEG_LEN) -> str:
    """Curata un segment de path pentru a fi safe pe Windows."""
    if not seg:
        return "file"

    # decode %xx
    seg = unquote(seg)

    # inlocuieste separatori
    seg = seg.replace("\\", "_").replace("/", "_")

    # daca segmentul contine alt URL (http:, https:)
    low = seg.lower()
    if "http://" in low or "https://" in low:
        h = hashlib.md5(seg.encode("utf-8", errors="ignore")).hexdigest()[:16]
        seg = f"url-{h}"

    # caractere invalide
    for ch in _INVALID_CHARS:
        seg = seg.replace(ch, "_")

    # curatari suplimentare
    seg = seg.strip().strip(".")  # fara spatii/puncte terminale

    if not seg:
        seg = "file"

    # limiteaza lungimea
    if len(seg) > max_len:
        root, ext = os.path.splitext(seg)
        h = hashlib.md5(seg.encode("utf-8", errors="ignore")).hexdigest()[:8]
        if ext:
            seg = f"{root[:max_len - len(ext) - 9]}-{h}{ext}"
        else:
            seg = f"{root[:max_len - 9]}-{h}"

    return seg


def _safe_ext_from_url_path(path: str) -> str:
    """Returneaza extensia din path (daca are), altfel string gol."""
    _, ext = os.path.splitext(path)
    return ext.lower()


def _default_ext_for_mime(content_type: Optional[str]) -> str:
    """Fallback: deduce extensie din tip MIME (daca il avem)."""
    if not content_type:
        return ""
    ct = content_type.split(";")[0].strip().lower()
    if ct.startswith("image/"):
        return "." + ct.split("/", 1)[1]
    if ct == "text/css":
        return ".css"
    if ct in ("application/javascript", "text/javascript", "application/x-javascript"):
        return ".js"
    if ct in ("text/html", "application/xhtml+xml"):
        return ".html"
    return ""


def _strip_query_fragment(url: str) -> str:
    """Scoate query & fragment pentru maparea la fisier."""
    s = urlsplit(url)
    return urlunsplit((s.scheme, s.netloc, s.path, "", ""))


def _is_page_path(path: str) -> bool:
    """Heuristic: decide daca path-ul pare pagina (vs resursa binara)."""
    ext = _safe_ext_from_url_path(path)
    if not ext:
        return True
    return ext in (".html", ".htm", ".xhtml", ".php", ".asp", ".aspx", ".jsp")


class PathMapper:
    """
    Creeaza mapari URL → cale locala (absoluta) + link relativ intre pagini.
    """

    def __init__(self, base_dir: str, resources_root: str = "__res__"):
        self.base_dir = os.path.abspath(base_dir)
        self.resources_root = resources_root

    # ------------------------------------------------------------------ #
    # Paginile
    # ------------------------------------------------------------------ #
    def path_for_page(self, page_url: str) -> str:
        """
        Returneaza calea locala (absoluta) pentru pagina data.
        Folosim <basedir>/<domeniu>/<path...>/index.html
        """
        parsed = urlparse(_strip_query_fragment(page_url))
        host = _clean_segment(parsed.netloc) if parsed.netloc else "root"

        # extrage segmente din path
        raw_parts = [p for p in parsed.path.split("/") if p]
        parts_clean = [_clean_segment(p) for p in raw_parts]

        # folder final
        folder = os.path.join(self.base_dir, host, *parts_clean)
        # asigura extensie .html
        return os.path.join(folder, "index.html")

    # ------------------------------------------------------------------ #
    # Resurse
    # ------------------------------------------------------------------ #
    def path_for_resource(
        self,
        resource_url: str,
        mime_type: Optional[str] = None,
        source_page_url: Optional[str] = None,
    ) -> str:
        """
        Returneaza calea locala (absoluta) pentru o resursa (imagine/js/css/etc.).
        Grupam dupa domeniul resursei, in subdir __res__.
        """
        parsed = urlparse(_strip_query_fragment(resource_url))
        host = _clean_segment(parsed.netloc) if parsed.netloc else "ext"

        # segmente din path
        raw_parts = [p for p in parsed.path.split("/") if p]
        parts_clean = [_clean_segment(p) for p in raw_parts]

        # nume fisier
        if parts_clean:
            fname = parts_clean[-1]
            dir_parts = parts_clean[:-1]
        else:
            fname = host  # fallback
            dir_parts = []

        # extensie
        ext = _safe_ext_from_url_path(fname)
        if not ext:
            ext = _default_ext_for_mime(mime_type) or ".bin"
            fname = _clean_segment(fname) + ext

        # reconstruieste
        res_dir = os.path.join(self.base_dir, self.resources_root, host, *dir_parts)
        return os.path.join(res_dir, fname)

    # ------------------------------------------------------------------ #
    # Relative HREF intre doua pagini
    # ------------------------------------------------------------------ #
    def rel_href(self, from_page_url: str, to_url: str, is_page: bool = False) -> str:
        """
        Returneaza un link relativ din pagina `from_page_url` catre `to_url`.
        Daca `is_page=True`, presupunem ca `to_url` e pagina (index.html).
        Daca domeniile difera -> intoarcem `to_url` (link absolut).
        """
        # determina domenii:
        f = urlparse(from_page_url)
        t = urlparse(to_url)
        if f.netloc.lower().lstrip("www.") != t.netloc.lower().lstrip("www."):
            # alt domeniu -> pastram absolut
            return to_url

        # cai locale absolute
        from_path = self.path_for_page(from_page_url)
        if is_page:
            to_path = self.path_for_page(to_url)
        else:
            # incercam intai ca pagina; daca to_url are extensie -> resursa
            if _is_page_path(t.path):
                to_path = self.path_for_page(to_url)
            else:
                to_path = self.path_for_resource(to_url)

        # calculeaza relativ
        rel = os.path.relpath(to_path, os.path.dirname(from_path))
        # Normalizeaza la / pentru HTML
        return rel.replace(os.sep, "/")
