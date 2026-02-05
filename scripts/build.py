import base64
import json
import math
import re
from dataclasses import dataclass
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

SRC_LIST = ROOT / "src" / "list.json"
ICONS_DIR = ROOT / "src" / "icons"

TEMPLATE = ROOT / "scripts" / "templates" / "index.template.html"
DIST_DIR = ROOT / "dist"
OUT_HTML = DIST_DIR / "index.html"

README = ROOT / "README.md"
README_START = "<!-- AUTOGEN:LIST:START -->"
README_END = "<!-- AUTOGEN:LIST:END -->"

ICON_SIZE = 24
SPRITE_COLS = 12  # adjust freely
SPRITE_FMT = "PNG"  # safest for broad compatibility


@dataclass(frozen=True)
class Site:
    name: str
    url: str
    category: str
    tags: list[str]


def _hostname(url: str) -> str:
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


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

    # Stable output order
    sites.sort(key=lambda s: (s.category, s.name, s.url))
    return sites


def build_category_options(sites: list[Site]) -> str:
    cats = sorted({s.category for s in sites if s.category})
    return "\n      ".join(f'<option value="{escape(c)}">{escape(c)}</option>' for c in cats)


def normalize_icon(img: Image.Image) -> Image.Image:
    # Convert to RGBA and fit inside ICON_SIZE x ICON_SIZE with transparency padding.
    img = img.convert("RGBA")
    w, h = img.size
    if w == 0 or h == 0:
        return Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))

    scale = min(ICON_SIZE / w, ICON_SIZE / h)
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    img = img.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    x = (ICON_SIZE - nw) // 2
    y = (ICON_SIZE - nh) // 2
    canvas.alpha_composite(img, (x, y))
    return canvas


def load_icons_by_hostnames(hostnames: list[str]) -> dict[str, Image.Image]:
    # Icons are optional. We only map hostnames that actually have a file in src/icons.
    icons: dict[str, Image.Image] = {}

    for host in hostnames:
        if not host:
            continue
        # File naming convention: <hostname>.png (you can extend to .webp/.jpg later)
        fp = ICONS_DIR / f"{host}.png"
        if fp.exists():
            try:
                img = Image.open(fp)
                icons[host] = normalize_icon(img)
            except Exception:
                # Ignore broken icon files; fallback will show a letter.
                pass

    return icons


def build_sprite(icons: dict[str, Image.Image]) -> tuple[str, str, str, dict[str, tuple[int, int]]]:
    """
    Returns:
      sprite_data_uri, bg_size_css, icon_css_rules, positions mapping
    """
    if not icons:
        # Minimal transparent 1x1 PNG as a placeholder; CSS/JS will still show letter fallback.
        blank = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        buf = BytesIO()
        blank.save(buf, format="PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        data_uri = f"data:image/png;base64,{b64}"
        bg_size = "1px 1px"
        return data_uri, bg_size, "", {}

    hosts = sorted(icons.keys())
    n = len(hosts)
    cols = SPRITE_COLS
    rows = int(math.ceil(n / cols))

    sprite_w = cols * ICON_SIZE
    sprite_h = rows * ICON_SIZE
    sprite = Image.new("RGBA", (sprite_w, sprite_h), (0, 0, 0, 0))

    positions: dict[str, tuple[int, int]] = {}
    for idx, host in enumerate(hosts):
        x = (idx % cols) * ICON_SIZE
        y = (idx // cols) * ICON_SIZE
        sprite.alpha_composite(icons[host], (x, y))
        positions[host] = (x, y)

    buf = BytesIO()
    # PNG optimize helps a lot on sprites of tiny icons.
    sprite.save(buf, format=SPRITE_FMT, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    data_uri = f"data:image/png;base64,{b64}"

    bg_size = f"{sprite_w}px {sprite_h}px"

    # Attribute selector rules. A hostname without an icon simply won't have a rule.
    rules = []
    for host, (x, y) in positions.items():
        rules.append(
            f'.favicon.has-ico[data-ico="{escape(host)}"]' +
            f'{{background-position:-{x}px -{y}px;}}'
        )

    icon_css_rules = "\n".join(rules)
    return data_uri, bg_size, icon_css_rules, positions


def build_readme_block(sites: list[Site]) -> str:
    # Group by category for readability
    by_cat: dict[str, list[Site]] = {}
    for s in sites:
        by_cat.setdefault(s.category or "سایر", []).append(s)

    lines: list[str] = []
    for cat in sorted(by_cat.keys()):
        items = sorted(by_cat[cat], key=lambda x: (x.name, x.url))

        lines.append(f"### {cat}")
        lines.append("")
        lines.append("| نام | آدرس | تگ‌ها |")
        lines.append("|---|---|---|")

        for it in items:
            name = it.name.replace("|", "\\|")
            url = it.url
            tags = "، ".join(it.tags).replace("|", "\\|")
            lines.append(f"| {name} | {url} | {tags} |")

        lines.append("")

    return "\n".join(lines).strip() + "\n"


def update_readme(block: str) -> None:
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(README_START) + r".*?" + re.escape(README_END), flags=re.DOTALL)

    if not pattern.search(text):
        raise RuntimeError("README markers not found. Add AUTOGEN markers first.")

    replacement = f"{README_START}\n\n{block}\n{README_END}"
    new_text = pattern.sub(replacement, text)
    README.write_text(new_text, encoding="utf-8")


def main() -> None:
    sites = load_sites()

    # Collect hostnames from the list (only for icon lookup and ICON_HOSTS set)
    hostnames = sorted({ _hostname(s.url) for s in sites if _hostname(s.url) })

    icons = load_icons_by_hostnames(hostnames)
    sprite_data_uri, bg_size_css, icon_css_rules, positions = build_sprite(icons)

    icon_hosts = sorted(list(positions.keys()))

    template = TEMPLATE.read_text(encoding="utf-8")

    html = template
    html = html.replace("__DATA__", json.dumps([s.__dict__ for s in sites], ensure_ascii=False))
    html = html.replace("__ICON_HOSTS__", json.dumps(icon_hosts, ensure_ascii=False))
    html = html.replace("__CATEGORIES__", build_category_options(sites))

    html = html.replace("__SPRITE_DATA_URI__", sprite_data_uri)
    html = html.replace("__SPRITE_BG_SIZE__", bg_size_css)
    html = html.replace("__ICON_CSS_RULES__", icon_css_rules)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")

    # Update README auto-generated section
    readme_block = build_readme_block(sites)
    update_readme(readme_block)

    print(f"Built: {OUT_HTML}")
    print(f"Updated: {README}")


if __name__ == "__main__":
    main()
