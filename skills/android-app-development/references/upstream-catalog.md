# Upstream Android skills: focused adoption, no blind vendoring

Review these before implementing a specialist technique. Links are original sources; descriptions summarize publisher claims, not independent proof in the target app.

| Resource | Use when | How to adopt |
|---|---|---|
| [android/skills](https://github.com/android/skills) (official Android first-party catalog) | Platform permissions, security, intents, R8, accessibility, widgets, profiling and other current Android workflows | Prefer the smallest task-matched skill and official developer.android.com API reference; pin accepted revision/version. The official Android CLI supports installing its own skills; availability depends on agent runtime. |
| [skydoves/android-testing-skills](https://github.com/skydoves/android-testing-skills) | Compose semantics/gestures, AndroidX instrumentation, UiAutomator, ADB, coroutine/JVM tests | Pick a few relevant modules; this large catalog itself warns against blanket installation. Read and review any install script before execution. |
| [skydoves/compose-performance-skills](https://github.com/skydoves/compose-performance-skills) | Profile-guided Compose stability, recomposition, lazy layout, side effects, Baseline Profiles, R8 | Establish actual metrics first; adapt only evidence-backed practice and compare after. |
| [Agent Skills specification](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx) | Authoring/packaging/validation | Required SKILL.md frontmatter, concise main instructions and progressive references; run skills-ref validate if available. |

All three published skill collections were observed as Apache-2.0 on their respective repositories in the initial audit; recheck current license and revision before copying text/code. This repository **links and synthesizes concepts**, contains no copied third-party skill bodies or executable external scripts, and makes no license claim about the owner's new original work. Before distribution beyond this private repository, owner should select desired publication/license terms and inspect attribution obligations.

**Selection contract:** verify the candidate addresses a concrete current failure; inspect its docs, original code/API assumptions and scripts; pin a commit; compare against repository architecture and Android target/SDK; run narrow before/after acceptance; document if it altered decisions. Installing everything is not a quality strategy.
