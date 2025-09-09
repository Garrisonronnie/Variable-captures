📘 BFD Monitor Dynamic
🔍 Overview
BFD Monitor Dynamic is a Python-based, lightweight, extensible SNMP polling and webhook receiver system designed to monitor the operational status of Bidirectional Forwarding Detection (BFD) sessions on network devices.
Inspired by—but not modifying—the native BFD protocol or its implementations on routers/switches, this tool provides external observability into BFD status using standard SNMP OIDs.
🧠 What is BFD?
BFD (Bidirectional Forwarding Detection) is a protocol used in IP networks to detect link or path failures rapidly between two forwarding engines. BFD is used in high-availability networks where detection of failure must happen in milliseconds.
However, while BFD is robust and fast, many environments lack centralized monitoring or external visibility into BFD session health without directly logging into routers.
🚀 Purpose of This Tool
This tool does not modify or replace BFD in any way. Instead, it:
Passively polls BFD operational status via SNMP from network devices
Logs BFD state changes to a local SQLite audit database
Optionally accepts authenticated webhooks from external tools/scripts reporting BFD-related issues
Provides a simple REST API to query historical BFD state changes
This makes it easy to:
Integrate with dashboards, monitoring systems, or alerting tools
Maintain an independent audit trail of BFD-related events
Build proactive monitoring workflows around critical session failures
🔧 How It Works
The system is composed of the following components:
Component	Description
SNMP Poller	Periodically queries configured devices for their BFD operational status using a provided OID.
Webhook Listener (Flask)	Accepts JSON webhooks about BFD failures, verifies HMAC signatures, and logs the events.
SQLite Audit DB	Stores a persistent record of BFD events (from both SNMP and webhooks).
REST API	Exposes GET /events to retrieve recent events for dashboards or integrations.
🛠️ Setup Instructions
1. 📦 Install Dependencies
Ensure Python 3.8+ is installed, then install required packages:
pip install flask pysnmp
Optional: Create a virtual environment for isolation.
2. 🗂️ Configuration
You can configure settings via command-line flags or environment variables.
Example via CLI:
python bfd_monitor.py \
    --snmp-community public \
    --device-name edge-router \
    --device-host 192.0.2.1 \
    --bfd-oper-status-oid 1.3.6.1.2.1.285.1.1.1.2 \
    --webhook-secret supersecrethmac \
    --poll-interval 10
Or set as environment variables:
export SNMP_COMMUNITY=public
export DEVICE_HOST=192.0.2.1
export DEVICE_NAME=edge-router
export WEBHOOK_HMAC_SECRET=supersecrethmac
python bfd_monitor.py
3. ✅ SNMP Requirements
Ensure SNMP is enabled on your devices and that the OID for BFD operational status is accessible.
Default OID: 1.3.6.1.2.1.285.1.1.1.2 (example; verify with your device vendor)
Devices should respond to SNMP GET requests for this OID.
4. 🔐 Webhook Usage (Optional)
You can post alerts from external systems to the Flask server:
Endpoint: POST /webhook/failure
Header: X-Hub-Signature-256: sha256=<hmac-hex>
Body (JSON):
{
  "device": "edge-router",
  "reason": "bfd_down_alert",
  "evidence": {
    "interface": "eth0",
    "remote_ip": "192.0.2.10"
  }
}
Webhook HMAC signature is verified using your configured secret.
5. 🌐 API Access
List recent events:
curl http://localhost:8080/events?limit=50
Returns JSON-formatted audit logs.
🧪 Sample Output
Logged Event (SNMP):
{
  "id": 12,
  "ts": "2025-09-05T12:00:00Z",
  "device": "edge-router",
  "event_type": "snmp_poll",
  "details": {
    "oper_status": "down"
  }
}
Logged Event (Webhook):
{
  "id": 13,
  "ts": "2025-09-05T12:00:05Z",
  "device": "edge-router",
  "event_type": "bfd_down_alert",
  "details": {
    "interface": "eth0",
    "remote_ip": "192.0.2.10"
  }
}
📌 Design Principles
Non-invasive: Does not modify BFD behavior on devices.
Composable: Easily integrates with Prometheus, Grafana, Elastic, etc.
Portable: Runs on any Linux/Unix/Windows host with Python.
Auditable: Local DB stores all historical events.
Secure: HMAC verification prevents spoofed webhook data.
🔄 Extending It
You can easily extend this tool by:
Adding support for multiple OIDs or vendors
Triggering alerts via email, Slack, or pager
Exporting data to Prometheus or other systems
Visualizing BFD state transitions in Grafana or Kibana
📥 Contributions
Pull requests, issues, and ideas are welcome! Please ensure code is formatted using black
 and includes clear docstrings/comments.
📄 License
This project is provided as-is under the MIT License.
🧠 Credits
Inspired by BFD protocol behavior and the need for external, SNMP-based observability.
Uses pysnmp for SNMP interaction, Flask for webhooks, and sqlite3 for persistent local auditing.
❓FAQ
Q: Does this modify BFD on devices?
A: No. This tool is entirely external and passive. It reads BFD state via SNMP and does not interact with the protocol stack directly.
Q: Can I monitor multiple devices?
⚖️ Legal Notice & Responsible Use
✅ Legal Use
This tool is 100% legal to use under the following conditions:
You own, operate, or have explicit permission to monitor the network devices being queried.
You are using standard SNMP polling — an industry-standard and permitted method of querying device state.
You are not modifying or interfering with the actual BFD protocol or device configuration.
❌ Prohibited Use
You must not use this tool for:
Polling or scanning unauthorized or third-party devices.
Attempting to exploit SNMP vulnerabilities or weaknesses.
Using default SNMP communities (like public) without securing access or restricting IPs.
Gathering data from networks you do not own or administer.
⚠️ Ethical Reminder
Just because a device responds to SNMP does not mean you’re authorized to query it.
Unauthorized use of SNMP can be interpreted as unauthorized access under various laws (e.g., Computer Fraud and Abuse Act in the U.S., or Cybercrime Acts in other countries). Always document permission and audit your activities.
👮‍♂️ Compliance Best Practices
To stay compliant and responsible:
Use strong SNMP community strings (avoid public, private).
Limit SNMP access via ACLs or firewall rules.
Use read-only SNMP credentials.
Log all polling and webhook activity (already built-in via the audit DB).
Inform your organization’s network/security team of any deployment.
📌 TL;DR
✅ Legal and safe — when used on your own devices or with explicit authorization.
❌ Illegal and unethical — if used to monitor unauthorized or external networks.
A: The current version supports one device, but the code structure allows for easy expansion to multiple devices by modifying the devices list.
bfd_monitor_dynamic.py – Functional Chart
Category
What It Does
How It Works
Legal / Safety
Runs in sandboxed monitoring mode only.
No rerouting, no reconfiguration, no injected traffic.
License
MIT License, copyright 2025 Ronnie Garrison.
Free to use/modify with attribution, â€œas-isâ€ (no warranty).
Local Detection
Auto-detects local IP + current user at runtime.
Uses a UDP socket to 8.8.8.8 (Google DNS) and env vars (USER, USERNAME).
Configuration
Supports command-line args + environment vars.
SNMP settings, poll interval, OIDs, SQLite DB path, webhook secret, logging, etc.
Logging
Rotating file + console logging.
Writes logs with timestamps, levels (INFO, WARNING, ERROR).
Database (SQLite)
Stores audit logs of events.
Thread-safe AuditDB class with insert, fetch_recent, and close.
Auditing
Records each poll + failure into DB and logs.
JSON-encoded details stored with timestamp, device name, event type.
SNMP Polling
Queries BFD operational status OID from devices.
Uses pysnmp to run getCmd() on target devices.
Failure Detection
Detects BFD down/not operational states.
Logs warnings + inserts audit event (bfd_failure).
Threaded Poller
Continuously polls devices at interval until stopped.
Uses a threading.Event to manage safe shutdown.
🔧 It is a BFD status monitor with live device management, event auditing, and webhook ingestion
Component	What it actually does
✅ SNMP Polling	Polls devices repeatedly using SNMP to check BFD operational status.
✅ Status Interpretation	Maps raw SNMP values to readable statuses like up, down, or unknown.
✅ Live Device Inventory	Lets you add/remove SNMP devices at runtime via HTTP (read-write behavior).
✅ Webhook Receiver	Accepts and authenticates signed webhook requests, logs them in DB.
✅ Audit Logging	Logs all events (polls, webhooks, device changes) into a SQLite DB.
✅ Event Pruning	Keeps DB size in check by auto-deleting oldest rows when max is exceeded.
✅ REST API	Exposes endpoints to view health, metrics, events, and devices.
✅ Metrics	Keeps internal counters (polls, failures, webhooks, etc.) for observability.
✅ Shutdown Support	Supports graceful shutdown via secure HTTP request or OS signal.
