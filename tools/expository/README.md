# Expository: Repository Explorer

> Explore the story of your repository.

A dark-first, rainbow-accented, mobile-first visual browser for **any GitHub repository**. It is read-only, uses no backend, and ships as one standalone HTML file.

## Quick start

Run `python3 -m http.server 8000` from `tools/expository/` and open `http://localhost:8000`. Or copy only `index.html` to a separate trusted static host.

For a **public** repo, enter `owner/repository` and choose **Open repository**. No login is necessary.

For a **private** repo, create a GitHub fine-grained personal access token restricted to the selected repository or repositories with **Contents: Read-only**. Enter it in Expository and select **Connect / refresh repos**. The repository selector will show accessible repos. Token state lives in tab memory only. **Forget credentials & clear session** discards it and clears the app's private browsing state without reloading.

Only enter a token on a deployment whose code and origin you trust. A GitHub token is a bearer credential, and malicious scripts or browser extensions on that origin could extract it. Expository never deliberately sends a token to another host: GitHub API requests include the token, and blob previews are rendered locally. The only persistent preference is the light/dark theme.

## Using the browser

- **Folders:** open folders with breadcrumbs or the left navigation. Expand/collapse the indexed folder tree independently from navigation. On narrow screens use the menu button.
- **Views:** toggle compact list or gallery. Switch the scope selector between **This folder**, **Search entire repo**, and **Images in subfolders**. The search field filters names/paths within that scope.
- **Galleries:** images and SVGs preview on demand; requests are only started near the viewport, at most three simultaneously. Large sets load in pages of 80; Show more adds files without redownloading displayed thumbnails.
- **Inspect:** select a file for image/SVG, safe plain Markdown, source, PDF, browser-compatible audio or video preview. Previous/next controls and arrow keys navigate other files within the current results.
- **Compare:** open a raster or SVG image and select **Pin A**. Navigate to another image and select **Compare A/B** for an annotated side-by-side preview (stacked on narrow screens). The pinned image's Blob remains in this tab's memory until unpinned, the repository changes, or the session is cleared. No files or comparisons are uploaded.
- **Share:** use the arrow button for a folder URL or **Copy ↗** inside file previews to generate a deep link. URLs include no credential. A recipient needs their own GitHub access to private content.
- **Disconnect:** forget token and reset private browser state using the dedicated button.

The interface never writes to repositories, executes fetched JavaScript, loads external preview scripts, or sends analytics.

## Safe deployment

**IMPORTANT:** `gamesbyian/general-purpose` is itself a private repository containing unrelated tools and sensitive workflows. Never publish the whole repository, its contents, a recursive manifest, or its artifacts to GitHub Pages just to deploy Expository.

To host Expository with GitHub Pages, create a dedicated public repository for its reviewed *static application code only*, put `index.html` at the root, and enable Pages from its own main branch. The static source may be public; private repository files are not included in that deployment. Alternatively use another trusted static hosting origin.

Expository itself does not need a backend or deployment secrets. Do not put tokens in build-time variables, the HTML, Pages actions, browser localStorage, remote log collectors, or query strings.

## Testing

```sh
node --test tools/expository/expository.test.cjs
```

Uses only the Node.js test runner, with no external dependencies. A path-filtered PR workflow runs these smoke checks when Expository files change. Checks cover application JavaScript syntax, sidebar ancestry, collapsed/expanded folder rendering, cross-folder search, recursive galleries, deep-link structure, session clearing, visual comparison boundaries, and basic security invariants.

These are **not** substitutes for an optical/browser audit. Before a release, verify actual Android portrait Chrome (especially Pixel-width navigation, keyboard/screen-reader focus, and very large SVG galleries) and desktop Safari/Firefox.

## Current limitations

- GitHub API rate limits apply, particularly unauthenticated thumbnails. GitHub Contents API directory listings can be capped at 1,000 entries; Git Trees API can truncate very large repository indices (which makes global search incomplete). The UI labels this state. The index-error fallback limits results to the current folder.
- Markdown is intentionally rendered as plain, restricted content without arbitrary HTML execution, external image loads, full GFM formatting, or remote links. Syntax highlighting, full-text code search, issue/PR browsing, and editable file operations are out of scope.
- Binary previews above 20 MB, thumbnails above 8 MB and unsupported media/codecs are delegated to GitHub. Preview files and authentication remain in tab memory; no offline cache/PWA shell yet.
- Repo-list discovery currently reads at most 500 of the most recently updated accessible repositories. Manual repo entry works independently.
- Deep links require the recipient to have access to that repository. Private URLs are not public file shares.
- Browser-level performance and accessibility acceptance are not yet recorded. The app is a prototype, not a production-certified viewer.

## Ideas for optional repository adapters

Keep the generic browser clean; extensions should activate only when matching supported artifact structures.

- **Glimpse:** the generic visual A/B viewer already supports SVG storyboards; a future adapter could add contact sheets, annotated interaction-state coverage, and adjacent-screen transitions.
- **ROYGBIV/wallgen:** use generic visual A/B for artwork; add PNG recipe metadata and per-material comparison overlays in a future adapter.
- **UR-Recomp / Ring Road:** use generic visual A/B for screenshots; future features include pixel-difference inspection, registration and provenance links.
- **General-purpose:** date- and status-aware report browsing without interacting with sensitive mail/audit services.

## Project structure

```
tools/expository/
  index.html              # standalone application, no external dependencies
  expository.test.cjs     # Node built-in test runner
  README.md               # docs, security and release limitations
.github/workflows/expository-smoke.yml
```
