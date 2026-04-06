# Redmine Service Alert MVP

Minimal incident notification MVP:
- Redmine plugin (`redmine_service_alert`) manages one global alert state in plugin settings.
- Python notifier (`tools/incident_notifier.py`) toggles Redmine alert and sends Bitrix24 chat messages.

## Repository layout

```text
.
├── README.md
├── .gitignore
├── tools/
│   └── incident_notifier.py
└── plugins/
    └── redmine_service_alert/
        ├── init.rb
        ├── config/routes.rb
        ├── app/controllers/service_alert_controller.rb
        ├── app/views/service_alert/_alert.html.erb
        ├── assets/javascripts/service_alert.js
        ├── assets/stylesheets/service_alert.css
        └── lib/redmine_service_alert/hooks/view_layouts_hook.rb
```

## Redmine plugin behavior (MVP)

State is stored **only** in `Setting.plugin_redmine_service_alert` with these keys:
- `enabled` (boolean)
- `severity` (`info|warning|critical`)
- `title` (string)
- `message` (string)
- `link_url` (string)
- `show_popup` (boolean)
- `version` (integer)

Endpoints:
- `POST /service_alert/activate`
- `POST /service_alert/deactivate`
- `GET /service_alert/current` (debug/smoke)

Authentication:
- Required header: `X-Service-Alert-Token`
- Compared with env: `REDMINE_SERVICE_ALERT_TOKEN`
- Unauthorized returns HTTP 401 and JSON error.

UI:
- When `enabled=true`: global persistent banner appears on Redmine pages.
- Severity-specific classes: `service-alert-info`, `service-alert-warning`, `service-alert-critical`.
- When `enabled=true` and `show_popup=true`: popup appears once per browser session for current `version`.
- Popup seen key: `service_alert_seen_version_<version>` in `sessionStorage`.

## Install plugin into Redmine

1. Copy plugin folder into Redmine plugins directory:
   ```bash
   cp -R plugins/redmine_service_alert /path/to/redmine/plugins/
   ```
2. Set shared token for Redmine process:
   ```bash
   export REDMINE_SERVICE_ALERT_TOKEN='replace-with-strong-token'
   ```
3. Restart Redmine.

No custom migration is required for this MVP.

## Notifier environment variables

Set before running `tools/incident_notifier.py`:

- `REDMINE_BASE_URL` (example: `https://redmine.example.com`)
- `REDMINE_ALERT_TOKEN` (must match `REDMINE_SERVICE_ALERT_TOKEN`)
- `BITRIX_WEBHOOK_URL` (example: `https://company.bitrix24.ru/rest/1/abcdef`)
- `BITRIX_DIALOG_ID` (chat/dialog identifier)

## API examples (curl)

Activate:

```bash
curl -X POST "https://redmine.example.com/service_alert/activate" \
  -H "Content-Type: application/json" \
  -H "X-Service-Alert-Token: replace-with-strong-token" \
  -d '{
    "severity": "critical",
    "title": "Сбой платежного сервиса",
    "message": "Возможны ошибки при проведении операций. Идут восстановительные работы.",
    "link_url": "https://status.example.com/inc-123",
    "show_popup": true
  }'
```

Deactivate:

```bash
curl -X POST "https://redmine.example.com/service_alert/deactivate" \
  -H "Content-Type: application/json" \
  -H "X-Service-Alert-Token: replace-with-strong-token" \
  -d '{}'
```

Current state:

```bash
curl -X GET "https://redmine.example.com/service_alert/current" \
  -H "X-Service-Alert-Token: replace-with-strong-token"
```

## Notifier usage examples

Start incident:

```bash
python tools/incident_notifier.py start \
  --severity critical \
  --title "Сбой платежного сервиса" \
  --message "Возможны ошибки при проведении операций. Идут восстановительные работы." \
  --link-url "https://status.example.com/inc-123" \
  --show-popup true
```

End incident:

```bash
python tools/incident_notifier.py end \
  --message "Работа платежного сервиса восстановлена."
```

## Manual smoke test

1. Configure plugin in Redmine, set `REDMINE_SERVICE_ALERT_TOKEN`, and restart Redmine.
2. Verify plugin loads on startup by checking Redmine logs for plugin initialization and opening any Redmine page without plugin-related errors.
3. Open browser developer tools on a Redmine page and verify plugin assets are loaded:
   - `service_alert.css`
   - `service_alert.js`
4. Call `GET /service_alert/current` with valid token and verify default state.
5. Call `POST /service_alert/activate` and verify:
   - HTTP 200,
   - `enabled=true`, incremented `version`,
   - banner renders on Redmine pages,
   - popup opens if `show_popup=true`.
6. Refresh page in same browser session and verify popup does not reopen for the same `version`.
7. Call `POST /service_alert/activate` again (new payload) and verify `version` increments and popup opens once for the new version.
8. Call `POST /service_alert/deactivate` and verify banner/popup are no longer rendered.
9. Call any endpoint with missing/wrong token and verify HTTP 401.
10. Run notifier `start` and `end`; verify Redmine state toggles and Bitrix chat gets messages.

## Expected integration flow

Incident start:
1. Operator/system runs notifier `start`.
2. Notifier calls Redmine `/service_alert/activate`.
3. Redmine stores current alert in plugin settings and increments version.
4. Redmine pages display persistent banner (+ optional one-time popup per version/session).
5. Notifier sends plain-text message to Bitrix24 chat via `im.message.add`.

Incident end:
1. Operator/system runs notifier `end`.
2. Notifier calls Redmine `/service_alert/deactivate`.
3. Redmine turns banner/popup off by setting `enabled=false`.
4. Notifier sends recovery message to same Bitrix24 chat.
