"""Dedicated Playwright worker. Run separately from the Streamlit event loop."""
import argparse
import json
import sys
import traceback
import os
import subprocess
from pathlib import Path

# Configure browser location BEFORE launching Playwright.
BASE_DIR = Path(__file__).resolve().parent
if sys.platform.startswith("linux"):
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(BASE_DIR / ".playwright-browsers"))

from scraper_playwright import scrape_kurs


def ensure_chromium_installed():
    """On cloud Linux, download matching browser once if it is missing."""
    if not sys.platform.startswith("linux"):
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        path = Path(p.chromium.executable_path)
    if path.is_file():
        return
    print("Chromium belum ditemukan; mengunduh browser Playwright...", file=sys.stderr)
    proc = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=True, text=True, timeout=300,
        env=os.environ.copy(), check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "Instalasi Chromium gagal. Periksa log deployment, dependency Linux, "
            "dan akses download.\n" + (proc.stderr or proc.stdout)[-3500:]
        )
    if not path.is_file():
        raise RuntimeError(f"Installer selesai tetapi executable Chromium tidak ditemukan: {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--headless", choices=["true", "false"], default="false")
    args = parser.parse_args()
    try:
        ensure_chromium_installed()
        tanggal, records = scrape_kurs(
            headless=True if sys.platform.startswith("linux") else (args.headless == "true")
        )
        if not records:
            raise ValueError("BI tidak mengembalikan baris kurs.")
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"tanggal": tanggal, "records": records}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        traceback.print_exc(file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
