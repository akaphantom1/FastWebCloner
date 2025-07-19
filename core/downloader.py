# core/downloader.py
# -*- coding: utf-8 -*-
"""
Descarca resursele statice si le salveaza sub <OUT>/__res__/subfolder/...
"""

from __future__ import annotations

import logging
import mimetypes
import os
import shutil
import time
from typing import Callable, Dict, Iterable, Optional

import requests

import config
from utils.helpers import format_size
from utils.pathmap import PathMapper, _clean_segment

logger = logging.getLogger(__name__)

_DEFAULT_MIME_MAP = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
    ".ico": "image/x-icon", ".css": "text/css", ".js": "application/javascript",
    ".woff": "font/woff", ".woff2": "font/woff2", ".ttf": "font/ttf",
    ".otf": "font/otf", ".eot": "application/vnd.ms-fontobject",
    ".mp4": "video/mp4", ".webm": "video/webm",
}

RES_ROOT = "__res__"  # acelaşi cu processor

TEXTS_DL = {
    "downloading": "Downloading resource...",
    "done": "All resources downloaded.",
}


class ResourceDownloader:
    def __init__(
        self,
        base_dir: str,
        pathmap: PathMapper,
        resource_types: Dict[str, bool],
        base_url: Optional[str] = None,
        allow_external: bool = True,
        session: Optional[requests.Session] = None,
        timeout: int = 20,
    ):
        self.base_dir = base_dir
        self.pathmap = pathmap
        self.resource_types = resource_types
        self.base_url = base_url
        self.allow_external = allow_external
        self.session = session or requests.Session()
        self.timeout = timeout

        self.downloaded_count = 0
        self.failed_count = 0

    # ------------------------------------------------------------------ #
    def download_all(
        self,
        resources: Iterable[str],
        res_sources: Dict[str, str],
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ):
        res_list = list(resources)
        total = len(res_list)
        if total == 0:
            if progress_callback:
                progress_callback(100, "No resources.")
            return

        for idx, url in enumerate(res_list, 1):
            if config.CANCELLED:
                break

            ok = self._download_one(url, res_sources.get(url))
            self.downloaded_count += ok
            self.failed_count += (not ok)

            if progress_callback:
                pct = int((idx / total) * 100)
                progress_callback(pct, f"{TEXTS_DL['downloading']} {idx}/{total}")

            while config.PAUSED and not config.CANCELLED:
                time.sleep(0.2)

        if progress_callback:
            progress_callback(100, TEXTS_DL["done"])

    # ------------------------------------------------------------------ #
    def _download_one(self, url: str, src_page: Optional[str]) -> bool:
        if not self._should_dl(url):
            return True

        try:
            r = self.session.get(url, timeout=self.timeout, stream=True)
            r.raise_for_status()
        except Exception as e:
            logger.warning("Network error %s: %s", url, e)
            return False

        content = r.content
        mime = r.headers.get("Content-Type") or _guess_mime(url)

        local_path = self.pathmap.path_for_resource(
            url,
            mime_type=mime,
            source_page_url=src_page
        )
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(content)
            logger.debug("Saved %s -> %s (%s)", url, local_path, format_size(len(content)))
            return True
        except OSError as e:
            logger.error("Write error %s: %s", local_path, e)
            try:
                safe = _clean_segment(os.path.basename(local_path))
                fb = os.path.join(os.path.dirname(local_path), safe)
                with open(fb, "wb") as f:
                    f.write(content)
                return True
            except Exception as e2:
                logger.error("Fallback write failed %s: %s", url, e2)
                return False

    # ------------------------------------------------------------------ #
    def _should_dl(self, url: str) -> bool:
        from urllib.parse import urlparse

        if not self.allow_external and self.base_url:
            if urlparse(url).netloc.lower().lstrip("www.") != urlparse(
                self.base_url
            ).netloc.lower().lstrip("www."):
                return False

        ext = os.path.splitext(url.split("?", 1)[0])[1].lower()
        t = self.resource_types
        if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"):
            return t.get("images", True)
        if ext == ".css":
            return t.get("css", True)
        if ext == ".js":
            return t.get("js", True)
        if ext in (".woff", ".woff2", ".ttf", ".otf", ".eot"):
            return t.get("fonts", True)
        if ext in (".mp4", ".webm", ".mov", ".avi", ".mkv"):
            return t.get("videos", False)
        return True


def _guess_mime(url: str) -> Optional[str]:
    ext = os.path.splitext(url.split("?", 1)[0])[1].lower()
    if ext in _DEFAULT_MIME_MAP:
        return _DEFAULT_MIME_MAP[ext]
    guess, _ = mimetypes.guess_type(url)
    return guess
