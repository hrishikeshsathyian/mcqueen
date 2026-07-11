# mcqueen

Live internship alert bot for NUS Computing students. It scrapes internship
listings from company career pages, filters for new Singapore-based
internships, and posts alerts to a Telegram chat.

## How it works

1. **Scrape** — [pipeline/sources/registry.py](pipeline/sources/registry.py) defines the sources to pull from, currently:
   - TikTok's own careers page
   - Companies hosted on SmartRecruiters ([pipeline/data/smartrecruiters.csv](pipeline/data/smartrecruiters.csv))
   - Companies hosted on Lever ([pipeline/data/lever.csv](pipeline/data/lever.csv))

   Each source is fetched concurrently via [jobhive](https://pypi.org/project/jobhive-py/) scrapers (see [pipeline/sources/base.py](pipeline/sources/base.py)).
2. **Filter** — jobs are kept only if they're internships located in Singapore, and haven't been seen before [pipeline/scripts/scrape.py](pipeline/scripts/scrape.py).
3. **Persist** — new jobs are recorded in a Supabase `seen_jobs` table so they aren't alerted twice ([db/jobs.py](db/jobs.py), [db/models.py](db/models.py)).
4. **Notify** — each new job is sent as a formatted message to a Telegram chat via [bot/bot.py](bot/bot.py).

The whole pipeline runs end-to-end from [main.py](main.py).

## Adding a new scraper source

Add an entry to `SOURCES` in [pipeline/sources/registry.py](pipeline/sources/registry.py), pointing at a `jobhive` scraper class and (if multi-company) a CSV of slugs in [pipeline/data/](pipeline/data/) with `name,slug,url` columns.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and requires Python >=3.13.

```bash
uv sync
```

### Environment variables

Create a `.env` file in the project root with:

```
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SECRET_KEY=
SUPABASE_JWKS_URL=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

- `SUPABASE_URL` / `SUPABASE_SECRET_KEY` — used to connect to the Supabase project storing seen jobs.
- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` — the Telegram bot and chat that alerts are posted to.

## Usage

```bash
uv run main.py
```

This scrapes all configured sources, filters for new Singapore internships, records them in the database, and sends a Telegram alert for each one. Intended to be run on a schedule (e.g. cron) to catch new postings as they go live.
