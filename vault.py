#!/usr/bin/env python3
"""
Vault - Personal Encrypt/Decrypt Tool
Pure Python 3 only (uses the 'cryptography' package for strong encryption).

Install dependency (one-time):
    pip install cryptography

Run:
    python3 vault.py
"""

import os
import sys
import base64
import getpass
from datetime import datetime

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ----------------------------------------------------------------------
# COLORS (ANSI escape codes)
# ----------------------------------------------------------------------
YELLOW = "\033[93m"
RESET = "\033[0m"

# ----------------------------------------------------------------------
# LOGO
# ----------------------------------------------------------------------
# Replace this ASCII art with your own logo/text any time.
LOGO = r"""
_________   _____  .___________________      _____      _____   
 /   _____/  /  _  \ |   \__    ___/  _  \    /     \    /  _  \  
 \_____  \  /  /_\  \|   | |    | /  /_\  \  /  \ /  \  /  /_\  \ 
 /        \/    |    \   | |    |/    |    \/    Y    \/    |    \
/_______  /\____|__  /___| |____|\____|__  /\____|__  /\____|__  /
        \/         \/                    \/         \/         \/ 

        S E C U R E   V A U L T
"""


def show_logo():
    print(YELLOW + LOGO + RESET)
    print(YELLOW + "=" * 42 + RESET)
    print(YELLOW + "  Python-only Encrypt / Decrypt Tool" + RESET)
    print(YELLOW + "=" * 42 + RESET)
    print()


# ----------------------------------------------------------------------
# OUTPUT FOLDER FOR SAVED ENCRYPTED TEXT
# ----------------------------------------------------------------------
ENCRYPTED_TEXT_DIR = "encrypted_texts"


# ----------------------------------------------------------------------
# CRYPTO HELPERS
# ----------------------------------------------------------------------
SALT_SIZE = 16
KDF_ITERATIONS = 390_000  # OWASP-recommended-ish minimum for PBKDF2-HMAC-SHA256


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password + salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


def encrypt_text(plaintext: str, password: str) -> str:
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    token = Fernet(key).encrypt(plaintext.encode("utf-8"))
    # Store salt + token together, base64-encoded, so decrypt only needs one string
    payload = base64.urlsafe_b64encode(salt) + b"." + token
    return payload.decode("utf-8")


def decrypt_text(payload: str, password: str) -> str:
    salt_b64, token = payload.split(".", 1)
    salt = base64.urlsafe_b64decode(salt_b64.encode("utf-8"))
    key = derive_key(password, salt)
    plaintext = Fernet(key).decrypt(token.encode("utf-8"))
    return plaintext.decode("utf-8")


def encrypt_file(path: str, password: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    token = Fernet(key).encrypt(data)
    out_path = path + ".vault"
    with open(out_path, "wb") as f:
        f.write(base64.urlsafe_b64encode(salt) + b"." + token)
    return out_path


def decrypt_file(path: str, password: str) -> str:
    with open(path, "rb") as f:
        content = f.read()
    salt_b64, token = content.split(b".", 1)
    salt = base64.urlsafe_b64decode(salt_b64)
    key = derive_key(password, salt)
    data = Fernet(key).decrypt(token)
    if path.endswith(".vault"):
        out_path = path[: -len(".vault")] + ".decrypted"
    else:
        out_path = path + ".decrypted"
    with open(out_path, "wb") as f:
        f.write(data)
    return out_path


# ----------------------------------------------------------------------
# MENU
# ----------------------------------------------------------------------
def prompt_password(confirm: bool = False) -> str:
    while True:
        pw = getpass.getpass("Password: ")
        if not pw:
            print("Password cannot be empty.\n")
            continue
        if confirm:
            pw2 = getpass.getpass("Confirm password: ")
            if pw != pw2:
                print("Passwords do not match. Try again.\n")
                continue
        return pw


def menu_encrypt_text():
    text = input("Enter text to encrypt: ")
    password = prompt_password(confirm=True)
    result = encrypt_text(text, password)

    print("\nEncrypted text (you'll need the same password to decrypt):\n")
    print(result)
    print()

    os.makedirs(ENCRYPTED_TEXT_DIR, exist_ok=True)
    default_name = f"encrypted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filename = input(
        f"Save to file [{default_name}] (press Enter to accept, or type a name, "
        f"or '-' to skip saving): "
    ).strip()

    if filename == "-":
        print("Not saved to a file.\n")
        return

    if not filename:
        filename = default_name

    out_path = os.path.join(ENCRYPTED_TEXT_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"\nSaved to: {os.path.abspath(out_path)}\n")


def menu_decrypt_text():
    source = input(
        "Enter path to encrypted .txt file, or press Enter to paste text directly: "
    ).strip()

    if source:
        if not os.path.isfile(source):
            print("File not found.\n")
            return
        with open(source, "r", encoding="utf-8") as f:
            payload = f.read().strip()
    else:
        payload = input("Paste encrypted text: ").strip()

    password = prompt_password(confirm=False)
    try:
        result = decrypt_text(payload, password)
        print("\nDecrypted text:\n")
        print(result)
        print()
    except (InvalidToken, ValueError):
        print("\nDecryption failed. Wrong password or corrupted/invalid data.\n")


def menu_encrypt_file():
    path = input("Path to file to encrypt: ").strip()
    if not os.path.isfile(path):
        print("File not found.\n")
        return
    password = prompt_password(confirm=True)
    out_path = encrypt_file(path, password)
    print(f"\nEncrypted file written to: {out_path}\n")


def menu_decrypt_file():
    path = input("Path to .vault file to decrypt: ").strip()
    if not os.path.isfile(path):
        print("File not found.\n")
        return
    password = prompt_password(confirm=False)
    try:
        out_path = decrypt_file(path, password)
        print(f"\nDecrypted file written to: {out_path}\n")
    except (InvalidToken, ValueError):
        print("\nDecryption failed. Wrong password or corrupted/invalid file.\n")


def main():
    show_logo()
    menu = """
Choose an option:
  1) Encrypt text
  2) Decrypt text
  3) Encrypt a file
  4) Decrypt a file
  5) Exit
"""
    while True:
        print(menu)
        choice = input("> ").strip()
        print()
        if choice == "1":
            menu_encrypt_text()
        elif choice == "2":
            menu_decrypt_text()
        elif choice == "3":
            menu_encrypt_file()
        elif choice == "4":
            menu_decrypt_file()
        elif choice == "5":
            print("Goodbye.")
            sys.exit(0)
        else:
            print("Invalid choice, try again.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye.")
        sys.exit(0)
