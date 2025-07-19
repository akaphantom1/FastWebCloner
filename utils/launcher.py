
"""
Construieste un index.html de lansare in radacina snapshot-ului.
Daca gaseste <domeniu>/index.html il foloseste; altfel cauta cea mai mare
sau cea mai 'potrivita' pagina HTML in tot snapshot-ul.
"""

import os
from urllib.parse import urlparse


def _collect_html_files(root_folder: str):
    html_files = []
    for dirpath, _dirnames, filenames in os.walk(root_folder):
        for fn in filenames:
            if fn.lower().endswith((".html", ".htm")):
                full = os.path.join(dirpath, fn)
                try:
                    size = os.path.getsize(full)
                except OSError:
                    size = 0
                rel = os.path.relpath(full, start=root_folder).replace(os.sep, "/")
                html_files.append((full, rel, size))
    return html_files


def write_root_index_auto(output_folder: str, base_url: str = None):
    """
    Creeaza <output_folder>/index.html care redirectioneaza catre pagina „cea mai buna”:
      1. <netloc>/index.html daca exista.
      2. alt fisier index.html (oricare subfolder) daca exista.
      3. cel mai mare fisier .html/.htm din snapshot (probabil pagina principala).
    """
    target_rel = None

    # 1. incearca domeniul din base_url
    if base_url:
        netloc = urlparse(base_url).netloc
        if netloc:
            candidate = os.path.join(output_folder, netloc, "index.html")
            if os.path.exists(candidate):
                target_rel = os.path.relpath(candidate, start=output_folder).replace(os.sep, "/")

    # 2. cauta orice index.html in snapshot
    if target_rel is None:
        for dirpath, _dirnames, filenames in os.walk(output_folder):
            if "index.html" in filenames:
                candidate = os.path.join(dirpath, "index.html")
                target_rel = os.path.relpath(candidate, start=output_folder).replace(os.sep, "/")
                break

    # 3. alege cel mai mare fisier .html / .htm
    if target_rel is None:
        html_files = _collect_html_files(output_folder)
        if html_files:
            # sorteaza dupa marime descrescator
            html_files.sort(key=lambda t: t[2], reverse=True)
            _full, rel, _size = html_files[0]
            target_rel = rel

    # Daca tot nu avem nimic, nu scriem launcher
    if target_rel is None:
        return

    launcher_path = os.path.join(output_folder, "index.html")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Snapshot launcher</title>
<meta http-equiv="refresh" content="0; url={target_rel}">
</head>
<body>
<p>Deschid <a href="{target_rel}">{target_rel}</a>… Daca nu esti redirectionat automat, apasa linkul.</p>
</body>
</html>"""
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(html)
