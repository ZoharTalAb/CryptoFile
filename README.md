# CryptoFile# CryptoFile 🔐

Secure Multi-Layer Steganographic Messaging System  
Built with Clean Architecture, AES-GCM, and Key Hierarchy Design.

---

## 🏗 Architecture

The system follows **Clean Architecture** principles:

- **Domain** → Entities, Enums, Interfaces, Crypto logic
- **Application** → Use Cases (Business logic only)
- **Infrastructure** → Database, Stego engines, Repositories
- **Presentation** → FastAPI routes, JWT auth

Application layer depends only on Domain interfaces.  
Infrastructure implements those interfaces.

---

## 🔐 Cryptography Design

### AES-256-GCM

Why AES-GCM?

- Authenticated Encryption (confidentiality + integrity)
- Built-in authentication tag (prevents tampering)
- No padding oracle vulnerabilities
- 96-bit nonce (recommended for GCM)
- 256-bit symmetric key

---

## 🔑 Key Hierarchy (KEK / DEK Model)

### DEK (Data Encryption Key)

- Random 256-bit key generated per message
- Used to encrypt the actual payload
- Ensures forward secrecy between messages

### KEK (Key Encryption Key)

- Derived from user password via PBKDF2-HMAC-SHA256
- Used to wrap (encrypt) the DEK
- Never stored directly

### Flow:

1. User provides password
2. PBKDF2 derives KEK
3. Random DEK is generated
4. Payload encrypted with DEK
5. DEK wrapped with KEK
6. Wrapped DEK stored alongside message

This ensures:

- Password compromise does not expose plaintext directly
- Each message has independent encryption key

---

## 🕵️ Threat Model (Basic)

| Threat            | Mitigation                                                                       |
| ----------------- | -------------------------------------------------------------------------------- |
| Database breach   | Passwords hashed with bcrypt                                                     |
| Message tampering | AES-GCM authentication tag                                                       |
| Key reuse         | Random DEK per message                                                           |
| Replay attack     | JWT validation + expiration                                                      |
| Stego detection   | Not resistant to advanced steganalysis (future improvement: DCT-based embedding) |

---

## 🔐 Authentication

- JWT (HS256)
- Secret required via environment variable
- No default fallback
- Token expiration enforced

---

## 🗄 Database

- SQLAlchemy ORM
- Environment-based DATABASE_URL
- SQLite (dev)
- PostgreSQL-ready (production)

---

## 🧪 Testing

- 44 unit tests
- Crypto engines tested
- Key management tested
- Use cases tested in isolation
- Stego engines tested independently

---

## 🚀 Setup

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
pytest
```
