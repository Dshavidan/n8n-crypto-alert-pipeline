# Setup Guide

## 1. Start n8n Locally

```bash
cp .env.example .env
docker compose up -d
```

Open `http://localhost:5678` and create the local owner account.

## 2. Import the Workflow

In n8n:

1. Open `Workflows`.
2. Select `Import from File`.
3. Import `workflows/crypto-alert-pipeline.json`.
4. Save the workflow.
5. Run it manually once before activating the schedule.

## 3. Configure Alerts

The workflow contains a disabled webhook delivery node. To use it:

1. Set `ALERT_WEBHOOK_URL` in `.env`.
2. Restart Docker with `docker compose up -d`.
3. Open the `Send Alert Webhook` node.
4. Enable the node.
5. Test the workflow manually.

You can replace the webhook node with Telegram, Slack, Discord, email, or Google Sheets depending on the target channel.

## 4. Change the Watchlist

The example config lives in `config/watchlist.example.json`. For the n8n workflow itself, update both:

- The `ids` query parameter in `Fetch Market Data`
- The `coins` list inside `Normalize and Score`

This keeps the visual workflow self-contained and easy to import.

## 5. Validate the Project

```bash
python scripts/validate_project.py
```

The CI workflow runs the same validation on every push and pull request.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| n8n opens but workflow is missing | Import `workflows/crypto-alert-pipeline.json` manually |
| API node returns 429 | Wait, reduce schedule frequency, or configure a paid CoinGecko API key |
| Alert webhook fails | Check `ALERT_WEBHOOK_URL`, restart Docker, and enable the node |
| Workflow imports but does not alert | Lower thresholds or use `docs/sample-market-response.json` as a manual test reference |
