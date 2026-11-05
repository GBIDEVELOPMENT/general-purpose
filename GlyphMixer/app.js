(function () {
'use strict';
const core = window.GlyphMixerCore;
const opentype = window.opentype;
const zip = window.fflate;
const $ = id => document.getElementById(id);
const MAX_FONTS = 80, MAX_FILE = 30*1024*1024, MAX_TOTAL = 160*1024*1024, MAX_ZIP_ENTRIES = 300;
const SUPPORTED = /\.(ttf|otf|woff)$/i;
const ARCHIVE = /\.zip$/i;
const state = {
  fonts:new Map(), original:new Map(), assignments:new Map(),
  baseId:null, seq:0, tab:'map', selected:null,
  page:0, pickerPage:0, pickerCandidates:[], history:[],
  compiledUrl:null, compiledFace:null, compiledVersion:-1,
  version:0, busy:false, toastTimer:0
};
if (!core || !opentype || !zip) {
  $('welcome').insertAdjacentText('beforeend', ' Required font processing libraries could not load. Check your connection and reload.');
  return;
}
function notice(message, bad) {
  const el=$('toast'); el.textContent=message; el.style.borderColor=bad?'var(--bad)':'var(--border)';
  el.classList.add('visible'); clearTimeout(state.toastTimer);
  state.toastTimer=setTimeout(()=>el.classList.remove('visible'),6000);
}
function setBusy(busy) {
  state.busy=busy;
  for(const id of ['chooseBase','openInitialProject','saveProject','openProject','exportFont','addSources','refreshPreview']) $(id).disabled=busy;
}
function family(font, fallback) {
  const names=font.names || {};
  const name=key=>names[key]?.en || Object.values(names[key]||{})[0] || '';
  return String(name('fullName') || [name('fontFamily'),name('fontSubfamily')].filter(Boolean).join(' ') || fallback.replace(/\.[^.]+$/,'')).slice(0,150);
}
function mimeName(file) { return file.replace(/[^a-z0-9_.-]/gi,'_').slice(-90); }
function bytesFingerprint(bytes) {
  let h=2166136261;
  for(let i=0;i<bytes.length;i++) h=Math.imul(h^bytes[i],16777619);
  return bytes.length+':'+(h>>>0).toString(16);
}
function codeDisplay(cp) {
  if (cp===32) return '␣';
  if (cp<32 || (cp>=0x7f && cp<0xa0)) return '·';
  try { return String.fromCodePoint(cp) } catch { return '□' }
}
function allSourcePoints(rec) {
  if(!rec.points) rec.points=[...core.glyphMappings(rec.font).entries()].sort((a,b)=>a[0]-b[0]);
  return rec.points;
}
function make(tag,cls,txt) {
  const node=document.createElement(tag);
  if(cls) node.className=cls;
  if(txt!==undefined) node.textContent=txt;
  return node;
}
function releaseRecord(rec) {
  try { if(rec.face) document.fonts.delete(rec.face) } catch {}
  if(rec.url) URL.revokeObjectURL(rec.url);
}
function releasePreview() {
  if(state.compiledFace) { try {document.fonts.delete(state.compiledFace)} catch{} }
  if(state.compiledUrl) URL.revokeObjectURL(state.compiledUrl);
  state.compiledFace=null;state.compiledUrl=null;state.compiledVersion=-1;
}
function newRecord(bytes, filename, id) {
  if(bytes.byteLength>MAX_FILE) throw new Error('A font exceeds the 30 MB per-font limit.');
  let font;
  try {
    const copy=bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);
    font=opentype.parse(copy);
  } catch(e) { throw new Error('Cannot parse '+filename+': '+e.message) }
  const record={id,filename:String(filename).slice(0,150),bytes, font,
    name:family(font,filename), fingerprint:bytesFingerprint(bytes),
    points:null, url:null, face:null, cssName:'glyphmixer-'+id};
  return record;
}
async function setupFace(rec) {
  const blob=new Blob([rec.bytes],{type:'font/otf'});
  rec.url=URL.createObjectURL(blob);
  try {
    rec.face=new FontFace(rec.cssName,'url("'+rec.url+'")');
    await rec.face.load();
    document.fonts.add(rec.face);
  } catch(e) {
    // Parsing, mapping, and export can still work for fonts the browser will not render.
    rec.face=null;
  }
}
async function recordsFromFiles(files) {
  let entries=[],total=0;
  for (const file of files) {
    total+=file.size;
    if(total>MAX_TOTAL) throw new Error('Selected files exceed 160 MB.');
    if(ARCHIVE.test(file.name)) {
      if(file.size>MAX_TOTAL) throw new Error('Archive too large.');
      let unpacked;
      try {
        const raw=new Uint8Array(await file.arrayBuffer());
        let zipTotal=0,count=0;
        unpacked=zip.unzipSync(raw,{filter:info=>{
          if(!SUPPORTED.test(info.name)) return false;
          count++;zipTotal+=info.originalSize;
          if(count>MAX_ZIP_ENTRIES || zipTotal>MAX_TOTAL || info.originalSize>MAX_FILE)
            throw new Error('ZIP exceeds safe import limits.');
          return true;
        }});
      }catch(e){throw new Error('Cannot open ZIP '+file.name+': '+e.message)}
      const contents=Object.entries(unpacked).sort((a,b)=>a[0].localeCompare(b[0]));
      entries.push(...contents.map(([name,bytes])=>({name:file.name+' / '+name,bytes})));
    } else if(SUPPORTED.test(file.name)) {
      entries.push({name:file.name,bytes:new Uint8Array(await file.arrayBuffer())});
    } else {
      throw new Error('Unsupported file type: '+file.name+'. Use OTF, TTF, WOFF, or ZIP.');
    }
  }
  if(!entries.length) throw new Error('No supported fonts found. OTF, TTF and WOFF are supported.');
  if(entries.length>MAX_FONTS) throw new Error('A selection can contain at most 80 fonts.');
  return entries;
}
async function importSources(files, asBase) {
  if(state.busy || !files.length) return;
  if(asBase && state.baseId && !confirm('Start a new project? The current unsaved project will be replaced.')) return;
  setBusy(true);
  const prepared=[];
  try {
    const entries=await recordsFromFiles(files);
    const existing=asBase?new Set():new Set([...state.fonts.values()].map(x=>x.fingerprint));
    for(const e of entries) {
      if(prepared.length+(!asBase?state.fonts.size:0)>=MAX_FONTS) throw new Error('80-font project limit reached.');
      const id='f'+String(state.seq+prepared.length+1).padStart(5,'0');
      const rec=newRecord(e.bytes,e.name,id);
      if(existing.has(rec.fingerprint)) continue;
      existing.add(rec.fingerprint);
      prepared.push(rec);
    }
    if(!prepared.length) { notice('Those fonts are already in this project.');return; }
    for(const rec of prepared) await setupFace(rec);
    if(asBase) {
      for(const rec of state.fonts.values()) releaseRecord(rec);
      releasePreview();
      state.fonts.clear();state.original.clear();state.assignments.clear();state.history=[];
      state.baseId=prepared[0].id;
      const cmap=core.glyphMappings(prepared[0].font);
      for(const [cp,index] of cmap) {
        const ref={fontId:state.baseId,glyphIndex:index};
        state.original.set(cp,ref);
        state.assignments.set(cp,{...ref});
      }
      $('familyName').value=prepared[0].name.replace(/\s*(Regular|Book|Roman)$/i,'').trim()+' Remix';
      state.seq+=prepared.length; prepared.forEach(rec=>state.fonts.set(rec.id,rec));
      state.page=0;state.tab='map';state.version++;
      $('welcome').hidden=true;$('workspace').hidden=false;$('bottomNav').hidden=false;
      tab('map');
      notice('Base loaded with '+cmap.size.toLocaleString()+' mapped characters. Add sources whenever you like.');
    } else {
      state.seq+=prepared.length; prepared.forEach(rec=>state.fonts.set(rec.id,rec));
      notice('Added '+prepared.length+' new source font'+(prepared.length===1?'':'s')+'.');
    }
    renderAll();
  } catch(e) { prepared.forEach(rec=>{if(!state.fonts.has(rec.id)) releaseRecord(rec)});notice(e.message,true) }
  finally {setBusy(false)}
}
function changed(cp) {
  const a=state.assignments.get(cp),b=state.original.get(cp);
  return Boolean(a && (!b || a.fontId!==b.fontId || a.glyphIndex!==b.glyphIndex));
}
function checkpoint() {
  state.history.push(new Map([...state.assignments].map(([k,v])=>[k,{...v}])));
  if(state.history.length>15) state.history.shift();
}
function mutate() {
  state.version++;state.page=0;
  renderAll();
}
function undo() {
  if(!state.history.length)return;
  state.assignments=state.history.pop(); state.version++;
  renderAll(); if(state.selected!==null) renderCurrent();
  notice('Last mapping change undone.');
}
function renderSummary() {
  const changes=[...state.assignments.keys()].filter(changed).length;
  $('projectSummary').textContent=state.assignments.size.toLocaleString()+' positions · '+changes+' replacement'+(changes===1?'':'s')+' · '+state.fonts.size+' source font'+(state.fonts.size===1?'':'s');
}
function renderGlyph(canvas, fontId, index) {
  const rec=state.fonts.get(fontId);
  if(!rec)return;
  try {
    const glyph=rec.font.glyphs.get(index);
    if(!glyph)return;
    const cssWidth=62,cssHeight=46,scale=Math.min(2,window.devicePixelRatio||1);
    canvas.width=cssWidth*scale;canvas.height=cssHeight*scale;canvas.style.width='100%';canvas.style.height=cssHeight+'px';
    const context=canvas.getContext('2d');
    if(!context) return;
    context.scale(scale,scale);
    const ink=getComputedStyle(document.documentElement).getPropertyValue('--text').trim()||'#fff';
    context.fillStyle=ink;
    const advance=glyph.advanceWidth || rec.font.unitsPerEm;
    const fontSize=36;
    const width=advance/(rec.font.unitsPerEm||1000)*fontSize;
    glyph.draw(context,Math.max(2,(cssWidth-width)/2),36,fontSize,{fill:ink},rec.font);
  }catch(e){canvas.replaceWith(make('span','letter','□'))}
}
function tile(cp, ref, target) {
  const label=codeDisplay(cp),node=make('button','tile'+(target&&changed(cp)?' changed':'')); node.type='button';
  node.setAttribute('aria-label',(target?'Edit destination ':'Choose source ')+core.displayCodepoint(cp)+' '+label);
  const canvas=make('canvas','letter');
  const code=make('span','code',core.displayCodepoint(cp).slice(2));
  node.append(canvas,code);
  if(ref)renderGlyph(canvas,ref.fontId,ref.glyphIndex);
  else canvas.replaceWith(make('span','letter',label));
  return node;
}
const TARGET_PAGE=180;
function filteredTargets() {
  const term=$('targetSearch').value.trim().toLowerCase();
  const filter=$('rangeFilter').value;
  const cpSearch=core.parseCodepoint(term);
  return [...state.assignments.keys()].filter(cp=>{
    if(filter==='common' && !(cp>=0x20&&cp<=0x024f)) return false;
    if(filter==='other' && cp<=0x024f) return false;
    if(filter==='changes' && !changed(cp))return false;
    if(!term)return true;
    if(cpSearch!==null)return cp===cpSearch;
    return core.displayCodepoint(cp).toLowerCase().includes(term) ||
      cp.toString(16).includes(term.replace(/^(u\+|0x)/,''));
  }).sort((a,b)=>a-b);
}
function renderMap() {
  const grid=$('targetGrid');grid.replaceChildren();
  const filtered=filteredTargets(),shown=filtered.slice(0,TARGET_PAGE*(state.page+1));
  $('mapCount').textContent=filtered.length.toLocaleString()+' characters · showing '+shown.length;
  for(const cp of shown) {
    const node=tile(cp,state.assignments.get(cp),true);
    node.addEventListener('click',()=>openPicker(cp));
    grid.append(node);
  }
  if(!filtered.length) grid.append(make('p','footnote','No matching characters. Try another range or add a position.'));
  $('showMore').hidden=shown.length>=filtered.length;
}
function renderSources() {
  const list=$('sourceList');list.replaceChildren();
  for(const rec of state.fonts.values()) {
    const card=make('article','source-card'),title=make('h3','',rec.name);
    const file=make('p','',rec.filename),sample=make('div','source-sample','Aa Bb 012345 ★');
    if(rec.face) sample.style.fontFamily='"'+rec.cssName+'"';
    const row=make('div','source-actions');
    const count=make('span','tiny muted',allSourcePoints(rec).length.toLocaleString()+' Unicode mappings');
    row.append(count);
    if(rec.id===state.baseId)row.append(make('span','base-chip','BASE FONT'));
    else {
      const remove=make('button','button secondary','Remove');
      remove.onclick=()=>{
        if([...state.assignments.values()].some(v=>v.fontId===rec.id)) {
          notice('This source is in use. Revert its replacements before removing.',true);return;
        }
        releaseRecord(rec);state.fonts.delete(rec.id);state.version++;renderAll();
      };
      row.append(remove);
    }
    card.append(title,file,sample,row);list.append(card);
  }
}
function renderAll(){renderSummary();renderMap();renderSources()}
function tab(name) {
  state.tab=name;
  for(const key of ['map','sources','preview']) $(key+'Panel').hidden=(name!==key);
  for(const btn of document.querySelectorAll('[data-tab]')) {
    const active=btn.dataset.tab===name;
    btn.classList.toggle('active',active);
    if(active) btn.setAttribute('aria-current','page');else btn.removeAttribute('aria-current');
  }
  if(name==='preview') refreshPreview();
}
function renderCurrent() {
  const cp=state.selected;
  if(cp===null)return;
  const current=state.assignments.get(cp),original=state.original.get(cp);
  const rec=current&&state.fonts.get(current.fontId);
  $('pickerCurrent').textContent='Current: '+(rec?.name||'none')+' · glyph #'+(current?.glyphIndex??'?')+
    (original?' · '+(changed(cp)?'modified':'original'):' · new Unicode position');
  $('revertGlyph').disabled=!original||!changed(cp);
  $('removePosition').disabled=state.original.has(cp);
}
function openPicker(cp) {
  state.selected=cp;state.pickerPage=0;
  $('pickerTitle').textContent='Replace '+codeDisplay(cp);
  $('pickerSubtitle').textContent='Destination '+core.displayCodepoint(cp);
  const sel=$('pickerFont');sel.replaceChildren();
  for(const rec of state.fonts.values()){
    const opt=make('option','',rec.name);opt.value=rec.id;sel.append(opt);
  }
  const current=state.assignments.get(cp);
  sel.value=current?.fontId||state.baseId;
  $('pickerSearch').value='';
  $('pickerOverlay').hidden=false;
  document.body.style.overflow='hidden';
  renderCurrent();renderPicker();
  $('pickerSearch').focus({preventScroll:true});
}
function closePicker() {
  $('pickerOverlay').hidden=true; document.body.style.overflow='';state.selected=null;
}
function searchPickerPoints(rec) {
  const query=$('pickerSearch').value.trim().toLowerCase();
  const points=allSourcePoints(rec);
  if(!query) return points;
  const indexMatch=/^#(\d+)$/.exec(query);
  if(indexMatch) {
    const i=Number(indexMatch[1]);
    if(i>=0 && i<rec.font.glyphs.length) {
      const found=points.find(p=>p[1]===i);
      return [[found?.[0]??0,i]];
    }
    return [];
  }
  const parsed=core.parseCodepoint(query);
  if(parsed!==null)return points.filter(([cp])=>parsed===cp);
  return points.filter(([cp])=>core.displayCodepoint(cp).toLowerCase().includes(query)||
    cp.toString(16).includes(query.replace(/^(u\+|0x)/,'')));
}
function renderPicker() {
  const rec=state.fonts.get($('pickerFont').value); if(!rec)return;
  const points=searchPickerPoints(rec);
  const shown=points.slice(0,TARGET_PAGE*(state.pickerPage+1));
  const grid=$('pickerGrid');grid.replaceChildren();
  $('pickerCount').textContent=points.length.toLocaleString()+' matching glyphs · '+shown.length+' shown';
  for(const [cp,index] of shown) {
    const node=tile(cp,{fontId:rec.id,glyphIndex:index},false);
    if(state.assignments.get(state.selected)?.fontId===rec.id &&
       state.assignments.get(state.selected)?.glyphIndex===index) node.classList.add('active');
    node.addEventListener('click',()=>{
      checkpoint();
      state.assignments.set(state.selected,{fontId:rec.id,glyphIndex:index});
      mutate();renderCurrent();renderPicker();
      notice('Assigned glyph #'+index+' to '+core.displayCodepoint(state.selected)+'.');
    });
    grid.append(node);
  }
  if(!points.length) grid.append(make('p','footnote','No glyph matches. Try a character, U+hex code, or #glyph index.'));
  $('pickerMore').hidden=shown.length>=points.length;
}
function addPosition() {
  const raw=prompt('Enter a destination character or Unicode position, e.g. ★ or U+2605');
  if(raw===null)return;
  const cp=core.parseCodepoint(raw);
  if(cp===null||core.isNoncharacter(cp)) {notice('Use a single character or a valid U+hex position.',true);return}
  if(state.assignments.has(cp)) {openPicker(cp);return}
  const fallback=state.fonts.get(state.baseId);
  const mapped=core.glyphMappings(fallback.font).get(cp);
  const ref={fontId:state.baseId,glyphIndex:mapped||0};
  checkpoint();state.assignments.set(cp,ref);mutate();
  $('rangeFilter').value='all';$('targetSearch').value=core.displayCodepoint(cp);
  renderMap();openPicker(cp);
  notice('Added '+core.displayCodepoint(cp)+'. Choose a source glyph.');
}
async function getCompiled() {
  const result=core.buildFont(opentype,state.fonts,state.assignments,state.baseId,$('familyName').value);
  return new Blob([result.bytes],{type:'font/otf'});
}
async function refreshPreview() {
  if(state.busy||!state.baseId)return;
  if(state.compiledVersion===state.version && state.compiledFace) {drawPreview();return}
  $('previewOutput').textContent='Building preview…';
  try {
    const blob=await getCompiled();
    releasePreview();
    const url=URL.createObjectURL(blob);
    const face=new FontFace('GlyphMixerPreview','url("'+url+'")');
    try { await face.load();document.fonts.add(face) }
    catch(e) {URL.revokeObjectURL(url);throw e}
    state.compiledUrl=url;state.compiledFace=face;state.compiledVersion=state.version;
    drawPreview();
  }catch(e){$('previewOutput').textContent='Preview unavailable: '+e.message;notice(e.message,true)}
}
function drawPreview() {
  const view=$('previewOutput');
  view.textContent=$('previewText').value||' ';
  view.style.fontFamily=state.compiledFace?'"GlyphMixerPreview",sans-serif':'sans-serif';
  view.style.fontSize=$('previewSize').value+'px';
}
async function binarySave(build, filename, extension, mime) {
  // Request the Android file destination directly in the button gesture.
  // Heavy OTF generation/ZIP packaging happens only after the picker returns.
  let handle=null;
  if(typeof window.showSaveFilePicker==='function') {
    try {
      handle=await window.showSaveFilePicker({
        suggestedName:filename,
        types:[{description:extension.toUpperCase()+' file',accept:{[mime]:['.'+extension]}}]
      });
    }catch(e) {
      if(e.name==='AbortError')return false;
      // Fall back when the browser rejects this file type or picker.
    }
  }
  const blob=await build();
  if(handle) {
    const writer=await handle.createWritable();
    try { await writer.write(blob);await writer.close() }
    catch(e) {try {await writer.abort()}catch{} throw e}
    notice('Saved '+filename+' to your device.');
    return true;
  }
  const url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),60000);
  notice('Download started for '+filename+'.');
  return true;
}
function saveProjectArchive() {
  const manifest={
    format:'glyph-mixer-project',version:1,
    name:$('familyName').value,baseId:state.baseId,preview:$('previewText').value,
    fonts:[],assignments:[...state.assignments.entries()]
  };
  const archive={};
  let i=0;
  for(const rec of state.fonts.values()){
    const ext=/\.(ttf|otf|woff)$/i.exec(rec.filename)?.[1].toLowerCase()||'otf';
    const file='fonts/'+String(++i).padStart(4,'0')+'.'+ext;
    manifest.fonts.push({id:rec.id,file,name:rec.name,filename:rec.filename});
    archive[file]=rec.bytes;
  }
  archive['project.json']=zip.strToU8(JSON.stringify(manifest));
  return new Blob([zip.zipSync(archive,{level:0})],{type:'application/zip'});
}
async function saveProject() {
  if(state.busy||!state.baseId)return;
  setBusy(true);
  try {
    await binarySave(()=>saveProjectArchive(),core.slug($('familyName').value)+'.glyphmix','glyphmix','application/zip');
  }catch(e){notice('Project save failed: '+e.message,true)}
  finally{setBusy(false)}
}
async function openProjectFile(file) {
  if(state.busy||!file)return;
  if(state.baseId&&!confirm('Open the saved project? Unsaved changes to your current project will be lost.'))return;
  setBusy(true);
  const prepared=[];
  try {
    if(file.size>MAX_TOTAL)throw new Error('Project file is too large.');
    let total=0,count=0;
    const entries=zip.unzipSync(new Uint8Array(await file.arrayBuffer()),{filter:info=>{
      count++;total+=info.originalSize;
      if(total>MAX_TOTAL||count>MAX_ZIP_ENTRIES||info.originalSize>MAX_TOTAL)throw new Error('Project archive exceeds safe limits.');
      return true;
    }});
    if(!entries['project.json'])throw new Error('Project manifest is missing.');
    const project=core.validateProject(JSON.parse(zip.strFromU8(entries['project.json'])));
    for(const item of project.fonts) {
      const raw=entries[item.file];
      if(!raw)throw new Error('Missing embedded font: '+item.file);
      const rec=newRecord(raw,item.filename||item.file,item.id);
      await setupFace(rec);
      prepared.push(rec);
    }
    const fontMap=new Map(prepared.map(rec=>[rec.id,rec]));
    const original=new Map([...core.glyphMappings(fontMap.get(project.baseId).font)]
      .map(([cp,index])=>[cp,{fontId:project.baseId,glyphIndex:index}]));
    const assignments=new Map();
    for(const [cp,ref] of project.assignments) {
      const source=fontMap.get(ref.fontId);
      if(!source||ref.glyphIndex>=source.font.glyphs.length)
        throw new Error('Project references an unavailable glyph.');
      assignments.set(cp,{...ref});
    }
    for(const rec of state.fonts.values())releaseRecord(rec);
    releasePreview();
    state.fonts=fontMap;state.original=original;state.assignments=assignments;
    state.baseId=project.baseId;state.seq=Math.max(...prepared.map(r=>Number(r.id.replace(/\D/g,''))||0));
    state.history=[];state.version++;state.page=0;
    $('familyName').value=project.name.slice(0,100);
    $('previewText').value=project.preview||'Thus Spake Zarathustra';
    $('welcome').hidden=true;$('workspace').hidden=false;$('bottomNav').hidden=false;
    tab('map');renderAll();notice('Project restored with '+prepared.length+' embedded source fonts.');
  }catch(e){prepared.forEach(releaseRecord);notice('Cannot open project: '+e.message,true)}
  finally{setBusy(false)}
}
async function exportFont() {
  if(state.busy||!state.baseId)return;
  setBusy(true);
  try {
    await binarySave(()=>getCompiled(),core.slug($('familyName').value)+'.otf','otf','font/otf');
    notice('OTF prepared with '+state.assignments.size.toLocaleString()+' Unicode positions. Complex shaping and kerning are not preserved.');
  }catch(e){notice('Font export failed: '+e.message,true)}
  finally{setBusy(false)}
}
function setTheme(mode) {
  document.documentElement.dataset.theme=mode;
  $('themeToggle').textContent=mode==='dark'?'☀':'☾';
  $('themeToggle').setAttribute('aria-label','Switch to '+(mode==='dark'?'light':'dark')+' theme');
  localStorage.setItem('glyph-mixer-theme',mode);
  if(state.baseId)renderMap();
}
setTheme(localStorage.getItem('glyph-mixer-theme')==='light'?'light':'dark');
$('themeToggle').onclick=()=>setTheme(document.documentElement.dataset.theme==='dark'?'light':'dark');
$('chooseBase').onclick=()=>$('baseFiles').click();
$('openInitialProject').onclick=$('openProject').onclick=()=>$('projectFile').click();
$('addSources').onclick=()=>$('sourceFiles').click();
$('baseFiles').onchange=e=>{importSources([...e.target.files],true);e.target.value=''};
$('sourceFiles').onchange=e=>{importSources([...e.target.files],false);e.target.value=''};
$('projectFile').onchange=e=>{openProjectFile(e.target.files[0]);e.target.value=''};
$('saveProject').onclick=saveProject;
$('exportFont').onclick=exportFont;
$('addPosition').onclick=addPosition;
$('targetSearch').oninput=()=>{state.page=0;renderMap()};
$('rangeFilter').onchange=()=>{state.page=0;renderMap()};
$('showMore').onclick=()=>{state.page++;renderMap()};
for(const btn of document.querySelectorAll('[data-tab]'))btn.onclick=()=>tab(btn.dataset.tab);
$('closePicker').onclick=$('closePickerDone').onclick=$('pickerBackdrop').onclick=closePicker;
$('pickerFont').onchange=()=>{state.pickerPage=0;renderPicker()};
$('pickerSearch').oninput=()=>{state.pickerPage=0;renderPicker()};
$('pickerMore').onclick=()=>{state.pickerPage++;renderPicker()};
$('revertGlyph').onclick=()=>{
 const cp=state.selected,ref=state.original.get(cp);
 if(!ref)return;
 checkpoint();state.assignments.set(cp,{...ref});mutate();renderCurrent();renderPicker();
};
$('removePosition').onclick=()=>{
 const cp=state.selected;if(state.original.has(cp))return;
 checkpoint();state.assignments.delete(cp);mutate();closePicker();
};
$('previewText').oninput=drawPreview;
$('previewSize').oninput=()=>{$('previewSizeValue').textContent=$('previewSize').value;drawPreview()};
$('refreshPreview').onclick=()=>{state.compiledVersion=-1;refreshPreview()};
$('familyName').oninput=()=>{state.version++;renderSummary()};
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('pickerOverlay').hidden)closePicker()});
const undoButton=make('button','button secondary','↶ Undo');
undoButton.type='button';undoButton.style.marginLeft='6px';undoButton.onclick=undo;
$('addPosition').insertAdjacentElement('beforebegin',undoButton);
renderSummary();
})();