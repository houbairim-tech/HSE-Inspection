# HSE107E Cloud-connected builds

The Android and Windows builds use the same Cloudflare Worker/D1 backend:
https://hse107e-api.hse107e-cloud-api.workers.dev

## Build outputs
- Android: APK
- Windows: NSIS installer EXE + portable EXE

The Cloud button is injected into both builds. It supports login, first-admin bootstrap, upload of local application data, and download of Cloud data.

Cloudflare database: hse107e-cloud
Worker: hse107e-api
