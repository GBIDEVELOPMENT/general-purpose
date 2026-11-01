#!/usr/bin/env python3
"""Read-only GitHub PR/issue metadata inventory for Android engineering research.

Never stores issue bodies, credentials, workflow logs or review comments.
Github pagination is not an atomic snapshot: start/end main heads are recorded.
"""
import argparse
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.request

REPOS = ("gamesbyian/Chunks", "gamesbyian/Glimpse", "gamesbyian/Expository")
API = "https://api.github.com"


def next_url(link_header):
    for part in link_header.split(","):
        match = re.match(r'\s*<([^>]+)>;\s*rel="([^"]+)"', part)
        if match and match.group(2) == "next":
            return match.group(1)
    return None


def github_get(url, token=None, opener=urllib.request.urlopen):
    if not url.startswith(API + "/repos/"):
        raise ValueError("Unexpected API URL")
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "android-skill-history-snapshot/0.1",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    with opener(request, timeout=30) as response:
        return json.load(response), next_url(response.headers.get("Link", ""))


def collection(url, getter):
    seen, rows, pages = set(), [], 0
    while url:
        data, url = getter(url)
        if not isinstance(data, list):
            raise ValueError("Expected a GitHub list response")
        pages += 1
        if pages > 100:
            raise ValueError("Pagination did not terminate")
        for item in data:
            number = item["number"]
            if number in seen:
                raise ValueError(f"Duplicate item across pages: {number}")
            seen.add(number)
            rows.append(item)
    return rows, pages


def branch_sha(repo, getter):
    data, _ = getter(f"{API}/repos/{repo}/branches/main")
    return data["commit"]["sha"]


def record(row, is_pr):
    fields = {"number": row["number"], "title": row.get("title", ""),
              "url": row.get("html_url"), "state": row.get("state"),
              "created_at": row.get("created_at"), "updated_at": row.get("updated_at"),
              "closed_at": row.get("closed_at"),
              "labels": sorted(x.get("name", "") for x in row.get("labels", []))}
    if is_pr:
        fields.update(merged_at=row.get("merged_at"), draft=row.get("draft"),
                      base_sha=(row.get("base") or {}).get("sha"),
                      head_sha=(row.get("head") or {}).get("sha"))
    return fields


def snapshot(repos, getter):
    result = {"schema": "android-skill-github-metadata-v1",
              "scope": "PR and distinct issue metadata; no diffs/reviews/CI",
              "repositories": {},
              "limitations": ["GitHub pagination is not atomic",
                              "A listed PR is not a manually reviewed diff or CI outcome"]}
    for repo in repos:
        before = branch_sha(repo, getter)
        prs, pr_pages = collection(f"{API}/repos/{repo}/pulls?state=all&per_page=100&page=1", getter)
        mixed, issue_pages = collection(f"{API}/repos/{repo}/issues?state=all&per_page=100&page=1", getter)
        issues = [item for item in mixed if "pull_request" not in item]
        after = branch_sha(repo, getter)
        result["repositories"][repo] = {
            "main_before": before, "main_after": after,
            "main_moved_during_scan": before != after,
            "pr_pages": pr_pages, "issue_pages": issue_pages,
            "pr_count": len(prs), "issue_count": len(issues),
            "pull_requests": [record(item, True) for item in sorted(prs, key=lambda x: x["number"])],
            "issues": [record(item, False) for item in sorted(issues, key=lambda x: x["number"])],
        }
    return result


def atomic_write(path, result):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                     dir=path.parent, prefix=".history-", delete=False) as f:
        temp = Path(f.name)
        try:
            json.dump(result, f, indent=2, ensure_ascii=False, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        except Exception:
            temp.unlink(missing_ok=True)
            raise
    os.replace(temp, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Path for the local JSON snapshot")
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    result = snapshot(REPOS, lambda url: github_get(url, token))
    atomic_write(args.output, result)
    for name, data in result["repositories"].items():
        print(f"{name}: {data['pr_count']} PRs, {data['issue_count']} issues, "
              f"main moved={data['main_moved_during_scan']}")
    print("Metadata only: not a complete diff, CI or failure-root-cause audit")


if __name__ == "__main__":
    main()
