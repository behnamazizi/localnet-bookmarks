# localnet-bookmarks

A curated directory of locally accessible websites during internet restrictions.

## What is this?

This repository maintains a JSON list of Iranian websites and online services intended to remain accessible when global internet access is limited.  
Each build generates a single, offline-ready HTML file (self-contained) and publishes it as a Release asset.

## Data format

Source file: `src/list.json`

Each item:

-   `name`
-   `url`
-   `category`
-   `tags` (up to 5)

## Icons (optional)

Place optional PNG icons in `src/icons/` using the hostname as filename:

-   `my.tax.gov.ir.png`
-   `divar.ir.png`

Icons are packed into a single embedded sprite during build.  
If an icon is missing, the UI shows the first letter of the site name.

## Build locally

```bash
python -m pip install Pillow
python scripts/build.py
```

## Directory (auto-generated)

<!-- AUTOGEN:LIST:START -->
<!-- AUTOGEN:LIST:END -->
