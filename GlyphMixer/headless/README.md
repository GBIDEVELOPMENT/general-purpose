# Glyph Mixer headless automation

This directory is the **actual automation interface**. The browser editor and Python headless compiler are independent tools; the browser UI does not yet expose GSUB feature authoring.

## Human/agent workflow

An agent takes a request such as:

> Start with font A, substitute its lowercase a-z with B, install the uppercase A-Z of C as alternates, alternate adjacent repeats contextually, and name the result Z.

It produces a versioned JSON recipe, runs the CLI, examines warnings and GSUB/mapping results, and returns a TTF file and machine-readable report. The recipe is the source of truth, not the wording of the prompt. Never assume that the requested characters exist in all sources; the report lists missing glyphs and strict mode can fail instead.

Example:

```json
{
  "version": 1,
  "name": "Z",
  "base": "A",
  "sources": {
    "A": {"path": "GlyphMixer/test-fonts/Unkempt.zip"},
    "B": {"path": "GlyphMixer/test-fonts/besty.zip"},
    "C": {"path": "GlyphMixer/test-fonts/ahoy-font.zip"}
  },
  "operations": [
    {"action": "replace", "source": "B", "target": "lowercase"},
    {"action": "alternate", "source": "C", "target": "uppercase",
     "features": ["aalt", "salt", "ss01"], "context": "adjacent-repeat"}
  ],
  "output": "GlyphMixer/build/Z.ttf"
}
```

### Run locally

```sh
python -m pip install -r GlyphMixer/headless/requirements.txt
python GlyphMixer/headless/cli.py inventory --output GlyphMixer/build/fixture-inventory.json
python GlyphMixer/headless/cli.py build --recipe GlyphMixer/recipes/example-uppercase-alternates.json
```

### Run through GitHub Actions

Go to **Actions → Glyph Mixer headless build → Run workflow** and enter the repository-relative path to a committed recipe. The workflow checks the JSON, builds the font in GitHub Actions, and uploads a downloadable artifact containing the TTF and report. It runs separately from GitHub Pages, requiring no Android or desktop machine. An agent with repo access can create a recipe/PR and let the CI build it. Automation uses no external font service.

The agent contract is also expressed as a machine-readable [recipe JSON Schema](recipe.schema.json). The CLI performs its own semantic validations, including source existence and glyph availability.

### JSON schema (version 1)

- `base`: a key in `sources`.
- `sources`: up to 80 keys such as A, B, C; each has a repo-relative `path` to TTF/OTF/WOFF/WOFF2/TTC/OTC/ZIP; ZIPs choose a deterministic first font unless `member` gives the exact archived filename. Collections support `face` (zero-based). Static variable-font axis coordinates may be supplied under `axes`. Always inspect archive inventory before choosing members for production.
- `operations`: ordered list. `replace` substitutes outlines/advance metrics for the selected target characters. `reassign` maps one explicit donor Unicode `glyph` to a `destination` (both literal character, integer or U+XXXX). `alternate` preserves mapped glyphs while adding distinct unencoded alternatives from its source, with optional GSUB features. `ligature` uses a donor glyph specified by `glyph` for a `sequence` of two to eight characters; declare `feature` liga or dlig.
- `target`: one of `lowercase`, `uppercase`, `digits`, `basic-latin`, `latin-1`, `all`, `chars:<text>`, U+XXXX, or a list of Unicode characters/codes.
- `features`: alternate features `aalt` (selection API), `salt` (stylistic alternates), `rand` (registered randomized-alternate candidates selected by a supporting application), `ss01` / `ss02` (select specific alternates), `calt` (contextual substitution). `context: "adjacent-repeat"` enables deterministic repeat alternation; `context: {"preceded_by":"o"}` or `{"followed_by":"e"}` targets explicit adjacent character contexts, and both may be combined.
- `strict: true` fails a step when its requested source glyph is absent. By default the compiler reports and skips those positions.
- `output`: repository-relative filename ending in .ttf. The output is a static OpenType font with TrueType outlines. A JSON report is written beside it, named *.report.json.

### Truthfulness and limitations

- These are real **GSUB** rules baked into the compiled font. Alternate source outlines are separate glyphs without assigned Unicode characters. Normal text remains normal Unicode.
- Aalt/salt/rand/ss01/ss02 require application opt-in or shaping-system support. Rand stores candidates but selection behavior is controlled by the application and is inconsistently supported. Calt is usually on by default but individual apps can disable it.
- This first compiler implements **adjacent-repeat** and **immediate previous/next character** contextual rules. It does not implement guaranteed random distribution in the font itself, document-wide memory of previously seen letters, long-range context predicates, complete automatic spacing/kerning reconciliation, GPOS, Arabic/Indic shaping, inherited GSUB/GPOS from the base, or rich color/bitmap/variable output tables. Do not claim these features.
- Input outline types are normalized to TrueType quadratic contours through fontTools. Base font units-per-em determine output em size, with advances and sidebearings scaled proportionally.
- Source fonts are local repo fixtures and may carry restricted licences. Keep output artifacts and redistribution compliant with those licences.
- The CLI validates output by reopening it and comparing Unicode maps and GSUB presence. CI independently shapes characters with HarfBuzz for stylistic-set and adjacent-repeat rules; physical Android and multiple-application acceptance remain separate tasks. All 22 ZIP archives are also exercised as donor sources through an actual export/reimport smoke test.

### Agent validation discipline

Review the JSON recipe diff and font selection before execution. Prefer strict mode when the user expects every targeted glyph; a forgiving recipe should disclose all misses. Inspect the resulting *.report.json, the generated TTF table listing, and sample shaping for contexts. Never reinterpret a failed operation as a successful font merge.
