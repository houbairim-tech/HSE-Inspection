# HSE 107E — Android build

The Android version uses Capacitor 8 and keeps the existing HSE 107E HTML application as the web layer.

The GitHub Actions workflow:
1. downloads/unpacks the existing `DOC-20261119-WA0121.zip` source already stored in this repository;
2. applies the Android/mobile responsive UI layer;
3. bundles SheetJS for Excel export;
4. creates the native Android project with Capacitor;
5. builds debug and release APKs;
6. publishes both APKs as a GitHub Actions artifact.

The UI is optimized for phone width, touch targets, safe-area insets, bottom-sheet dialogs and horizontal scrolling for wide HSE tables.