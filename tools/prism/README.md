# Expository: Repository Explorer

A mobile-first, read-only GitHub repository browser and visual artifact gallery, with restrained rainbow styling and a dark-first interface.

## Start

Open `index.html` in a local HTTP server or publish this directory as a standalone GitHub Pages deployment. It uses plain HTML, CSS and JavaScript; no build or third-party dependencies.

For example, from `tools/prism/`, run `python3 -m http.server 8000` and open `http://localhost:8000`.

Enter `owner/repo` to browse any public repository. The optional *fine-grained, Contents: Read-only* GitHub PAT permits access to private repositories; select only the repositories you intend to expose to the browser. Press **Connect / refresh repos** to load your accessible repository list.

**Important:** Only enter a private-repository token on an instance whose source and deployment you trust. A token is retained in memory until the tab is closed or reloaded, and is never written to localStorage, URL fragments, logs, or repository files. The visual theme preference alone is stored locally. All GitHub content comes from GitHub API requests made directly from the browser. Treat any browser extension with page access as capable of inspecting browser memory; GitHub tokens are bearer credentials. Revoke compromised tokens immediately.

## Deploy safely

This repository is private and contains unrelated sensitive utilities. **Do not enable GitHub Pages for the entire general-purpose repository, copy its contents into a public Pages branch, or publish any private file manifests**.

Recommended deployment: copy only the reviewed `tools/prism/index.html` to a separate public Pages repository as `index.html`, or host the single file on another trusted static origin. The *app's code* may be public. Private repositories are fetched at runtime with a read-only token; they must not be baked into the static deployment. GitHub Pages hosting does not make the private API responses public by itself, but scripts running on that origin could read a supplied token. A dedicated origin avoids co-hosting unrelated scripts.

## What works

- Responsive folder navigation, gallery/list views and name filtering in the current folder.
- Authenticated repository discovery (first 500 repositories ordered by last update) or manually entered public/private repo.
- Default branch lookup with optional branch override; breadcrumbs and hash-based directory links.
- Image and SVG previews, including gallery thumbnails; text and simple Markdown; PDF, browser-compatible video and audio.
- Concurrency-limited thumbnail fetching (three at a time) and blob URLs rather than permanent artifact caches.
- Keyboard Escape to dismiss overlays; visible focus styles; reduced-motion preference; touch-sized controls.
- No write API calls, tracking, cookies, analytics or credential persistence.

## Boundaries and next work

This is a usable **first-pass prototype**, not a fully audited release. Its Markdown reader intentionally displays plain/safe content without rendering raw HTML or remote images. File rendering depends on browser codec support. GitHub's Contents API directory listing can be truncated at 1,000 files; large trees need a separate paginated/tree-backed explorer. Thumbnail generation is live and can encounter API rate limits in image-heavy folders. Very large previews are limited to 20 MB (gallery thumbnails to 8 MB). Binary/unknown file types link to GitHub. Private files never go through a third-party proxy.

Priority improvements: accessible expandable recursive folder tree; lazy thumbnail loading based on visibility; search across the whole repository using a tree index; multi-select/contact sheets; side-by-side SVG comparison; tests at actual Android viewport sizes; optimistic large-repo indexing and explicit rate-limit feedback.

## Project-specific opportunities

- **Glimpse:** storyboard state coverage badges, transition comparison and view-by-screen-family.
- **ROYGBIV:** image-to-recipe metadata inspector, wallpaper contact sheets and visual variant comparison.
- **UR-Recomp / Ring Road:** screenshot atlas overlays, render golden comparisons and image-difference inspection.
- **General-purpose:** read-only audit ledger browser with date and run-type facets.

All project-specific features should be optional adapters rather than assumptions built into the generic browser.
