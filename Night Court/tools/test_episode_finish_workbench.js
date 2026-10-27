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
const context=vm.createContext({document:{getElementById:()=>({})}});
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
console.log("Source-exact Unicode P0 multi-voice review workbench: PASS");
