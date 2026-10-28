#!/usr/bin/env node
// Offline browser-workbench P0 regression. No source film, captions, secrets or network.
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const page=fs.readFileSync(path.resolve(__dirname,"../episode-finish-workbench.html"),"utf8");
const match=page.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match,"Missing inline offline AV workbench code");
const nodes=new Map(), storage=new Map();
const context=vm.createContext({
  document:{getElementById(id){
    if(!nodes.has(id))nodes.set(id,{addEventListener:()=>{},textContent:"",value:""});
    return nodes.get(id);
  }},
  localStorage:{
    getItem:k=>storage.get(k)??null,
    setItem:(k,v)=>storage.set(k,v),
    removeItem:k=>storage.delete(k)
  }
});
new vm.Script(match[1],{filename:"episode-finish-workbench-inline.js"}).runInContext(context);
function run(expression){return JSON.parse(JSON.stringify(vm.runInContext(expression,context)))}
const original="Hey🙂 there!\nYeah.";
assert.deepEqual(run('insideCaptionSplits("Yeah. | DAN", '+JSON.stringify(original)+',"LANA")'),[
 {start:0,end:12,role:"LANA"},
 {start:12,end:17,role:"DAN"} ]);
assert.deepEqual(run('insideCaptionSplits("@12 | DAN", '+JSON.stringify(original)+',"LANA")'),[
 {start:0,end:12,role:"LANA"},
 {start:12,end:17,role:"DAN"} ]);
assert.equal(run('insideCaptionSplits("", "one", "LANA")'),null);
assert.throws(()=>run('insideCaptionSplits("Yeah | DAN", "Yeah Yeah", "LANA")'),/occur exactly once/);
assert.throws(()=>run('insideCaptionSplits("@9 | DAN", "one", "LANA")'),/inside the original caption/);
assert.throws(()=>run('insideCaptionSplits("@1 | LANA", "one", "LANA")'),/Redundant/);
assert.equal(run('getEdge({id:"B0001",provisional_same_turn:true})'),"");
assert.equal(run('getEdge({id:"B0002",provisional_same_turn:false})'),"");
assert.equal(run('bytesToHex(new Uint8Array([0,9,10,15,255]))'),"00090a0fff");
assert.ok(page.includes('sourceFile'),"Original-source movie picker missing");
assert.ok(page.includes('verifyOriginalSource(file)'),"No true local SHA-256 verification");
assert.ok(page.includes('if(!field||!field.value)'),"Unchecked proposed P0 boundary auto-accepted");
assert.equal(run('proposalForEdge({provisional_same_turn:true})'),"same_speaker_continuation");
assert.equal(run('proposalForEdge({provisional_same_turn:false})'),"new_speaker");
assert.ok(page.includes('MIN_OBSERVED_PLAYBACK_SECONDS=8'),"No measured listening minimum");
assert.ok(page.includes('observed_original_film_playback_seconds'),"No playback evidence in signed review");
assert.ok(page.includes('endorseP0'),"No fast explicit P0 batch endorsement");
assert.ok(page.includes('original_audio_machine_voice_pair_similarity'),
  "Original soundtrack P0 model comparisons not shown during playback");
assert.ok(page.includes('original_audio_model_uncertified_role_hint'),
  "Original soundtrack P1 model abstention not shown during playback");
assert.ok(page.includes('original_actor_voice_verified')||page.includes('not independently heard/verified'),
  "Original-film model display must not be mistaken for certified actor voices");
// Simulate a browser interruption mid-episode. Keep completed decisions only
// for the identical original-film/dialogue packet, not for another episode.
assert.equal(run('packet={episode_id:"S01E01",packet_sha256:"source-A"};saved={boundaries:{B0001:{result:"new_speaker"}},roles:{x:{role:"HARRY"}},batches:{batch1:{observed_original_film_playback_seconds:12}}};$("reviewer").value="Original reviewer";persistDraft();Object.keys(saved.batches).length'),1);
assert.equal(run('saved={boundaries:{},roles:{},batches:{}};$("reviewer").value="";restoreDraft();Object.keys(saved.roles).length'),1);
assert.equal(run('Object.keys(saved.batches).length'),1);
assert.equal(run('$("reviewer").value'),"Original reviewer");
assert.equal(run('packet.packet_sha256="different-source";saved={boundaries:{},roles:{},batches:{}};restoreDraft();Object.keys(saved.roles).length'),0);
assert.equal(run('packet.packet_sha256="source-A";restoreDraft();Object.keys(saved.roles).length'),1);
assert.ok(page.includes('localStorage.removeItem(journalKey())'),
  "Reviewer needs a clear-local-draft control");
console.log("Source-bound local AV draft journal: resume after interruption, isolate source and clear");
assert.ok(page.includes('data-beat-tone'),"P2 audio delivery must attach to a source reading block");
assert.ok(page.includes('data-beat-props'),"P3 clothing and props must attach to a source reading block");
assert.ok(page.includes('data-beat-action'),"P4 physical comedy must attach to a source reading block");
assert.ok(page.includes('original_av_beat_notes:beats'),"Per-block AV notes must be exported in same stable decisions");
assert.ok(page.includes('el.dataset[fieldName]===r.id'),"Beat-note controls must bind by original reading-block ID");
console.log("P2/P3/P4 exact-source line-anchored original AV annotations: PASS");
assert.equal(run('filmSecondsSeen=new Set();recordFullFilmSeconds(.2,1.1,1450)'),2);
assert.equal(run('recordFullFilmSeconds(1.1,120.3,1450)'),0,"Seeking cannot fake whole-film coverage");
assert.equal(run('filmSecondsSeen.size'),2);
assert.equal(run('recordFullFilmSeconds(1.1,2.1,1450)'),1);
assert.equal(run('filmSecondsSeen.size'),3);
assert.ok(page.includes('original_film_playback_coverage:fullFilmCoverage()'),
  "Full-film playback data must travel with the one editorial decision ledger");
assert.ok(page.includes('film_coverage_seconds:[...filmSecondsSeen]'),
  "Original film coverage needs crash-safe local storage");
console.log("Continuous source film timeline: watched seconds count; skipped footage does not");
// A reviewer may navigate or crash mid-line. Preserve draft edits, but NEVER
// promote them to source-reviewed voice or turn decisions.
const draftInput=[
  {dataset:{role:"R100"},value:"LANA WAGNER"},
  {dataset:{edge:"B0100"},value:""},
  {dataset:{split:"R100"},value:"@14 | PAINTER"},
  {dataset:{beatTone:"R100"},value:"hesitant, abrupt"},
  {dataset:{beatAction:"R100"},value:"points to window"}
];
nodes.get("editor").querySelectorAll=()=>draftInput;
nodes.get("performance")?.value;
run('packet={episode_id:"S01E01",packet_sha256:"draft-test",sequential_one_pass_batches:[{id:"S01E01-AV-001"},{id:"S01E01-AV-002"}]};sequence=0;saved={boundaries:{},roles:{},batches:{}};');
nodes.get("performance").value="dry";
nodes.get("props").value="red scarf";
nodes.get("actions").value="points";
nodes.get("watched").checked=false;
assert.equal(run('captureUnacceptedForm();Object.keys(pendingForms).length'),1);
assert.equal(run('saved.roles.R100??null'),null,"Draft voice label MUST NOT be AV certified");
assert.equal(run('pendingForms["S01E01-AV-001"].fields["role:R100"]'),"LANA WAGNER");
run('persistDraft();pendingForms={};restoreDraft()');
assert.equal(run('pendingForms["S01E01-AV-001"].fields["split:R100"]'),"@14 | PAINTER");
for(const el of draftInput)el.value="";
nodes.get("performance").value="";
nodes.get("props").value="";
nodes.get("actions").value="";
run('restoreUnacceptedForm({id:"S01E01-AV-001"})');
assert.equal(draftInput[2].value,"@14 | PAINTER");
assert.equal(draftInput[4].value,"points to window");
assert.equal(nodes.get("props").value,"red scarf");
assert.equal(run('Object.keys(saved.roles).length'),0,"Unaccepted local draft was promoted to source-reviewed decision");
run('packet.packet_sha256="another-episode";pendingForms={};restoreDraft()');
assert.equal(run('Object.keys(pendingForms).length'),0,"Pending corrections leaked to another source packet");
console.log("Unaccepted P0/P1/P2-P4 corrections survive navigation/crash without dishonest AV signoff: PASS");
console.log("Original film SHA, listened P0 and explicitly unverified acoustic hints: PASS");
