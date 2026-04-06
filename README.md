
Redmine Service Alert

Minimal incident notification system:

shows a global alert banner in Redmine
optionally shows a popup (once per browser session/version)
sends incident start/end notifications to Bitrix24 chat
Scope

This project is intentionally minimal.

Supported:

one active alert at a time
API-based activation/deactivation
Redmine banner + optional popup
Bitrix24 notification via webhook

Not supported:

multiple alerts
incident history
scheduling
UI editor
acknowledgements
Structure

plugins/redmine_service_alert — Redmine plugin
tools/incident_notifier.py — notifier

Storage

State is stored in:

Setting.plugin_redmine_service_alert

Fields:

enabled
severity (info | warning | critical)
title
message
link_url
show_popup
version
API

Activate:

curl -X POST "http://localhost:3000/service_alert/activate
"
-H "Content-Type: application/json"
-H "X-Service-Alert-Token: TOKEN"
-d '{
"severity": "critical",
"title": "Service outage",
"message": "Operations may fail",
"link_url": "",
"show_popup": true
}'

Deactivate:

curl -X POST "http://localhost:3000/service_alert/deactivate
"
-H "Content-Type: application/json"
-H "X-Service-Alert-Token: TOKEN"
-d '{}'

Current:

curl -X GET "http://localhost:3000/service_alert/current
"
-H "X-Service-Alert-Token: TOKEN"

Install

cp -R plugins/redmine_service_alert /path/to/redmine/plugins/

export REDMINE_SERVICE_ALERT_TOKEN='your-token'

docker compose restart redmine

Notifier

export REDMINE_BASE_URL='http://localhost:3000
'
export REDMINE_ALERT_TOKEN='your-token'
export BITRIX_WEBHOOK_URL='https://...'
export BITRIX_DIALOG_ID='chat123'

Start:

python tools/incident_notifier.py start
--severity critical
--title "Service outage"
--message "Operations may fail"
--show-popup true

End:

python tools/incident_notifier.py end
--message "Service restored"

Production

volumes:

/opt/redmine-service-alert/plugins/redmine_service_alert:/usr/src/redmine/plugins/redmine_service_alert:ro
Token

openssl rand -hex 32

UI
banner when enabled=true
popup once per version
sessionStorage used
Flow

START:
notifier → activate → banner → popup → Bitrix

END:
notifier → deactivate → hide → Bitrix

