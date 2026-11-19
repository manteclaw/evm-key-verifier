#!/usr/bin/env python3
"""
Wallet Key Verifier — pre-flight safety check before funding any wallet.

Verifies that a private key you hold derives to the expected address
*before* any funds are sent to that address. If the key does not match,
funding that address would burn the funds — the check refuses (exit 1)
instead of letting you proceed.

The key is read from the EVM_PRIVATE_KEY environment variable or from a
key file passed with --key-file. It is never written to disk by this
script, never transmitted anywhere, and only used locally to derive the
address. No filesystem scanning: this tool checks exactly the key you
hand it, nothing else.

Usage:
    EVM_PRIVATE_KEY=0x... python3 verify-wallet-key.py 0xYourAddress
    python3 verify-wallet-key.py 0xYourAddress --key-file ~/.config/mywallet.key
    python3 verify-wallet-key.py --generate   # print a fresh keypair (do not share the key)

Exit: 0 if the key derives to the address, 1 otherwise.
"""

import argparse
import os
import sys

from eth_account import Account


def load_key(args) -> str:
    """Return the private key from --key-file or EVM_PRIVATE_KEY."""
    if args.key_file:
        try:
            with open(args.key_file) as f:
                key = f.read().strip()
        except OSError as e:
            print(f"Could not read key file: {e}")
            sys.exit(1)
    else:
        key = os.getenv("EVM_PRIVATE_KEY", "").strip()
        if not key:
            print("No key supplied. Set EVM_PRIVATE_KEY or pass --key-file <path>.")
            print("Never paste a private key into a command line that gets logged;")
            print("prefer the environment variable or a 0600 key file.")
            sys.exit(1)
    if not key.startswith("0x"):
        key = "0x" + key
    if len(key) != 66:
        print("Key does not look like a 32-byte hex private key (expected 0x + 64 hex chars).")
        sys.exit(1)
    return key


def verify(address: str, key: str) -> int:
    try:
        derived = Account.from_key(key).address
    except Exception as e:  # noqa: BLE001 - bad key input is a user error
        print(f"Could not derive an address from the supplied key: {e}")
        return 1
    if derived.lower() == address.lower():
        print(f"KEY VERIFIED: the key derives to {derived}")
        return 0
    print("KEY MISMATCH — do not fund this address.")
    print(f"  Expected: {address}")
    print(f"  Key derives to: {derived}")
    return 1


def generate() -> int:
    """Print a fresh keypair. The key is shown once — store it safely and never share it."""
    acct = Account.create()
    print("Fresh keypair generated locally. Store the private key in your")
    print("password manager / hardware wallet and never share it with anyone.")
    print(f"  Address:     {acct.address}")
    print(f"  Private key: {acct.key.hex()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a private key derives to an expected address before funding it."
    )
    parser.add_argument("address", nargs="?", help="expected address (0x...)")
    parser.add_argument("--key-file", help="path to a file containing the private key")
    parser.add_argument("--generate", action="store_true", help="print a fresh keypair and exit")
    args = parser.parse_args()

    if args.generate:
        return generate()
    if not args.address:
        parser.print_usage()
        print("verify-wallet-key.py: error: an address is required (or use --generate)")
        return 1
    return verify(args.address, load_key(args))


if __name__ == "__main__":
    sys.exit(main())
