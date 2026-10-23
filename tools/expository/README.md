# Expository: Repository Explorer

> Explore the story of your repository.

A dark-first, rainbow-accented, mobile-first visual browser for **any GitHub repository**. It is read-only, uses no backend, and ships as one standalone HTML file.

## Quick start

Run `python3 -m http.server 8000` from `tools/expository/` and open `http://localhost:8000`. Or copy only `index.html` to a separate trusted static host.

For a **public** repo, enter `owner/repository` and choose **Open repository**. No login is necessary.

For a **private** repo, create a GitHub fine-grained personal access token restricted to the selected repository or repositories with **Contents: Read-only**. Enter it in Expository and select **Connect / refresh repos**. The repository selector will show accessible repos. Token state lives in tab memory only. **Forget credentials & clear session** discards it and clears the app's private browsing state without reloading.

Only enter a token on a deployment whose code and origin you trust. A GitHub token is a bearer credential, and malicious scripts or browser extensions on that origin could extract it. Expository never deliberately sends a token to another host: GitHub API requests include the token, and blob previews are rendered locally. The persistent preferences are light/dark theme and explicitly starred **public** repository names; private repository identifiers and content are not saved.

## Using the browser

- **Folders:** open folders with breadcrumbs or the left navigation. Expand/collapse the indexed folder tree independently from navigation. On narrow screens use the menu button.
- **Views and filters:** toggle list/gallery, sort by name/size/extension, and filter by image/code/document/data/other. Choose **This folder**, **Search entire repo** or **Images in subfolders**; the Find field filters indexed filenames and paths. A density slider adjusts the gallery tile width.
- **Bounded full-text scan:** enter at least two characters into **Find by name**, then explicitly choose **Search contents**. This reads at most the first 120 eligible indexed text files (128 KiB each, three concurrent GitHub requests), displays up to two matching lines per file and 80 results total, and offers **Cancel scan**. This is opt-in, incomplete by design for huge repos, and not a server-side universal code search.
- **Public bookmarks:** star public repositories for one-tap switching. Only *public* repository names are retained in browser storage, never private repository names, paths, credentials or scan results.
- **Galleries:** images and SVGs preview on demand; requests are only started near the viewport, at most three simultaneously. Large sets load in pages of 80; Show more adds files without redownloading displayed thumbnails.
- **Inspect:** select a file for image/SVG, safe plain Markdown, source, PDF, browser-compatible audio or video preview. Text/source files have inert DOM-based syntax colors and line numbers, plus **Copy text** and **Download** for supported previews. Previous/next controls and arrow keys navigate other files within current results.
- **Compare:** open a raster or SVG image and select **Pin A**. Navigate to another image and select **Compare A/B**. The default **Reveal slider** overlays two aligned images with a large, finger-friendly reveal control (also operable by keyboard); **Side by side** displays two labeled panels, stacked on phones. When image aspect ratios differ, both are fitted to the same frame with letterboxing, so this is a visual comparison rather than a pixel-registered diff. The pinned image stays only in tab memory until unpinned, the repository changes, or the session is cleared. No files or comparisons are uploaded.
- **Share:** use the arrow button for a folder URL or **Copy ↗** inside file previews to generate a deep link. URLs include no credential. A recipient needs their own GitHub access to private content.
- **Disconnect:** forget token and reset private browser state using the dedicated button.

The interface never writes to repositories, executes fetched JavaScript, loads external preview scripts, or sends analytics.

## Safe deployment

**IMPORTANT:** `gamesbyian/general-purpose` is itself a private repository containing unrelated tools and sensitive workflows. Never publish the whole repository, its contents, a recursive manifest, or its artifacts to GitHub Pages just to deploy Expository.

To host Expository with GitHub Pages, create a dedicated public repository for its reviewed *static application code only*, put `index.html` at the root, and enable Pages from its own main branch. The static source may be public; private repository files are not included in that deployment. Alternatively use another trusted static hosting origin.

### Guarded one-command publisher (GitHub CLI)

From the private source checkout, after `gh auth login`:

```sh
bash tools/expository/publish-pages.sh gamesbyian/expository
```

The script previews the **public** target and exact exported files and requires typing `PUBLISH` interactively. It copies only the current application `index.html`, a `.nojekyll` marker and a non-sensitive publisher marker into a clean, separate public repository, then enables Pages. It never publishes the surrounding `general-purpose` tree. If the target already exists, it updates only `index.html` and refuses a repository without its explicit management marker. Review the source file before first publishing, and verify the exact GitHub target printed by the command. The script is deliberately non-automatable without a human confirmation.

An existing target with restricted permissions or unconfigured Pages may require manual Settings → Pages adjustments. After successful deployment, the expected URL is `https://gamesbyian.github.io/expository/`, subject to GitHub's actual Pages configuration. **No Pages deployment has been performed by this PR.**

Expository itself does not need a backend or deployment secrets. Do not put tokens in build-time variables, the HTML, Pages actions, browser localStorage, remote log collectors, or query strings.

## Testing

```sh
node --test tools/expository/expository.test.cjs
```

Uses only the Node.js test runner, with no external dependencies. A path-filtered PR workflow runs these smoke checks when Expository files change. Checks cover application JavaScript syntax, sidebar ancestry, collapsed/expanded folder rendering, cross-folder search, recursive galleries, deep-link structure, session clearing, image reveal controls, modal focus wrapping, visual comparison boundaries, and basic security invariants.

### Real browser smoke and visual evidence

```sh
node tools/expository/browser-smoke.cjs
```

Requires local Chromium or Google Chrome; no npm packages or GitHub credentials. It starts a real browser through the Chrome DevTools Protocol and substitutes deterministic **fictional SVG fixture responses** for GitHub API requests, so the test never accesses private repositories. It checks gallery rendering, responsive widths (360px and 393px), basic modal isolation, image comparisons, reveal slider interaction and above-the-fold controls. Its three screenshot outputs are stored in ignored `tools/expository/browser-evidence/`, and the path-scoped PR workflow keeps them as a private artifact for seven days.

**QA boundary:** passing synthetic fixture browser checks proves these specific interactions, not all runtime file formats, external API/rate-limit behavior, visual correctness with the real projects, or full accessibility. Real Android Chrome and assistive-technology acceptance remain release tasks.

These are **not** substitutes for an optical/browser audit. Before a release, verify actual Android portrait Chrome (especially keyboard/screen-reader focus, real authenticated private browsing, and very large SVG galleries) and desktop Safari/Firefox.

See [FEATURE-ROADMAP.md](FEATURE-ROADMAP.md) for a weighted, competitor-informed implementation programme and release gates.

## Current limitations

- GitHub API rate limits apply, particularly unauthenticated thumbnails. GitHub Contents API directory listings can be capped at 1,000 entries; Git Trees API can truncate very large repository indices (which makes global search incomplete). The UI labels this state. The index-error fallback limits results to the current folder.
- Markdown is intentionally rendered as plain, restricted content without arbitrary HTML execution, external image loads, full GFM formatting, or remote links. Syntax colorization is intentionally basic and not a full language parser; repository content search is a manually triggered bounded scan, not a complete search engine. Issue/PR browsing and editable file operations remain out of scope.
- Binary previews above 20 MB, thumbnails above 8 MB and unsupported media/codecs are delegated to GitHub. Preview files and authentication remain in tab memory; no offline cache/PWA shell yet.
- Repo-list discovery currently reads at most 500 of the most recently updated accessible repositories. Manual repo entry works independently.
- Deep links require the recipient to have access to that repository. Private URLs are not public file shares.
- Synthetic Chromium browser acceptance exists, but real-world authenticated private-repo performance and accessibility acceptance are not yet recorded. The app is a prototype, not a production-certified viewer.

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
