#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 Ronnie Garrison
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

"""
FlatBuffersWrapper (production-ready)
- Compression and decompression
- Optional AES encryption (with insecure fallback if enabled)
- Safe memory access
- Atomic file save/load with macOS/iOS-safe paths
- Ready for integration into real-world apps and services

Author: Ronnie Garrison
License: MIT
"""

from __future__ import annotations
import sys, os, zlib, struct, logging
from typing import Optional
from pathlib import Path

try:
    import flatbuffers  # type: ignore
    FLATBUFFERS_AVAILABLE = True
except Exception:
    FLATBUFFERS_AVAILABLE = False

try:
    from Crypto.Cipher import AES  # type: ignore
    from Crypto.Random import get_random_bytes  # type: ignore
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("FlatBuffersWrapper")


class FlatBuffersWrapper:
    HEADER_FMT = ">BBI"
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    def __init__(self, encryption_key: Optional[bytes] = None, timeout: int = 10, use_crypto_fallback: bool = False):
        if encryption_key and len(encryption_key) not in (16, 24, 32):
            raise ValueError("Encryption key must be 16, 24, or 32 bytes long.")
        self.encryption_key = encryption_key
        self.timeout = timeout
        self.use_crypto_fallback = use_crypto_fallback and not CRYPTO_AVAILABLE
        if not CRYPTO_AVAILABLE and encryption_key and not use_crypto_fallback:
            logger.warning(
                "Crypto (PyCryptodome) not available. Encryption will be disabled unless use_crypto_fallback=True."
            )

    # --- Compression ---
    def compress(self, data: bytes, level: int = 6) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("compress expects bytes-like input")
        return zlib.compress(data, level)

    def decompress(self, data: bytes) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("decompress expects bytes-like input")
        return zlib.decompress(data)

    # --- Encryption ---
    def encrypt(self, data: bytes) -> bytes:
        if not self.encryption_key:
            raise ValueError("No encryption key provided.")
        if CRYPTO_AVAILABLE:
            cipher = AES.new(self.encryption_key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            return cipher.nonce + tag + ciphertext
        elif self.use_crypto_fallback:
            key = self.encryption_key
            return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        else:
            raise RuntimeError(
                "Encryption requested but PyCryptodome not available. "
                "Set use_crypto_fallback=True to use insecure fallback."
            )

    def decrypt(self, data: bytes) -> bytes:
        if not self.encryption_key:
            raise ValueError("No encryption key provided.")
        if CRYPTO_AVAILABLE:
            if len(data) < 32:
                raise ValueError("Encrypted payload too short.")
            nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
            cipher = AES.new(self.encryption_key, AES.MODE_EAX, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        elif self.use_crypto_fallback:
            key = self.encryption_key
            return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        else:
            raise RuntimeError(
                "Decryption requested but PyCryptodome not available. "
                "Set use_crypto_fallback=True to use insecure fallback."
            )

    # --- Serialization ---
    def serialize(self, builder: Optional[object], *, compress: bool = True, encrypt: bool = False) -> bytes:
        if isinstance(builder, (bytes, bytearray)):
            raw = bytes(builder)
        elif FLATBUFFERS_AVAILABLE and hasattr(builder, "Output"):
            raw = bytes(builder.Output())
        elif builder is None:
            raise ValueError("No builder/data provided to serialize.")
        else:
            maybe = getattr(builder, "to_bytes", None)
            if callable(maybe):
                raw = maybe()
            else:
                raise TypeError(
                    "Unsupported builder type for serialization. "
                    "Provide bytes or real flatbuffers.Builder."
                )
        if compress:
            raw = self.compress(raw)
        if encrypt:
            raw = self.encrypt(raw)
        return raw

    def deserialize(self, data: bytes, *, compressed: bool = True, encrypted: bool = False) -> bytes:
        if encrypted:
            data = self.decrypt(data)
        if compressed:
            data = self.decompress(data)
        return data

    # --- File Handling ---
    @staticmethod
    def get_safe_path(path: str) -> str:
        if sys.platform == "darwin":
            base = Path.home() / "Documents"
            base.mkdir(parents=True, exist_ok=True)
            return str((base / Path(path).name).resolve())
        return str(Path(path).resolve())

    def save_to_file(self, data: bytes, path: str) -> None:
        safe = self.get_safe_path(path)
        target = Path(safe)
        tmp = (
            target.with_suffix(target.suffix + ".tmp")
            if target.suffix
            else target.with_name(target.name + ".tmp")
        )
        tmp.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp), str(target))
        logger.info("Saved %d bytes to %s", len(data), safe)

    def load_from_file(self, path: str) -> bytes:
        safe = self.get_safe_path(path)
        with open(safe, "rb") as f:
            data = f.read()
        logger.info("Loaded %d bytes from %s", len(data), safe)
        return data

    # --- Safe Memory Access ---
    @staticmethod
    def safe_read(data: bytes, offset: int, length: int) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("safe_read expects bytes-like data")
        if offset < 0 or length < 0:
            raise ValueError("Offset and length must be non-negative")
        if offset + length > len(data):
            raise ValueError("Requested region extends beyond buffer length")
        return data[offset : offset + length]
