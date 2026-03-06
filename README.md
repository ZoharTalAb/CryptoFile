# CryptoFile Backend 🔐

FastAPI backend for a secure messaging system using:

- AES-GCM encryption
- KEK/DEK key hierarchy (password-derived KEK + per-message DEK)
- Steganography (audio / image / text)
- JWT authentication
- Clean Architecture

## Run with Docker (recommended)

1. Create `.env` from the example:

```bash
cp .env.example .env
```
