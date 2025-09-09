#!/usr/bin/env python3
"""
bfd_monitor_dynamic.py
BFD Monitor (No AI, No Rerouting, No Reconfiguration)
LEGAL + SAFE USAGE
------------------
- This script is for sandboxed monitoring of your own devices.
- It auto-detects local IP and current user dynamically at runtime.
- It does NOT alter routing, reconfigure devices, or inject traffic.
- Only run on systems you are authorized to monitor.
LICENSE
-------
MIT License
Copyright (c) 2025 Ronnie Garrison
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
This audit logging module is intended exclusively for testing, development, and internal systems use.
It provides a lightweight, thread-safe interface to an SQLite database for recording and retrieving event logs.
Access to this module must be strictly restricted to authorized personnel only, ensuring the protection of.
sensitive data and compliance with organizational security policies.
This module is not designed, certified, or recommended for production or external deployment.
Users must adhere to all applicable laws, regulations, and organizational guidelines related to data privacy, security,
audit logging when using this module.
By using this software, users acknowledge their responsibility to safeguard data and maintain confidentiality.
you must fill the place holders in with your current details and setup follow readme.md for details.
# BFD Monitor - read-only SNMP poller + webhook receiver
MIT License
Copyright (c) 2025 Ronnie Garrison
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import logging
import os
import signal
import sqlite3
import threading
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Iterable, List, Optional
from flask import Flask, abort, jsonify, request
try:
    from pysnmp.hlapi import (
        CommunityData,
        ContextData,
        ObjectIdentity,
        ObjectType,
        SnmpEngine,
        UdpTransportTarget,
        getCmd,
    )
except Exception as exc:
    raise ImportError(
        "pysnmp is required. Install with: pip install pysnmp\nOriginal error: {}".format(exc)
    )
# -----------------------------
# Helpers / Defaults
# -----------------------------
def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
LOCAL_IP = get_local_ip()
LOCAL_USER = os.getenv("USER") or os.getenv("USERNAME") or "unknown"
# -----------------------------
# CLI / ENV configuration
# -----------------------------
def build_config_from_args() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="BFD Monitor (read-only SNMP poll + webhook)")
    parser.add_argument("--snmp-community", default=os.getenv("SNMP_COMMUNITY", "public"))
    parser.add_argument("--snmp-port", type=int, default=int(os.getenv("SNMP_PORT", "161")))
    parser.add_argument("--poll-interval", type=int, default=int(os.getenv("POLL_INTERVAL", "5")))
    parser.add_argument("--bfd-oper-status-oid", default=os.getenv("BFD_OPER_STATUS_OID", "1.3.6.1.2.1.285.1.1.1.2"))
    parser.add_argument("--webhook-secret", default=os.getenv("WEBHOOK_HMAC_SECRET", "replace-with-strong-secret"))
    parser.add_argument("--bind-host", default=os.getenv("BIND_HOST", "0.0.0.0"))
    parser.add_argument("--bind-port", type=int, default=int(os.getenv("BIND_PORT", "8080")))
    parser.add_argument("--sqlite-db", default=os.getenv("SQLITE_DB", "bfd_monitor_dynamic.db"))
    parser.add_argument("--log-file", default=os.getenv("LOG_FILE", "bfd_monitor_dynamic.log"))
    parser.add_argument("--audit-max", type=int, default=int(os.getenv("AUDIT_MAX", "1000")))
    parser.add_argument("--device-name", default=os.getenv("DEVICE_NAME", f"local-device-{LOCAL_USER}"))
    parser.add_argument("--device-host", default=os.getenv("DEVICE_HOST", LOCAL_IP))
    parser.add_argument("--devices-file", default=os.getenv("DEVICES_FILE", ""))
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    return vars(parser.parse_args())
CONFIG = build_config_from_args()
# -----------------------------
# Logging Setup
# -----------------------------
LOG = logging.getLogger("bfd_monitor")
try:
    LOG.setLevel(getattr(logging, str(CONFIG.get("log_level", "INFO")).upper()))
except Exception:
    LOG.setLevel(logging.INFO)
log_dir = os.path.dirname(CONFIG["log_file"])
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)
file_handler = RotatingFileHandler(CONFIG["log_file"], maxBytes=5 * 1024 * 1024, backupCount=3)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s"))
LOG.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s"))
LOG.addHandler(console_handler)
# -----------------------------
# Database
# -----------------------------
class AuditDB:
    """Thread-safe audit logger for storing events to SQLite."""
    def __init__(self, path: str, max_rows: int = 1000) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._max_rows = max_rows
        self._conn = sqlite3.connect(self._path, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
        # Use WAL for concurrency where supported
        try:
            self._conn.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass
        self._init_schema()
    def _init_schema(self) -> None:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    device TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    details TEXT NOT NULL
                );
                """
            )
            self._conn.commit()
    def insert(self, device: str, event_type: str, details: Dict[str, Any]) -> None:
        payload = json.dumps(details, default=str)
        ts = datetime.utcnow().isoformat() + "Z"
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                "INSERT INTO events (ts, device, event_type, details) VALUES (?, ?, ?, ?)",
                (ts, device, event_type, payload),
            )
            self._conn.commit()
            self._prune_if_needed(cur)
    def _prune_if_needed(self, cur: sqlite3.Cursor) -> None:
        # prune oldest rows if above max
        try:
            cur.execute("SELECT COUNT(*) FROM events;")
            (count,) = cur.fetchone() or (0,)
            if count > self._max_rows:
                # delete the oldest rows to reduce to max_rows
                to_delete = count - self._max_rows
                LOG.debug("Pruning %d old audit rows", to_delete)
                cur.execute("DELETE FROM events WHERE id IN (SELECT id FROM events ORDER BY id ASC LIMIT ?)",
                (to_delete,))
                self._conn.commit()
        except Exception:
            LOG.exception("Failed during audit prune")
    def fetch_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        limit = min(limit, self._max_rows)
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                "SELECT id, ts, device, event_type, details FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = cur.fetchall()
        out: List[Dict[str, Any]] = []
        for r in rows:
            try:
                details = json.loads(r[4])
            except Exception:
                details = {"raw": r[4]}
            out.append({"id": r[0], "ts": r[1], "device": r[2], "event_type": r[3], "details": details})
        return out
    def close(self) -> None:
        with self._lock:
            try:
                self._conn.commit()
            except Exception as e:
                LOG.exception("Failed to commit DB: %s", e)
            try:
                self._conn.close()
            except Exception:
                pass
# Global DB instance
DB = AuditDB(CONFIG["sqlite_db"], max_rows=int(CONFIG.get("audit_max", 1000)))
def audit(device: str, event_type: str, details: Dict[str, Any]) -> None:
    """Insert and log audit events."""
    try:
        DB.insert(device, event_type, details)
        LOG.info("AUDIT %s %s %s", device, event_type, json.dumps(details, default=str))
    except Exception:
        LOG.exception("Failed to write audit record for %s", device)
# -----------------------------
# SNMP polling
# -----------------------------
def snmp_get(
    oid: str,
    target: str,
    community: str,
    port: int,
    timeout: int = 2,
    retries: int = 1,
) -> Optional[str]:
    """Perform a single SNMP GET and return the string value or None on failure."""
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((target, port), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )
        errorIndication, errorStatus, _, varBinds = next(iterator)
        if errorIndication:
            LOG.debug("SNMP errorIndication from %s: %s", target, errorIndication)
            return None
        if errorStatus:
            LOG.debug("SNMP errorStatus from %s: %s", target, errorStatus.prettyPrint())
            return None
        for varBind in varBinds:
            return str(varBind[1])
    except StopIteration:
        return None
    except Exception:
        LOG.exception("Unexpected error during SNMP GET to %s", target)
        return None
_stop_event = threading.Event()
_metrics_lock = threading.Lock()
METRICS: Dict[str, int] = {"polls": 0, "failures": 0, "webhooks": 0, "audit_events": 0}
def interpret_bfd_status(raw: Optional[str]) -> str:
    """Map common SNMP values to a normalized status: 'up', 'down', 'unknown'."""
    if raw is None:
        return "unknown"
    v = str(raw).strip().lower()
    # Common numeric mapping: 1=up,2=down (varies by MIB)
    if v in ("1", "up", "operational", "ok"):
        return "up"
    if v in ("2", "down", "notoperational", "not_operational", "fault"):
        return "down"
    # anything else is unknown but keep original
    return "unknown"
def poll_bfd_states(devices: Iterable[Dict[str, Any]], snmp_cfg: Dict[str, Any], stop_event: threading.Event) -> None:
    """Poll configured devices for BFD operational status periodically until stop_event is set."""
    poll_interval = int(snmp_cfg.get("poll_interval", 5))
    community = snmp_cfg.get("community", "public")
    port = int(snmp_cfg.get("port", 161))
    oid = snmp_cfg.get("bfd_oper_status_oid")
    if not oid:
        LOG.error("No BFD OID configured, poller exiting.")
        return
    LOG.info("Starting SNMP poller for device(s) every %s second(s)", poll_interval)
    while not stop_event.is_set():
        for dev in list(devices):  # snapshot
            if stop_event.is_set():
                break
            try:
                target_host = dev.get("host")
                METRICS_UPDATE = False
                op_raw = snmp_get(oid, target_host, community, port)
                op = interpret_bfd_status(op_raw)
                audit(dev.get("name", target_host), "snmp_poll", {"oper_status_raw": op_raw, "oper_status": op})
                with _metrics_lock:
                    METRICS["polls"] += 1
                    METRICS["audit_events"] += 1
                if op == "down":
                    LOG.warning("BFD failure detected on %s (status=%s)", dev.get("name", target_host), op_raw)
                    audit(dev.get("name", target_host), "bfd_failure", {"status_raw": op_raw, "status": op})
                    with _metrics_lock:
                        METRICS["failures"] += 1
            except Exception:
                LOG.exception("Error while polling device %s", dev)
        # wait with early exit and support small granularity
        for _ in range(int(poll_interval * 10)):
            if stop_event.is_set():
                break
            time.sleep(0.1)
# -----------------------------
# Device inventory helpers
# -----------------------------
def load_devices_from_file(path: str) -> List[Dict[str, Any]]:
    if not path:
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return data
        LOG.warning("Devices file %s did not contain a list; ignoring", path)
    except FileNotFoundError:
        LOG.info("Devices file %s not found; starting with empty inventory", path)
    except Exception:
        LOG.exception("Failed to load devices file %s", path)
    return []
def save_devices_to_file(path: str, devices: Iterable[Dict[str, Any]]) -> None:
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(list(devices), fh, indent=2)
    except Exception:
        LOG.exception("Failed to write devices file %s", path)
# -----------------------------
# Flask app (simple API)
# -----------------------------
app = Flask(__name__)
def verify_hmac_signature(secret: str, payload: bytes, signature_header: str) -> bool:
    """
    Verify HMAC-SHA256 signature; support header values like:
     - 'sha256=hex....'
     - 'hex...'
    """
    if not signature_header:
        return False
    try:
        # some providers use header names like X-Hub-Signature-256 or X-Signature-256; payload header passed in
        sent = signature_header
        if signature_header.startswith("sha256="):
            sent = signature_header.split("=", 1)[1]
        mac = hmac.new(secret.encode("utf-8"), payload or b"", hashlib.sha256)
        expected = mac.hexdigest()
        return hmac.compare_digest(expected, sent)
    except Exception:
        return False
@app.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat() + "Z"})
@app.route("/ready", methods=["GET"])
def ready() -> Any:
    # Simple readiness: DB open and poller not stopped
    ready_ok = not _stop_event.is_set()
    return jsonify({"ready": ready_ok, "db": os.path.exists(CONFIG["sqlite_db"]),
        "time": datetime.utcnow().isoformat() + "Z"})
@app.route("/events", methods=["GET"])
def events() -> Any:
    limit = int(request.args.get("limit", CONFIG.get("audit_max", 100)))
    results = DB.fetch_recent(limit)
    return jsonify(results)
@app.route("/metrics", methods=["GET"])
def metrics() -> Any:
    with _metrics_lock:
        return jsonify(METRICS.copy())
@app.route("/webhook", methods=["POST"])
def webhook() -> Any:
    # Basic webhook HMAC validation
    payload = request.get_data()
    # Accept various header keys that providers might use
    signature = (
        request.headers.get("X-Hub-Signature-256")
        or request.headers.get("X-Signature-256")
        or request.headers.get("X-Hub-Signature")
        or ""
    )
    if not verify_hmac_signature(CONFIG.get("webhook_secret", ""), payload, signature):
        LOG.warning("Rejected webhook due to bad signature")
        abort(401, description="Invalid signature")
    try:
        data = request.get_json(force=True)
    except Exception:
        LOG.exception("Failed to parse JSON payload")
        abort(400, description="Invalid JSON")
    # Record webhook into audit DB
    audit(CONFIG.get("device_name", "unknown"), "webhook_received", {"payload": data})
    with _metrics_lock:
        METRICS["webhooks"] += 1
        METRICS["audit_events"] += 1
    return jsonify({"status": "accepted"}), 202
# simple in-memory device inventory (thread-safe)
_devices_lock = threading.Lock()
_devices: List[Dict[str, Any]] = []
@app.route("/devices", methods=["GET"])
def list_devices() -> Any:
    with _devices_lock:
        return jsonify(list(_devices))
@app.route("/devices", methods=["POST"])
def add_device() -> Any:
    try:
        data = request.get_json(force=True)
    except Exception:
        abort(400, description="Invalid JSON")
    if not isinstance(data, dict) or "host" not in data:
        abort(400, description="device object with 'host' required")
    device = {"name": data.get("name") or data["host"], "host": data["host"]}
    with _devices_lock:
        _devices.append(device)
        save_devices_to_file(CONFIG.get("devices_file", ""), _devices)
    audit(device["name"], "device_add", {"host": device["host"]})
    return jsonify(device), 201
@app.route("/devices/<string:host>", methods=["DELETE"])
def delete_device(host: str) -> Any:
    removed = None
    with _devices_lock:
        for i, d in enumerate(_devices):
            if d.get("host") == host or d.get("name") == host:
                removed = _devices.pop(i)
                break
        save_devices_to_file(CONFIG.get("devices_file", ""), _devices)
    if removed:
        audit(removed.get("name", host), "device_remove", {"host": host})
        return jsonify({"removed": removed})
    abort(404, description="device not found")
@app.route("/shutdown", methods=["POST"])
def shutdown() -> Any:
    # Protected shutdown endpoint — requires the same webhook secret (short-lived deployments should rotate)
    token = request.headers.get("Authorization") or ""
    # Accept Authorization: Bearer <secret> or direct secret
    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1]
    if not hmac.compare_digest(str(token), str(CONFIG.get("webhook_secret", ""))):
        abort(403, description="Forbidden")
    # Initiate graceful shutdown
    threading.Thread(target=_shutdown_async).start()
    return jsonify({"shutting_down": True})
def _shutdown_async() -> None:
    LOG.info("Shutdown via HTTP requested")
    _stop_event.set()
    # allow the main thread to reach finally and exit; flask dev server will stop when process exits
    time.sleep(0.5)
# -----------------------------
# Graceful shutdown & main
# -----------------------------
def _signal_handler(signum, frame):
    LOG.info("Received signal %s, shutting down", signum)
    _stop_event.set()
def main() -> None:
    # Register signal handlers
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    # Load devices from file if provided
    devices_file = CONFIG.get("devices_file") or ""
    initial_devices = load_devices_from_file(devices_file)
    if not initial_devices:
        # default device from CLI
        initial_devices = [
            {"name": CONFIG.get("device_name", "local"), "host": CONFIG.get("device_host", LOCAL_IP)},
        ]
    with _devices_lock:
        _devices.clear()
        _devices.extend(initial_devices)
    # SNMP configuration for poller
    snmp_cfg = {
        "community": CONFIG.get("snmp_community"),
        "port": CONFIG.get("snmp_port"),
        "poll_interval": CONFIG.get("poll_interval"),
        "bfd_oper_status_oid": CONFIG.get("bfd_oper_status_oid"),
    }
    # Start poller thread
    poll_thread = threading.Thread(target=poll_bfd_states, args=(_devices, snmp_cfg, _stop_event), daemon=True)
    poll_thread.start()
    # Start Flask app (note: for production, use gunicorn/uvicorn + proxy)
    bind_host = CONFIG.get("bind_host", "0.0.0.0")
    bind_port = int(CONFIG.get("bind_port", 8080))
    LOG.info("Starting HTTP server on %s:%s", bind_host, bind_port)
    try:
        # Flask's built-in server is fine for testing. In production use a WSGI server.
        app.run(host=bind_host, port=bind_port, threaded=True, use_reloader=False)
    except Exception:
        LOG.exception("HTTP server raised an exception")
    finally:
        LOG.info("Shutting down poller...")
        _stop_event.set()
        poll_thread.join(timeout=5)
        DB.close()
        LOG.info("Shutdown complete.")
if __name__ == "__main__":
    main()