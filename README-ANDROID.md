# HSE 107E — Android phone version

The Android build uses the native Android project already contained in `DOC-20261119-WA0121.zip`.

## Android build
The GitHub Actions workflow:
1. extracts the existing Android project;
2. keeps the verified local HTML/base-URL fix that prevents the blank-screen problem;
3. injects the responsive phone UI layer from `mobile/mobile.css`;
4. forces portrait orientation for normal phone use;
5. bundles SheetJS for Excel export;
6. builds a debug APK with Gradle;
7. publishes the APK as a GitHub Actions artifact.

The phone UI uses full-width layouts, touch-friendly controls, safe-area handling, bottom-sheet dialogs, and horizontal scrolling for wide HSE tables.

## Cloudflare
The connected source now includes a Cloudflare Workers + D1 backend:
- API: `https://hse107e-api.hse107e-cloud-api.workers.dev`
- Worker: `hse107e-api`
- D1 database: `hse107e-cloud`

Cloud synchronization is available from the **☁️ Cloud** panel in the connected Windows/Android source. Operational HSE records are synchronized; local account passwords are excluded.

The workflow is in `.github/workflows/build-android.yml`.
