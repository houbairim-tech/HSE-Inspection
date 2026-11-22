# HSE107E Cloudflare backend

The HSE107E cloud backend is deployed on Cloudflare Workers + D1.

- Worker: `hse107e-api`
- API: `https://hse107e-api.hse107e-cloud-api.workers.dev`
- D1: `hse107e-cloud`
- Authentication: email/password sessions with PBKDF2-SHA256 password hashing.
- Data model: `plants`, `users`, `sessions`, `records`, `audit_events`.
- Sync endpoint: `/records`.
- Local HSE operational data can be synchronized without uploading local account passwords.
- First administrator creation is protected by the Worker `BOOTSTRAP_CODE` secret.

The connected source archive supplied in this conversation contains the complete client integration for Windows/Electron and Android/Capacitor.
