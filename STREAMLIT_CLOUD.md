# Streamlit Community Cloud deployment

1. Push project to GitHub; entrypoint `app.py`.
2. Use Python 3.12 in Community Cloud Advanced settings if compatible.
3. `requirements.txt` installs the Playwright Python package, NOT Chromium. This version detects missing Chromium when clicking **Ambil dan simpan kurs**, then runs `python -m playwright install chromium` in the separate worker. Browser files are kept in `.playwright-browsers/`.
4. Linux uses headless=True automatically, irrespective of `.env`.
5. First sync can take longer because it downloads Chromium. Subsequent syncs reuse it during the app instance's lifetime.
6. If you see `error while loading shared libraries` or missing Linux shared libraries, Community Cloud may not have the browser's OS dependencies. Try adding a `packages.txt` (see Playwright official list for your distro), or deploy on a Docker/VPS platform where `python -m playwright install --with-deps chromium` is supported.
7. SQLite in Streamlit Community Cloud is ephemeral. Database changes and imported Excel history may disappear on reboot/redeploy. Use a persistent database or external storage for production historical monitoring.

Reference: https://playwright.dev/python/docs/browsers
