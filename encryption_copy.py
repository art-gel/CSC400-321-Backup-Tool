

import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

salt = 16    # random bytes mixed into the key so the same passphrase gives a different key each time
nonce = 12   # random bytes AES-GCM needs; must never repeat for the same key


def make_key(passphrase, salt):
    # turn a human passphrase into a proper 32-byte AES key.
    # scrypt is DELIBERATELY slow, so guessing passphrases is expensive.
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return kdf.derive(passphrase.encode("utf-8"))


def encrypt_file(image_path, passphrase):
    # locks the file. returns the path of the new locked ".enc" file.
    image_path = Path(image_path)

    data = image_path.read_bytes()          # read the whole image file
    salt = os.urandom(salt)            # fresh random salt
    nonce = os.urandom(nonce)          # fresh random nonce
    key = make_key(passphrase, salt)        # passphrase -> key (key only exists right here)

    ciphertext = AESGCM(key).encrypt(nonce, data, None)   # the actual locking

    enc_path = Path(str(image_path) + ".enc")
    # save: salt + nonce + ciphertext. salt and nonce are NOT secret --
    # they are needed later to rebuild the same key and unlock the file.
    enc_path.write_bytes(salt + nonce + ciphertext)
    return enc_path


def decrypt_file(enc_path, passphrase):
    # unlocks the file. returns the path of the recovered image.
    # if the passphrase is wrong, AESGCM raises an error instead of giving garbage.
    enc_path = Path(enc_path)

    blob = enc_path.read_bytes()
    salt = blob[:salt]                              # first 16 bytes
    nonce = blob[salt:salt + nonce]       # next 12 bytes
    ciphertext = blob[salt + nonce:]           # everything after that

    key = make_key(passphrase, salt)                     # same passphrase + same salt = same key
    data = AESGCM(key).decrypt(nonce, ciphertext, None)  # the actual unlocking

    out_path = Path(str(enc_path) + ".restored")
    out_path.write_bytes(data)
    return out_path

