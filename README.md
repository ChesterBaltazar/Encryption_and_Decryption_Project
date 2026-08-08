# Vault — Personal Encrypt/Decrypt Tool

A pure Python 3 command-line tool for encrypting and decrypting **text** and **files** using a password. Built with the `cryptography` library for strong, industry-standard encryption — no accounts, no cloud, everything stays local.

---

## Overview

Vault lets you lock down sensitive text or files behind a password. It uses **PBKDF2-HMAC-SHA256** to turn your password into a secure encryption key, and **Fernet** (AES-based symmetric encryption) to actually encrypt/decrypt the data. There's no separate key file to lose — your password *is* the key, and a random salt is stored alongside your encrypted data so the key can be re-derived correctly at decryption time.

---

## How It Works

1. **You provide a password.** Vault never stores it — it's only used in memory for the current operation.
2. **A random salt is generated** (16 bytes) for that specific encryption. The salt ensures that even if you encrypt the same text twice with the same password, the output is different each time.
3. **PBKDF2-HMAC-SHA256** derives a 32-byte encryption key from your password + salt, using **390,000 iterations** — this makes brute-force password guessing much slower for an attacker.
4. **Fernet encryption** uses that derived key to encrypt your text or file bytes into ciphertext (which also includes built-in integrity/authenticity checks).
5. **Salt + ciphertext are bundled together** (`salt.token`) and saved — so decryption only ever needs the password, since the salt travels with the data.
6. **To decrypt**, Vault splits the salt back out, re-derives the exact same key from your password, and reverses the Fernet encryption. If the password is wrong or the data is corrupted, decryption fails safely with an error instead of returning garbage.

### Program Flow

```
                        ┌───────────────────────┐
                        │      Run vault.py       │
                        └───────────┬─────────────┘
                                    │
                        ┌───────────▼─────────────┐
                        │        Main Menu          │
                        │  1) Encrypt text           │
                        │  2) Decrypt text            │
                        │  3) Encrypt a file           │
                        │  4) Decrypt a file            │
                        │  5) Exit                       │
                        └───────────┬─────────────┘
                                    │
        ┌───────────────┬───────────────┬────────────────┐
        │               │               │                │
 ┌──────▼──────┐ ┌───────▼──────┐ ┌──────▼───────┐ ┌───────▼───────┐
 │ Encrypt Text │ │ Decrypt Text  │ │ Encrypt File  │ │ Decrypt File   │
 │              │ │               │ │               │ │                │
 │ Enter text   │ │ Paste/point   │ │ Point to file │ │ Point to        │
 │ Set password │ │ to payload    │ │ Set password  │ │ .vault file     │
 │ + confirm    │ │ Enter         │ │ + confirm     │ │ Enter password  │
 │              │ │ password      │ │               │ │                │
 │ Generate     │ │               │ │ Generate      │ │ Re-derive key   │
 │ salt + key   │ │ Re-derive     │ │ salt + key    │ │ from salt in    │
 │              │ │ key from      │ │               │ │ file             │
 │ Encrypt with │ │ stored salt   │ │ Encrypt file  │ │                  │
 │ Fernet       │ │               │ │ bytes with    │ │ Decrypt with     │
 │              │ │ Decrypt with  │ │ Fernet        │ │ Fernet           │
 │ Show result, │ │ Fernet        │ │               │ │                  │
 │ optionally   │ │               │ │ Save as       │ │ Save as          │
 │ save to file │ │ Show result   │ │ file.vault    │ │ file.decrypted   │
 └──────────────┘ └───────────────┘ └───────────────┘ └────────────────┘
```

---

## Key Concepts

| Concept | Description |
|---|---|
| **Password** | The secret you choose. Used to derive the encryption key — nothing is stored except what you encrypt. |
| **Salt** | 16 random bytes generated per encryption, stored alongside the ciphertext. Prevents identical inputs from producing identical outputs. |
| **PBKDF2-HMAC-SHA256** | The key derivation function that turns your password + salt into a strong 32-byte key, run through 390,000 iterations to resist brute-forcing. |
| **Fernet** | The symmetric encryption scheme (built on AES) that actually encrypts/decrypts your data and verifies it hasn't been tampered with. |
| **`.vault` file** | The output of file encryption — contains the salt + encrypted bytes. |
| **`.decrypted` file** | The output of file decryption — your original file, restored. |

> **There is no password recovery.** If you forget your password, your encrypted text/files cannot be recovered by anyone — that's the point of strong encryption.

---

## Tech Stack

- **Language:** Python 3
- **Library:** [`cryptography`](https://pypi.org/project/cryptography/) — `Fernet`, `PBKDF2HMAC`, `hashes`
- **Standard library only otherwise:** `os`, `sys`, `base64`, `getpass`, `datetime`

---

## How to Download / Install

### Option 1: Clone with Git
```bash
git clone https://github.com/yourusername/vault.git
cd vault
```

### Option 2: Download as ZIP
1. Go to the GitHub repository page.
2. Click the green **Code** button.
3. Select **Download ZIP**.
4. Extract the ZIP file on your computer.
5. Open a terminal inside the extracted folder.

### Install the dependency
Vault has one external dependency:
```bash
pip install cryptography
```

### Requirements
- Python 3.7 or newer

Check your version with:
```bash
python3 --version
```

---

## Usage

Run the tool:
```bash
python3 vault.py
```

You'll see the Vault logo and a menu with 5 options:

```
Choose an option:
  1) Encrypt text
  2) Decrypt text
  3) Encrypt a file
  4) Decrypt a file
  5) Exit
```

## 1️⃣ Encrypt a file
- Provide the path to any file.
- Set and confirm a password.
- A new file is created alongside it: `yourfile.ext.vault`

### 2️⃣ Decrypt a file
- Provide the path to a `.vault` file.
- Enter the password used to encrypt it.
- The original file is restored as `yourfile.ext.decrypted`

### 3️⃣ Exit
Closes the program.

---

## Project Structure

```
vault/
│
├── vault.py               # Main script — all encryption/decryption logic + menu
└── encrypted_texts/         # Auto-created folder for saved encrypted text outputs
```

---

## Purpose

This project was built to:
1. Provide a simple, password-based way to encrypt sensitive text and files.
2. Demonstrate secure password-to-key derivation (PBKDF2) paired with authenticated encryption (Fernet).
3. Serve as a learning reference for real-world, correctly-implemented symmetric encryption in Python — no shortcuts like storing raw passwords or skipping salts.

---

## Disclaimer

This tool is intended for **educational purposes and personal file protection**. While it uses proper cryptographic practices (salted PBKDF2 + Fernet/AES), it has not been independently security-audited. Always keep backups of anything important, and **never forget your password** — there is no way to recover encrypted data without it.

---

## 📄 License

MIT License — feel free to use, modify, and share.
