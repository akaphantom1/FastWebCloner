# utils/helpers.py
"""
Helper utilities folosite de FastWebCloner.
Acest fișier conține:
    • gestiune directoare / output
    • formatare dimensiune, timp
    • validare / curățare URL
    • hash fișier
    • estimare timp download
    • funcții utilitare diverse

Tot codul este ASCII only.
"""

from __future__ import annotations

import hashlib
import logging
import os
import pathlib
import re
from urllib.parse import urljoin, urlparse, quote, unquote

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Directoare și fișiere
# ---------------------------------------------------------------------------


def ensure_dir(path: str) -> str:
    """
    Creează directorul (recursiv) dacă nu există și întoarce calea absolută.
    """
    p = pathlib.Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return str(p.resolve())


def get_unique_folder_name(base_name: str) -> str:
    """
    Generează un nume unic: folder, folder_1, folder_2, ...
    """
    if not os.path.exists(base_name):
        return base_name
    counter = 1
    while True:
        new_name = f"{base_name}_{counter}"
        if not os.path.exists(new_name):
            return new_name
        counter += 1


def write_text_file(path: str, text: str, encoding: str = "utf-8") -> None:
    """
    Scrie text în fișier (creează directoarele la nevoie).
    """
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding=encoding, errors="ignore") as f:
        f.write(text)


def write_binary_file(path: str, data: bytes) -> None:
    """
    Scrie fișier binar (creează directoarele la nevoie).
    """
    ensure_dir(os.path.dirname(path))
    with open(path, "wb") as f:
        f.write(data)


# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------


def format_size(bytes_size: float) -> str:
    """
    1536000 -> 1.5 MB
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_time(seconds: float) -> str:
    """
    125 -> 2m 5s
    """
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s" if s else f"{h}h {m}m"


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------


def is_valid_url(url: str) -> bool:
    """
    True dacă URL‑ul are schemă și netloc.
    """
    try:
        p = urlparse(url)
        return bool(p.scheme) and bool(p.netloc)
    except Exception:
        return False


def get_domain_from_url(url: str) -> str | None:
    """www.example.com -> example.com (fără www)."""
    try:
        domain = urlparse(url).netloc
        return domain[4:] if domain.startswith("www.") else domain
    except Exception as e:
        logger.error("Eroare extragere domeniu din %s: %s", url, e)
        return None


def domain_to_folder(domain: str) -> str:
    """
    Transpune domeniul într‑un nume de folder sigur (A‑Z, a‑z, 0‑9, _ . -).
    """
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", domain.strip())
    return safe or "site"


def guess_output_dir(base_output: str | None, start_url: str) -> str:
    """
    Dacă userul a furnizat --output îl folosim; altfel capturăm în captures_<domeniu>.
    """
    if base_output:
        return ensure_dir(base_output)
    domain = urlparse(start_url).netloc or start_url
    return ensure_dir(f"captures_{domain_to_folder(domain)}")


def clean_url_params(url: str) -> str:
    """
    Elimină parametrii de tracking (utm_*, fbclid, gclid etc.).
    """
    tracking = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "fbclid",
        "gclid",
        "msclkid",
        "ref",
        "source",
    }
    p = urlparse(url)
    if not p.query:
        return url
    kept = []
    for param in p.query.split("&"):
        if "=" in param:
            key, _ = param.split("=", 1)
            if key.lower() not in tracking:
                kept.append(param)
        else:
            kept.append(param)
    new_q = "&".join(kept)
    return p._replace(query=new_q).geturl()


def merge_urls(base_url: str, relative_url: str) -> str:
    """
    Combina URL de bază cu unul relativ; tratează // protocol‑relative și schemă specială.
    """
    if not relative_url:
        return base_url
    if relative_url.startswith(("http://", "https://")):
        return relative_url
    if relative_url.startswith("//"):
        return f"{urlparse(base_url).scheme}:{relative_url}"
    if relative_url.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
        return relative_url
    return urljoin(base_url, relative_url)


def ext_from_url(url: str) -> str:
    """
    Returnează extensia în litere mici (cu punct) sau string gol.
    """
    return os.path.splitext(urlparse(url).path)[1].lower()


# ---------------------------------------------------------------------------
# Hash / fișier
# ---------------------------------------------------------------------------


def get_file_hash(filepath: str, algorithm: str = "md5") -> str | None:
    """
    Calculează hash hex pentru un fișier (md5/sha1/sha256).
    """
    try:
        hash_func = getattr(hashlib, algorithm)()
    except AttributeError:
        logger.error("Algoritm hash necunoscut %s", algorithm)
        return None

    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        logger.error("Eroare hash %s: %s", filepath, e)
        return None


# ---------------------------------------------------------------------------
# Diverse
# ---------------------------------------------------------------------------


def estimate_download_time(size_bytes: float, speed_bps: float) -> str:
    """
    size_bytes: dimensiunea fișierului
    speed_bps: viteză (bytes/sec)
    """
    if speed_bps <= 0:
        return "Necunoscut"
    return format_time(size_bytes / speed_bps)


def is_binary_content(content_type: str | None) -> bool:
    """
    Detectează dacă un Content‑Type este binar (pentru filtrare rapidă).
    """
    if not content_type:
        return False
    content_type = content_type.lower()
    texty = (
        "text/",
        "application/json",
        "application/javascript",
        "application/xml",
        "application/xhtml+xml",
        "application/x-javascript",
    )
    return not any(t in content_type for t in texty)


def sanitize_filename(filename: str) -> str:
    """
    Curăță numele fișierului de caractere invalide și spații multiple.
    """
    invalid = '<>:"|?*'
    for ch in invalid:
        filename = filename.replace(ch, "_")
    filename = re.sub(r"\s+", " ", filename).strip()
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[: 255 - len(ext)] + ext
    return filename


def normalize_path(path: str) -> str:
    """
    Normalizează cale (schimbă backslash cu slash, elimină ../ ./ etc.).
    """
    path = path.replace("\\", "/")
    path = re.sub(r"/+", "/", path)
    parts = []
    for part in path.split("/"):
        if part == ".":
            continue
        if part == ".." and parts:
            parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)
