#!/usr/bin/env python3
"""Credential-free, best-effort recovery of public X tweets.

Never claim completeness. No account, cookies, API key, or paid service.
"""
import argparse
import csv
import html
from html.parser import HTMLParser
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

MIRRORS = ["https://nitter.net", "https://xcancel.com",
           "https://nitter.poast.org", "https://nitter.privacyredirect.com",
           "https://nitter.cf"]
ID = re.compile(r"/status(?:es)?/(\d{10,22})(?:[/?#]|$)", re.I)
HANDLE = re.compile(r"^[A-Za-z0-9_]{1,15}$")
COLUMNS = ["id", "author", "text", "date", "url", "is_reply", "is_repost", "source"]


def compact(text):
    return re.sub(r"\s+", " ", text).strip()


class NitterTimeline(HTMLParser):
    """Parse real Nitter timeline-item containers, never generic page text."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.item = None
        self.item_depth = None
        self.body_depth = None
        self.header_depth = None
        self.more_depth = None
        self.next_url = None
        self.posts = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set(a.get("class", "").split())
        if tag == "div":
            self.depth += 1
            if "timeline-item" in classes and self.item is None:
                self.item = {"id": None, "author": None, "text_parts": [],
                             "date": "", "is_reply": False, "is_repost": False}
                self.item_depth = self.depth
            if self.item is not None:
                if "tweet-content" in classes and self.body_depth is None:
                    self.body_depth = self.depth
                if "tweet-header" in classes:
                    self.header_depth = self.depth
                if "replying-to" in classes:
                    self.item["is_reply"] = True
                if "retweet-header" in classes:
                    self.item["is_repost"] = True
            if "show-more" in classes:
                self.more_depth = self.depth
        if tag == "a":
            href = a.get("href", "")
            if self.item is not None:
                match = ID.search(href)
                if match and self.item["id"] is None:
                    self.item["id"] = match.group(1)
                if "tweet-date" in classes:
                    self.item["date"] = a.get("title", "")
                if "username" in classes and self.header_depth is not None:
                    username = href.strip("/").split("/")[0].lstrip("@")
                    if HANDLE.fullmatch(username):
                        self.item["author"] = username
            elif self.more_depth is not None and self.next_url is None:
                self.next_url = href
        if tag == "time" and self.item is not None:
            self.item["date"] = a.get("datetime", self.item["date"])
        if tag == "br" and self.body_depth is not None:
            self.item["text_parts"].append(" ")

    def handle_data(self, data):
        if self.item is not None and self.body_depth is not None:
            self.item["text_parts"].append(data)

    def handle_endtag(self, tag):
        if tag != "div":
            return
        if self.body_depth == self.depth:
            self.body_depth = None
        if self.header_depth == self.depth:
            self.header_depth = None
        if self.item_depth == self.depth:
            item = self.item
            if item and item["id"]:
                item["text"] = compact("".join(item.pop("text_parts")))
                if item["text"]:
                    self.posts.append(item)
            self.item = None
            self.item_depth = None
        if self.more_depth == self.depth:
            self.more_depth = None
        self.depth = max(0, self.depth - 1)


def parse_timeline(markup):
    parser = NitterTimeline()
    parser.feed(markup)
    parser.close()
    return parser.posts, parser.next_url


def get(url, timeout):
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; public-post-research/1.0)",
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.5"})
    with urlopen(req, timeout=timeout) as response:
        return response.read(3_000_000).decode("utf-8", "replace")


def error(errors, provider, exception, url=""):
    errors.append({"provider": provider, "url": url,
                   "error": type(exception).__name__ + ": " + str(exception)[:180]})


def mirror_crawl(mirror, user, max_pages, delay, timeout, errors):
    hostname = urlparse(mirror).netloc
    found = []
    visited = set()
    for suffix in ("", "/with_replies"):
        url = mirror.rstrip("/") + "/" + user + suffix
        for unused in range(max_pages):
            if url in visited:
                break
            visited.add(url)
            try:
                items, nxt = parse_timeline(get(url, timeout))
                if not items:
                    errors.append({"provider": hostname, "url": url,
                                   "error": "No timeline items parsed"})
                    break
                for item in items:
                    author = item.get("author") or user
                    if author.lower() != user.lower():
                        continue  # Do not attribute a repost to this writer.
                    item["author"] = author
                    item["url"] = "https://x.com/" + author + "/status/" + item["id"]
                    item["source"] = hostname
                    found.append(item)
                if not nxt:
                    break
                candidate = urljoin(mirror + "/", nxt)
                parsed = urlparse(candidate)
                if (parsed.netloc != hostname or
                        not parsed.path.lower().startswith("/" + user.lower())):
                    errors.append({"provider": hostname,
                                   "error": "Unsafe/out-of-profile pagination rejected"})
                    break
                url = candidate
                time.sleep(delay)
            except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
                error(errors, hostname, exc, url)
                break
        time.sleep(delay)
    return found


def discover_ids(user, timeout, errors, archive_limit):
    ids = set()
    for domain in ("twitter.com", "x.com"):
        url = "https://web.archive.org/cdx/search/cdx?" + urlencode({
            "url": domain + "/" + user + "/status/*",
            "output": "json", "fl": "original", "filter": "statuscode:200",
            "collapse": "urlkey", "limit": str(archive_limit)})
        try:
            rows = json.loads(get(url, timeout))
            for row in rows[1:]:
                value = row[0] if isinstance(row, list) else str(row)
                match = ID.search(value)
                if match:
                    ids.add(match.group(1))
        except (HTTPError, URLError, TimeoutError, ValueError, OSError, IndexError) as exc:
            error(errors, "wayback-cdx", exc, url)
    for engine in ("https://www.google.com/search?",
                   "https://www.bing.com/search?"):
        url = engine + urlencode({"q": "site:x.com/" + user + "/status/"})
        try:
            text = html.unescape(unquote(get(url, timeout)))
            pattern = r"(?:x\.com|twitter\.com)/" + re.escape(user) + r"/status/(\d{10,22})"
            ids.update(re.findall(pattern, text, re.I))
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            error(errors, urlparse(engine).netloc, exc, url)
    return ids


def fetch_fx(user, tweet_id, timeout, errors):
    url = "https://api.fxtwitter.com/" + user + "/status/" + tweet_id
    try:
        data = json.loads(get(url, timeout)).get("tweet") or {}
        author = (data.get("author") or {}).get("screen_name") or ""
        if author.lower() != user.lower():
            errors.append({"provider": "fxtwitter", "url": url,
                           "error": "Post absent or author did not match"})
            return None
        text = compact(data.get("text") or "")
        if not text:
            return None
        return {"id": str(data.get("id") or tweet_id), "author": author,
                "text": text, "date": data.get("created_at") or "",
                "url": "https://x.com/" + user + "/status/" + tweet_id,
                "is_reply": bool(data.get("replying_to")),
                "is_repost": bool(data.get("is_retweet")),
                "source": "fxtwitter"}
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
        error(errors, "fxtwitter", exc, url)
        return None


def run(args):
    errors = []
    collected = {}
    counts = {}
    for mirror in args.mirrors:
        items = mirror_crawl(mirror, args.user, args.max_pages,
                             args.delay, args.timeout, errors)
        counts[urlparse(mirror).netloc] = len(items)
        for item in items:
            collected.setdefault(item["id"], item)
    ids = discover_ids(args.user, args.timeout, errors, args.archive_limit)
    counts["candidate_ids"] = len(ids)
    for tid in sorted(ids):
        if tid in collected:
            continue
        item = fetch_fx(args.user, tid, args.timeout, errors)
        if item:
            collected[item["id"]] = item
        time.sleep(args.delay)

    items = sorted(collected.values(), key=lambda i: int(i["id"]))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "tweets.jsonl").open("w", encoding="utf-8") as file:
        for item in items:
            file.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    with (out / "tweets.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)
    report = {
        "handle": args.user, "utc": datetime.now(timezone.utc).isoformat(),
        "unique": len(items),
        "originals": sum(not i["is_reply"] and not i["is_repost"] for i in items),
        "replies": sum(i["is_reply"] for i in items),
        "reposts": sum(i["is_repost"] for i in items),
        "by_source": dict(Counter(i["source"] for i in items)),
        "attempt_counts": counts, "errors": errors,
        "complete": False,
        "warning": "Incomplete anonymous recovery; zero results never proves no tweets."
    }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n",
                                    encoding="utf-8")
    summary = ["# Anonymous tweet recovery: @" + args.user, "",
               "Unique verified posts: **" + str(len(items)) + "**",
               "Originals: " + str(report["originals"]) +
               "; replies: " + str(report["replies"]), "",
               "**Incomplete sample; zero means retrieval failure, not no posts.**",
               "", "## Provider counts", ""]
    summary += ["- " + key + ": " + str(value) for key, value in counts.items()]
    summary += ["", "## Source errors", ""]
    summary += ["- " + e["provider"] + ": " + e["error"] for e in errors[:60]]
    (out / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps({"verified_posts": len(items),
                      "source_counts": counts, "errors": len(errors)}))
    return len(items)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="ianmakesjokes")
    parser.add_argument("--out", default="tweet-recovery")
    parser.add_argument("--max-pages", type=int, default=5)
    parser.add_argument("--delay", type=float, default=0.4)
    parser.add_argument("--timeout", type=float, default=12)
    parser.add_argument("--archive-limit", type=int, default=100)
    parser.add_argument("--mirrors", nargs="*", default=MIRRORS)
    args = parser.parse_args()
    if (not HANDLE.fullmatch(args.user) or not 1 <= args.max_pages <= 30 or
            not 0 <= args.delay <= 10 or not 2 <= args.timeout <= 90 or
            not 1 <= args.archive_limit <= 500):
        parser.error("invalid arguments")
    if any(urlparse(m).scheme != "https" for m in args.mirrors):
        parser.error("mirrors must use HTTPS")
    if run(args) == 0:
        print("No tweets verified; see report.json for access failures.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
