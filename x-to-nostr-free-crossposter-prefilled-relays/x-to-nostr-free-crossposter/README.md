# X → Nostr Free Crossposter (via Nitter RSS + GitHub Actions)

This repository runs **for free** using GitHub Actions on a schedule to read an RSS feed from a public Nitter instance and post new items to **Nostr**. No paid X API needed.

> ⚠️ **Important**: Using third‑party mirrors (like Nitter) may violate X’s Terms of Service. Proceed at your own risk. For policy‑compliant, reliable mirroring, use the official paid X API.

## How it works
- A GitHub Actions workflow runs every 5 minutes (you can change the schedule).
- It reads `RSS_URL` (a Nitter RSS feed for the account you want to mirror, e.g. `https://nitter.net/BillSimmons/rss`).
- New items are posted to your Nostr relays using your bot’s `nsec` key.
- A small state file (`state/last_id.txt`) is committed back to the repo so duplicates are avoided across runs.

### Default relays (pre-filled)
This template already uses these free public relays by default (you can override with a `NOSTR_RELAYS` secret or local env):

```
wss://relay.damus.io
wss://nos.lol
wss://relay.snort.social
wss://relay.primal.net
wss://nostr.mom
```

## Quick start

1. **Create a new GitHub repository** (public is fine).
2. **Upload these files** (or push via git).
3. Go to **Settings → Secrets and variables → Actions → New repository secret** and add:
   - `NOSTR_NSEC` – your bot’s Nostr private key (starts with `nsec...`).
   - `NOSTR_RELAYS` – comma‑separated relay URLs, e.g. `wss://relay.damus.io,wss://nos.lol,wss://relay.primal.net`
   - `RSS_URL` – e.g. `https://nitter.net/BillSimmons/rss`
4. (Optional) In `.github/workflows/nostr-crosspost.yml`, adjust the cron schedule.
5. Go to **Actions** tab → enable workflows for the repo if prompted. You can also **Run workflow** manually.

## Notes
- If your chosen Nitter instance goes down, replace `RSS_URL` with a working instance (same path pattern: `/USERNAME/rss`). 
- The bot posts text + a link back to X. Media/quotes may not be included by RSS.
- To change the “prefix” text, edit `bot.py` where the body is composed.

## Local run (optional)
```
pip install -r requirements.txt
export NOSTR_NSEC=...       # or use a .env if you prefer local only
export NOSTR_RELAYS=wss://relay.damus.io,wss://nos.lol
export RSS_URL=https://nitter.net/BillSimmons/rss
python bot.py
```