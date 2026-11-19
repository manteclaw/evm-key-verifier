# evm-key-verifier

A small CLI that verifies a private key derives to the expected address
**before** any funds are sent to that address — and refuses on mismatch.

## Who it's for

Developers and agents moving funds between wallets. The failure mode it
prevents is simple and expensive: funding an address whose private key
you don't actually control. Once funds land there, they are gone. This
check costs nothing and takes a second — run it before every first
funding of a new address.

## Install

```bash
git clone https://github.com/manteclaw/evm-key-verifier.git
cd evm-key-verifier
python3 -m pip install -r requirements.txt
```

Requires Python 3.10+. Only dependency is `eth-account`.

## Usage

```bash
EVM_PRIVATE_KEY=0x... python3 verify-wallet-key.py 0xExpectedAddress
```

Or read the key from a file (recommended — keeps it out of shell history):

```bash
python3 verify-wallet-key.py 0xExpectedAddress --key-file ~/.config/mywallet.key
```

Match:

```text
KEY VERIFIED: the key derives to 0xExpectedAddress
```

Mismatch:

```text
KEY MISMATCH — do not fund this address.
  Expected: 0xExpectedAddress
  Key derives to: 0xSomeOtherAddress
```

Exit code is `0` on match, `1` on mismatch or bad input.

Generate a fresh keypair (prints the key once — store it safely, never
share it):

```bash
python3 verify-wallet-key.py --generate
```

## Safety notes

- The key is used **only locally** to derive the address. It is never
  written to disk by this script and never transmitted anywhere.
- This tool checks exactly the key you hand it. It does **not** scan your
  filesystem, `.env` files, or credential stores for keys — a scanner
  that hunts for private keys is itself a liability, so this one
  deliberately doesn't do that.
- Prefer the key file over the environment variable, and keep the file at
  `0600` permissions. Never commit a key file, and never paste a private
  key into chat, logs, or a shared terminal.
- Deriving an address from a key does not prove the key is backed up.
  Verify your backup separately before funding anything important.

## License

MIT — see `LICENSE`.
