import datetime
import os
import subprocess
import base64
import json
import math
from dataclasses import dataclass, asdict
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

# Project paths
ROOT = Path(__file__).resolve().parents[1]
SRC_LIST = ROOT / "src" / "list.json"
ICONS_DIR = ROOT / "src" / "icons"

TEMPLATE = ROOT / "scripts" / "templates" / "index.template.html"
DIST_DIR = ROOT / "dist"
OUT_HTML = DIST_DIR / "index.html"

# Sprite config
ICON_SIZE = 24
SPRITE_COLS = 12  # change freely
SPRITE_WEBP_QUALITY = 85
SPRITE_JPG_QUALITY = 85


@dataclass(frozen=True)
class Site:
    name: str
    url: str
    category: str
    tags: list[str]
    icon_x: int | None = None
    icon_y: int | None = None


def _hostname(url: str) -> str:
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def _strip_www(host: str) -> str:
    if host.startswith("www."):
        return host[4:]
    return host


def load_sites() -> list[Site]:
    data = json.loads(SRC_LIST.read_text(encoding="utf-8"))
    raw = data.get("sites", [])

    sites: list[Site] = []
    for it in raw:
        name = (it.get("name") or "").strip()
        url = (it.get("url") or "").strip()
        category = (it.get("category") or "").strip()
        tags = [t.strip() for t in (it.get("tags") or []) if t and t.strip()]

        if not name or not url:
            continue

        sites.append(Site(name=name, url=url, category=category, tags=tags[:5]))

    sites.sort(key=lambda s: (s.category, s.name, s.url))
    return sites


def build_category_options(sites: list[Site]) -> str:
    cats = sorted({s.category for s in sites if s.category})
    return "\n      ".join(f'<option value="{escape(c)}">{escape(c)}</option>' for c in cats)


def normalize_icon_to_rgb_white_bg(img: Image.Image) -> Image.Image:
    """
    Returns a 24x24 RGB image (no alpha).
    If input has transparency, it is composited on white.
    """
    rgba = img.convert("RGBA")
    w, h = rgba.size
    if w <= 0 or h <= 0:
        return Image.new("RGB", (ICON_SIZE, ICON_SIZE), (255, 255, 255))

    scale = min(ICON_SIZE / w, ICON_SIZE / h)
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    rgba = rgba.resize((nw, nh), Image.LANCZOS)

    canvas_rgba = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (255, 255, 255, 255))
    x = (ICON_SIZE - nw) // 2
    y = (ICON_SIZE - nh) // 2
    canvas_rgba.alpha_composite(rgba, (x, y))

    return canvas_rgba.convert("RGB")


def load_icons_by_hostnames(hostnames: list[str]) -> dict[str, Image.Image]:
    """
    Icons are optional.
    File naming convention: <hostname>.png (exact hostname).
    Also supports 'www.' fallback: tries host, then host without 'www.'.
    """
    icons: dict[str, Image.Image] = {}

    for host in hostnames:
        if not host:
            continue

        candidates = [host]
        no_www = _strip_www(host)
        if no_www != host:
            candidates.append(no_www)

        icon_path = None
        for cand in candidates:
            fp = ICONS_DIR / f"{cand}.png"
            if fp.exists():
                icon_path = fp
                host = cand 
                break

        if icon_path is None:
            continue

        try:
            img = Image.open(icon_path)
            icons[host] = normalize_icon_to_rgb_white_bg(img)
        except Exception:
            continue

    return icons


def save_sprite_to_data_uri(sprite_rgb: Image.Image) -> tuple[str, str]:
    """
    Tries WebP first; if not supported by the Pillow build, falls back to JPEG.
    Returns (data_uri, mime).
    """
    buf = BytesIO()

    try:
        sprite_rgb.save(
            buf,
            format="WEBP",
            quality=SPRITE_WEBP_QUALITY,
            method=2, 
        )
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/webp;base64,{b64}", "image/webp"
    except Exception:
        buf = BytesIO()
        sprite_rgb.save(
            buf,
            format="JPEG",
            quality=SPRITE_JPG_QUALITY,
            optimize=True,
            progressive=True,
        )
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}", "image/jpeg"


def build_sprite_and_positions(icons: dict[str, Image.Image]) -> tuple[str, str, dict[str, tuple[int, int]]]:
    """
    Builds a single RGB sprite (no alpha) on white background.
    Returns:
      - sprite data URI
      - background-size css (e.g. "288px 120px")
      - positions dict: hostname -> (x, y) in pixels
    """
    if not icons:
        blank = Image.new("RGB", (1, 1), (255, 255, 255))
        data_uri, _mime = save_sprite_to_data_uri(blank)
        return data_uri, "1px 1px", {}

    hosts = sorted(icons.keys())
    n = len(hosts)
    cols = SPRITE_COLS
    rows = int(math.ceil(n / cols))

    sprite_w = cols * ICON_SIZE
    sprite_h = rows * ICON_SIZE
    sprite = Image.new("RGB", (sprite_w, sprite_h), (255, 255, 255))

    positions: dict[str, tuple[int, int]] = {}
    for idx, host in enumerate(hosts):
        x = (idx % cols) * ICON_SIZE
        y = (idx // cols) * ICON_SIZE
        sprite.paste(icons[host], (x, y))
        positions[host] = (x, y)

    data_uri, _mime = save_sprite_to_data_uri(sprite)
    bg_size = f"{sprite_w}px {sprite_h}px"
    return data_uri, bg_size, positions


def attach_icon_positions_to_sites(sites: list[Site], positions: dict[str, tuple[int, int]]) -> list[Site]:
    """
    Adds icon_x/icon_y to site objects if an icon exists.
    It tries hostname as-is and also without 'www.' for matching.
    """
    out: list[Site] = []
    for s in sites:
        host = _hostname(s.url)
        host2 = _strip_www(host)

        pos = None
        if host in positions:
            pos = positions[host]
        elif host2 in positions:
            pos = positions[host2]

        if pos is None:
            out.append(s)
        else:
            out.append(
                Site(
                    name=s.name,
                    url=s.url,
                    category=s.category,
                    tags=s.tags,
                    icon_x=pos[0],
                    icon_y=pos[1],
                )
            )
    return out


def main() -> None:
    sites = load_sites()

    hostnames = sorted({h for h in (_hostname(s.url) for s in sites) if h})

    icons = load_icons_by_hostnames(hostnames)
    sprite_data_uri, bg_size_css, positions = build_sprite_and_positions(icons)

    sites_with_icons = attach_icon_positions_to_sites(sites, positions)

    template = TEMPLATE.read_text(encoding="utf-8")

    sites_payload = [asdict(s) for s in sites_with_icons]

    html = template
    html = html.replace("__DATA__", json.dumps(sites_payload, ensure_ascii=False))
    html = html.replace("__CATEGORIES__", build_category_options(sites_with_icons))
    html = html.replace("__SPRITE_DATA_URI__", sprite_data_uri)
    html = html.replace("__SPRITE_BG_SIZE__", bg_size_css)

    html = html.replace("__ICON_CSS_RULES__", "")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")

    print(f"Built: {OUT_HTML}")
    print(f"Icons packed: {len(positions)}")


if __name__ == "__main__":
    main()
