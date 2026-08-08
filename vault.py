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
  1) Encrypt a file
  2) Decrypt a file
  3) Exit
"""
    while True:
        print(menu)
        choice = input("> ").strip()
        print()
        if choice == "1":
            menu_encrypt_file()
        elif choice == "2":
            menu_decrypt_file()
        elif choice == "3":
            sys.exit(0)
        else:
            print("Invalid choice, try again.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)