(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.GlyphMixerCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const MAX_CODEPOINT = 0x10ffff;
  function validCodepoint(cp) {
    return Number.isInteger(cp) && cp > 0 && cp <= MAX_CODEPOINT && !(cp >= 0xd800 && cp <= 0xdfff);
  }
  function parseCodepoint(text) {
    const s = String(text || '').trim();
    if (!s) return null;
    let value;
    if (/^U\+[0-9a-f]{1,6}$/i.test(s)) value = parseInt(s.slice(2), 16);
    else if (/^0x[0-9a-f]{1,6}$/i.test(s)) value = parseInt(s.slice(2), 16);
    else if (/^#[0-9]+$/.test(s)) value = Number(s.slice(1));
    else if ([...s].length === 1) value = s.codePointAt(0);
    else return null;
    return validCodepoint(value) ? value : null;
  }
  function displayCodepoint(cp) {
    return 'U+' + cp.toString(16).toUpperCase().padStart(4, '0');
  }
  function isNoncharacter(cp) {
    return (cp >= 0xfdd0 && cp <= 0xfdef) || (cp & 0xfffe) === 0xfffe;
  }
  function glyphMappings(font) {
    const indexMap = font && font.tables && font.tables.cmap && font.tables.cmap.glyphIndexMap || {};
    const output = new Map();
    for (const key of Object.keys(indexMap)) {
      const cp = Number(key), index = Number(indexMap[key]);
      if (validCodepoint(cp) && !isNoncharacter(cp) && Number.isInteger(index) && index > 0) output.set(cp, index);
    }
    // Also handle fonts whose parser exposes mappings on glyph objects.
    const count = font && font.glyphs && font.glyphs.length || 0;
    if (output.size === 0) {
      for (let i = 1; i < count; i++) {
        const glyph = font.glyphs.get(i);
        for (const cp of glyph.unicodes || (validCodepoint(glyph.unicode) ? [glyph.unicode] : [])) {
          if (validCodepoint(cp) && !isNoncharacter(cp)) output.set(cp, i);
        }
      }
    }
    return output;
  }
  function isSafeAssignment(value, fontIds) {
    return value && fontIds.has(value.fontId) && Number.isInteger(value.glyphIndex) && value.glyphIndex >= 0 && value.glyphIndex < 200000;
  }
  function validateProject(project) {
    if (!project || project.version !== 1 || typeof project.name !== 'string' ||
        !Array.isArray(project.fonts) || !Array.isArray(project.assignments) ||
        project.fonts.length < 1 || project.fonts.length > 80 || project.assignments.length > 100000) {
      throw new Error('Unsupported or invalid Glyph Mixer project.');
    }
    const ids = new Set();
    for (const font of project.fonts) {
      if (!font || !/^[a-zA-Z0-9_-]{1,48}$/.test(font.id) ||
          typeof font.file !== 'string' || !/^fonts\/[a-zA-Z0-9_.-]{1,80}$/.test(font.file) ||
          ids.has(font.id)) throw new Error('Project contains invalid font references.');
      ids.add(font.id);
    }
    if (!ids.has(project.baseId)) throw new Error('Project base font is missing.');
    for (const entry of project.assignments) {
      if (!Array.isArray(entry) || entry.length !== 2 || !validCodepoint(entry[0]) ||
          isNoncharacter(entry[0]) || !isSafeAssignment(entry[1], ids)) {
        throw new Error('Project contains invalid glyph assignments.');
      }
    }
    return project;
  }
  function slug(name) {
    return String(name || 'Hybrid Font').trim().replace(/[^a-z0-9_-]+/gi, '-').replace(/^-|-$/g, '').slice(0, 64) || 'Hybrid-Font';
  }
  function transformCommands(commands, factor, outputPath) {
    // OTF/CFF outlines are cubic. TrueType quadratic curves must be converted
    // instead of feeding Q commands to the CFF charstring writer.
    let current = [0, 0], start = [0, 0];
    const x = n => Number(n || 0) * factor;
    for (const c of commands || []) {
      if (c.type === 'M') {
        current = [x(c.x), x(c.y)]; start = current;
        outputPath.moveTo(...current);
      } else if (c.type === 'L') {
        current = [x(c.x), x(c.y)];
        outputPath.lineTo(...current);
      } else if (c.type === 'Q') {
        const control = [x(c.x1), x(c.y1)], end = [x(c.x), x(c.y)];
        const c1 = current.map((n, i) => n + (control[i] - n) * 2 / 3);
        const c2 = end.map((n, i) => n + (control[i] - n) * 2 / 3);
        outputPath.curveTo(...c1, ...c2, ...end);
        current = end;
      } else if (c.type === 'C') {
        current = [x(c.x), x(c.y)];
        outputPath.curveTo(x(c.x1), x(c.y1), x(c.x2), x(c.y2), ...current);
      } else if (c.type === 'Z') {
        outputPath.close(); current = start;
      }
    }
  }
  function buildFont(opentype, fonts, assignments, baseId, familyName) {
    const base = fonts.get(baseId);
    if (!base) throw new Error('Choose a base font first.');
    const upm = base.font.unitsPerEm || 1000;
    const sourceGlyph = (ref) => {
      const source = fonts.get(ref.fontId);
      if (!source || !source.font) throw new Error('A source font is missing.');
      if (ref.glyphIndex >= source.font.glyphs.length) throw new Error('Source glyph no longer exists.');
      return { font: source.font, glyph: source.font.glyphs.get(ref.glyphIndex) };
    };
    function copy(ref, cp, fallbackName) {
      const src = sourceGlyph(ref);
      const scale = upm / (src.font.unitsPerEm || 1000);
      const path = new opentype.Path();
      path.unitsPerEm = upm;
      transformCommands(src.glyph.path && src.glyph.path.commands, scale, path);
      const rawWidth = Number(src.glyph.advanceWidth);
      const width = Number.isFinite(rawWidth) ? Math.max(0, Math.round(rawWidth * scale)) : Math.round(upm * .6);
      return new opentype.Glyph({
        name: fallbackName || 'uni' + cp.toString(16).toUpperCase().padStart(4, '0'),
        unicode: cp === null ? undefined : cp,
        advanceWidth: width,
        path: path
      });
    }
    const glyphs = [copy({fontId:baseId,glyphIndex:0}, null, '.notdef')];
    const ordered = [...assignments.entries()].filter(([cp]) => validCodepoint(cp) && !isNoncharacter(cp)).sort((a,b) => a[0]-b[0]);
    for (const [cp, ref] of ordered) glyphs.push(copy(ref, cp));
    if (glyphs.length < 2) throw new Error('No mapped glyphs are available to export.');
    const family = String(familyName || 'Hybrid Font').trim().slice(0, 100) || 'Hybrid Font';
    const font = new opentype.Font({
      familyName: family,
      styleName: 'Regular',
      unitsPerEm: upm,
      ascender: Number(base.font.ascender) || Math.round(upm*.8),
      descender: Number(base.font.descender) || -Math.round(upm*.2),
      glyphs: glyphs
    });
    return {font, glyphCount:glyphs.length, bytes:font.toArrayBuffer()};
  }
  return { validCodepoint, parseCodepoint, displayCodepoint, isNoncharacter, glyphMappings,
    validateProject, slug, transformCommands, buildFont };
});