"""Step 2 of the pipeline: zero-knowledge encryption.

REAL IMPLEMENTATION (your job): stream the image through AES (e.g. via the
`cryptography` library), encrypting in chunks so you never load the whole image
into memory. The key is derived from a user passphrase and NEVER leaves the
machine — that's what makes it "zero-knowledge."
"""

import time
from pathlib import Path


def encrypt_file(image_path: Path, on_progress=None) -> Path:
    """Encrypt `image_path` in place/alongside. Returns the encrypted file path."""
    # TODO(team): real chunked AES-GCM encryption; key derived from user passphrase.
    for pct in (0.5, 1.0):
        time.sleep(0.05)
        if on_progress:
            on_progress(pct)
    return image_path.with_suffix(image_path.suffix + ".enc")
