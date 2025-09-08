# IPSW Toolkit
**IPSW Toolkit** is a Python extension layer for working with Apple IPSW (iOS/macOS firmware) files.  
It is **not a copy of the original `ipsw-parser` project** – instead, it is **inspired by the origanl work **.  
The toolkit provides safe, legal, and sandboxed enhancements that let developers and researchers work with IPSW archives more effectively,
without altering the original parser.  
---
## ✨ What It Does
- ✅ **Integrity Verification** — Check IPSW firmware archives with SHA-256 to ensure they are unmodified.  
- ✅ **Sandbox Extraction** — Export sensitive files (like `BuildManifest.plist`) into a safe temporary directory.  
- ✅ **Reports** — Generate quick JSON reports with restore/system version info and file counts.  
- ✅ **Extension Layer** — Works *with* the original `ipsw-parser`, but never changes or overwrites it.  
---
## 💡 Why It’s Useful
Apple IPSW firmware files are large, complex archives that contain manifests, trustcaches, and device support bundles.  
The original [`ipsw-parser`](https://github.com/blacktop/ipsw) gives you low-level access, but developers often need:  
- Security checks (integrity before analysis).
- Safe ways to extract only what’s needed.
- Clean reports for automation pipelines.
- A sandbox so the original IPSW is never touched.
That’s exactly what **IPSW Toolkit** provides.
---
## 🔗 Relationship to `ipsw-parser`
- `ipsw-parser` = the foundation (raw parsing).
- `ipsw-toolkit` = an **add-on extension** layer.
- We do **not** modify or duplicate the original project.
- Instead, we **import it** and safely extend functionality.
This design means:
- Your existing workflows with `ipsw-parser` keep working.
- You gain new features without risk.
- The project remains legal, modular, and future-proof.
---
## 🚀 Installation & Setup
### 1. Clone the Repository
```bash
git clone https://github.com/Garrisonronnie/python-Helper-library.git
cd ipsw-toolkit
 Requirements for this is 
 pip install -r requirements.txt
 pip install -e .
 ## usage  examples 
 from pathlib import Path
from ipsw_toolkit import IPSWToolkit

# Path to an IPSW file
ipsw_path = Path("iPhone16,1_18.3_22D5034e_Restore.ipsw")

# Create toolkit instance
toolkit = IPSWToolkit(ipsw_path)

# (Optional) Verify integrity with expected SHA-256 hash
toolkit.verify_integrity("expected_sha256_here")

# Export BuildManifest safely to sandbox
manifest = toolkit.export_manifest(Path("BuildManifest.plist"))
print("BuildManifest extracted to:", manifest)

# Generate quick info report
report = toolkit.report_info()
print(report)

# Cleanup sandbox when done
toolkit.cleanup()