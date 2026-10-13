# Anonymous public tweet recovery

The private chat-scheduler repository's existing purpose as an immutable agent
audit ledger is preserved. This is an independent one-off research workflow,
not an automation audit record or new recurring scheduler.

## How to run

Opening the implementation PR triggers an offline parser test followed by a
bounded public-tweet recovery attempt. After merge, Actions > Recover public
tweets (anonymous) > Run workflow runs it again. It doesn't need an X account,
API key, password, browser cookies, external scraping-service account, or paid
subscription.

For local use (Python standard library only):

    python scripts/collect_public_tweets.py --user ianmakesjokes --out tweet-recovery

Parameters: --max-pages controls per-mirror depth, --timeout limits network
request duration, --delay politely spaces requests, and --mirrors overrides
the list of public mirrors. The collection attempts Nitter-style profile and
with_replies timelines, discovers tweet IDs from the Internet Archive CDX and
search index pages, then verifies individually discovered IDs through the
public FxTwitter single-post endpoint, including author validation.

## Outputs / scientific limitations

The per-run downloadable Actions artifact contains:
- tweets.jsonl: structured verified tweet text, source, URL, flags and date
  when provided.
- tweets.csv: the same, ready for textual analysis.
- report.json: per-provider attempts, errors and counts, even if zero.
- summary.md: readable counts and failure diagnostics.

The workflow has read-only repo permissions, does not store credentials,
does not push data back into the repository, does not schedule recurrence,
and retains its run artifact for 30 days.

**Coverage is never guaranteed.** Anonymous X profile access is routinely
blocked; public Nitter mirrors are sometimes stale or unavailable; archive
indexes contain incomplete URLs. Zero recovered tweets means discovery or
access failed, not that the user had no tweets. Post text found in web search
snippets is deliberately not passed off as confirmed original writing.
Original/response classification from Nitter HTML is best effort, and
quotes, media, edits, and deleted posts may be missing. An official account
export remains necessary for complete corpus analysis.

We evaluated https://github.com/ythx-101/x-tweet-fetcher but its timeline
method still relies on functional Nitter/browser access. This collector
tries several independently hosted instances and explicitly records failure.
