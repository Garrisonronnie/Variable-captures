# FlatBuffersWrapper

**FlatBuffersWrapper** is a production-ready Python wrapper for FlatBuffer data.  
It provides compression, optional AES encryption, safe memory access, and atomic file handling.  
Designed for use on macOS, iOS, Linux, and Windows, it allows safe serialization, storage, and transmission of binary data.

---

## Features

- **Compression & Decompression:** Reduce storage and network transfer size using zlib.  
- **Optional AES Encryption:** Encrypt data securely with PyCryptodome, or use a safe fallback.  
- **Safe Memory Access:** Read slices of binary data safely (`safe_read`).  
- **Atomic File Operations:** Save/load files safely with temporary files and atomic replacement.  
- **Cross-Platform & macOS/iOS-safe paths:** Stores files in safe directories, like `~/Documents` on macOS/iOS.  
- **Flexible Serialization:** Works with bytes, bytearrays, or FlatBuffers Builder objects if installed.

---

## Supported Devices & Environments

- **macOS:** 10.15+ (Catalina, Big Sur, Monterey, Ventura, etc.)  
- **iOS:** 14+ (via Python interpreters like Pyto, Pythonista, or custom iOS Python runtime)  
- **Linux:** Any modern distribution with Python 3.8+  
- **Windows:** 10+ with Python 3.8+  

> **Note:** On iOS/macOS, file paths are automatically redirected to safe user-accessible directories (`Documents` folder), so the wrapper works with sandboxed environments.

---

## Use Cases

- Storing and transmitting FlatBuffer or binary data securely.  
- Compressing large binary payloads for network transfer.  
- Safe atomic file saving for desktop or mobile apps.  
- Encrypting sensitive payloads with AES (e.g., credentials, configurations).  
- Building cross-platform apps that need safe serialization/deserialization of data.

---

## Installation

### From PyPI (when published)

```bash
pip install flatbuffers-wrapper