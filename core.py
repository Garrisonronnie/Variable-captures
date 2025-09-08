# ipsw_toolkit/core.py
from __future__ import annotations
import hashlib
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, BinaryIO, Iterator
# Note: the original ipsw parser module must be importable as `ipsw_parser`.
# The toolkit *uses* that module but never modifies it.
try:
    from ipsw_parser import IPSW  # type: ignore
except Exception as e:
    IPSW = None  # type: ignore
# Public exceptions
class IPSWToolkitError(Exception):
    """Base class for errors raised by the IPSW toolkit."""
class IntegrityError(IPSWToolkitError):
    """Raised when a file's integrity check fails."""
class MissingDependencyError(IPSWToolkitError):
    """Raised when the original IPSW parser module cannot be imported."""
@dataclass
class ToolkitConfig:
    """Configuration for IPSWToolkit behavior."""
    keep_sandbox: bool = False  # if True, the sandbox directory is not deleted on cleanup
    sandbox_prefix: str = "ipsw_toolkit_"
    max_read_chunk: int = 8192  # bytes per read when hashing
class IPSWToolkit:
    """
    Safe extension wrapper around an existing IPSW parser.
    Usage:
        tool = IPSWToolkit(Path("something.ipsw"))
        report = tool.report_info()
        manifest_path = tool.export_manifest(Path("BuildManifest.plist"))
        tool.cleanup()
    """
    def __init__(self, ipsw_path: Path, config: Optional[ToolkitConfig] = None):
        if config is None:
            config = ToolkitConfig()
        self.config = config
        ipsw_path = Path(ipsw_path)
        if not ipsw_path.exists() or not ipsw_path.is_file():
            raise FileNotFoundError(f"IPSW file not found: {ipsw_path}")
        self.ipsw_path = ipsw_path
        self._sandbox_dir = Path(tempfile.mkdtemp(prefix=self.config.sandbox_prefix))
        self._open_ipsw_instance = None
        if IPSW is None:
            # Provide a clear, actionable message if the original module isn't installed.
            raise MissingDependencyError(
                "The original `ipsw_parser` module cannot be imported. "
                "Install or ensure it is importable (it must expose an `IPSW` class)."
            )
    @property
    def sandbox(self) -> Path:
        """Return the sandbox path for safe extraction/work."""
        return self._sandbox_dir
    def cleanup(self) -> None:
        """Remove the sandbox directory unless keep_sandbox is set."""
        if self.config.keep_sandbox:
            return
        if self._sandbox_dir.exists():
            shutil.rmtree(self._sandbox_dir, ignore_errors=True)
    # -----------------------------
    # Low-level helpers
    # -----------------------------
    def _sha256sum(self, file_path: Path) -> str:
        """Compute SHA-256 of a file in chunks."""
        h = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(self.config.max_read_chunk), b""):
                h.update(chunk)
        return h.hexdigest()
    @contextmanager
    def open_ipsw(self):
        """
        Context manager that opens the IPSW archive via the original parser and yields
        the IPSW object. The IPSW instance is created each time to avoid stateful changes.
        """
        import zipfile
        archive = zipfile.ZipFile(self.ipsw_path)
        try:
            ipsw = IPSW(archive)  # type: ignore
            yield ipsw
        finally:
            try:
                archive.close()
            except Exception:
                pass
    # -----------------------------
    # High-level features (safe)
    # -----------------------------
    def verify_integrity(self, expected_sha256: str) -> bool:
        """
        Verify the IPSW archive SHA256 matches expected_sha256.
        Raises:
            IntegrityError if mismatch.
        """
        found = self._sha256sum(self.ipsw_path)
        if found.lower() != expected_sha256.lower():
            raise IntegrityError(f"SHA256 mismatch (expected {expected_sha256}, got {found})")
        return True
    def export_manifest(self, output_name: Path) -> Path:
        """
        Export the BuildManifest from the IPSW into the toolkit sandbox.
        Returns the path to the written file in the sandbox.
        """
        with self.open_ipsw() as ipsw:
            # build_manifest may be an object or raw bytes depending on original parser.
            bm = getattr(ipsw, "build_manifest", None)
            if bm is None:
                raise IPSWToolkitError("IPSW has no build_manifest attribute")
            # Try common attribute names to access bytes; be conservative.
            manifest_bytes = None
            for attr in ("data", "plist", "raw", "bytes"):
                if hasattr(bm, attr):
                    try:
                        manifest_bytes = getattr(bm, attr)
                        break
                    except Exception:
                        continue
            if manifest_bytes is None:
                # Fallback: attempt to ask ipsw for the BuildManifest file by name
                try:
                    # The original code read build manifest at init; try to access via archive
                    manifest_bytes = ipsw.build_manifest  # type: ignore
                except Exception:
                    raise IPSWToolkitError("Could not obtain BuildManifest bytes from IPSW")
            # Ensure bytes
            if not isinstance(manifest_bytes, (bytes, bytearray)):
                # If it's a plist-like object, attempt to dump to bytes using plistlib
                import plistlib
                try:
                    manifest_bytes = plistlib.dumps(manifest_bytes)
                except Exception:
                    raise IPSWToolkitError("BuildManifest exists but cannot be serialized to bytes")
            out_path = (self._sandbox_dir / output_name.name).resolve()
            # atomic write to sandbox
            tmp = out_path.with_suffix(out_path.suffix + ".tmp")
            with tmp.open("wb") as f:
                f.write(manifest_bytes)
            tmp.replace(out_path)
            return out_path
    def report_info(self) -> Dict[str, object]:
        """
        Return metadata summary (restore_version, system_version, file count) as a dict.
        Values are strings where possible; bytes are decoded with errors='ignore'.
        """
        with self.open_ipsw() as ipsw:
            def decode_if_bytes(v):
                if isinstance(v, (bytes, bytearray)):
                    try:
                        return v.decode("utf-8", errors="ignore")
                    except Exception:
                        return str(v)
                return v
            restore = getattr(ipsw, "restore_version", None)
            system = getattr(ipsw, "system_version", None)
            filelist = getattr(ipsw, "filelist", None)
            return {
                "restore_version": decode_if_bytes(restore),
                "system_version": decode_if_bytes(system),
                "num_files": len(filelist) if filelist is not None else None,
            }
    def safe_write_file(self, rel_path: str, data: bytes) -> Path:
        """
        Safely write a file into the sandbox, preventing path traversal.
        Returns the absolute Path to the written file.
        """
        rel = Path(rel_path)
        if rel.is_absolute():
            raise IPSWToolkitError("Absolute output paths are not allowed; must be relative to sandbox")
        # resolve target within sandbox
        target = (self._sandbox_dir / rel).resolve()
        if self._sandbox_dir not in target.parents and self._sandbox_dir != target:
            # Prevent path traversal outside sandbox
            raise IPSWToolkitError("Requested output is outside the sandbox")
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        with tmp.open("wb") as f:
            f.write(data)
        tmp.replace(target)
        return target
    # Optional helper to create an abbreviated text report
    def report_text(self) -> str:
        info = self.report_info()
        lines = [
            f"Restore Version: {info.get('restore_version')}",
            f"System Version: {info.get('system_version')}",
            f"Number of files in IPSW: {info.get('num_files')}",
            f"Sandbox path: {self._sandbox_dir}",
        ]
        return "\n".join(lines)