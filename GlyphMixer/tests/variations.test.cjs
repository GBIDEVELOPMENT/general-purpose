const test=require('node:test');
const assert=require('node:assert/strict');
const V=require('../variations-core.js');
const byte=()=>new Uint8Array([0,1,2]);
const fonts=new Map([
 ["f00001",{id:"f00001",filename:"base.ttf",bytes:byte()}],
 ["f00002",{id:"f00002",filename:"donor.otf",bytes:byte()}],
 ["f00003",{id:"f00003",filename:"second.woff",bytes:byte()}]
]);
const original=new Map([
 [65,{fontId:"f00001",glyphIndex:1}],
 [110,{fontId:"f00001",glyphIndex:2}],
 [111,{fontId:"f00001",glyphIndex:3}],
 [101,{fontId:"f00001",glyphIndex:4}],
 [116,{fontId:"f00001",glyphIndex:5}],
 [104,{fontId:"f00001",glyphIndex:6}]
]);
const assignments=new Map([...original.entries()].map(([k,v])=>[k,{...v}]));
assignments.set(65,{fontId:"f00002",glyphIndex:2});
function alt(extra={}) {
 return {id:"v001",kind:"alternate",target:110,sourceId:"f00002",glyphIndex:7,
  feature:"calt",context:"repeat",...extra};
}
test("parse literal and hexadecimal codepoints; reject surrogates/noncharacters",()=>{
 assert.equal(V.point("n"),110);assert.equal(V.point("U+006E"),110);
 assert.equal(V.point("0x6e"),110);assert.equal(V.point("🪁"),0x1fa81);
 assert.equal(V.point("test"),null);assert.equal(V.point("U+D800"),null);
 assert.equal(V.point("U+FDD0"),null);assert.equal(V.point("U+10FFFF"),null);
});
test("converts sparse mapping changes and contextual rules to headless operations",()=>{
 const rules=[alt(),alt({id:"v002",feature:"salt",context:"before",before:111,sourceId:"f00003",glyphIndex:9}),
  alt({id:"v003",feature:"ss01",context:"after",after:101,glyphIndex:8}),
  {id:"v004",kind:"ligature",sequence:"th",sourceId:"f00002",glyphIndex:22,feature:"dlig"}];
 const x=V.buildRecipe({name:"Z",baseId:"f00001",fonts,assignments,original,rules});
 assert.deepEqual(Object.keys(x.recipe.sources),["f00001","f00002","f00003"]);
 assert.equal(x.fontBytes.length,3);
 assert.equal(x.recipe.operations.length,5);
 assert.deepEqual(x.recipe.operations[0],{action:"reassign",source:"f00002",destination:"U+0041",glyph_index:2,strict:true});
 assert.deepEqual(x.recipe.operations[1],{action:"alternate",source:"f00002",glyph_index:7,strict:true,target:"U+006E",features:["calt"],context:"adjacent-repeat"});
 assert.deepEqual(x.recipe.operations[2].context,{preceded_by:"U+006F"});
 assert.deepEqual(x.recipe.operations[3].context,{followed_by:"U+0065"});
 assert.equal(x.recipe.operations[4].sequence,"th");
 assert.equal(x.recipe.operations[4].feature,"dlig");
});
test("multiple alternate sources, rand feature and explicit two-sided context",()=>{
 const rules=[alt({feature:"rand",context:"none"}),alt({id:"v002",feature:"salt",context:"both",before:111,after:101})];
 const x=V.buildRecipe({name:"Z",baseId:"f00001",fonts,assignments,original,rules});
 assert.deepEqual(x.recipe.operations[1].features,["rand","aalt"]);
 assert.deepEqual(x.recipe.operations[2].context,{preceded_by:"U+006F",followed_by:"U+0065"});
});
test("rejects invalid rules, missing source fonts, and unsupported destination",()=>{
 assert.throws(()=>V.validateRules([alt({feature:"bogus"})],[...fonts.keys()]),/invalid OpenType/);
 assert.throws(()=>V.validateRules([alt({sourceId:"missing"})],[...fonts.keys()]),/missing/);
 assert.throws(()=>V.validateRules([alt({context:"before"})],[...fonts.keys()]),/previous/);
 assert.throws(()=>V.validateRules([alt({target:200})],[...fonts.keys()],{mapped:new Set(assignments.keys())}),/destination/);
 assert.throws(()=>V.validateRules([alt(),alt()],[...fonts.keys()]),/duplicate/);
 assert.throws(()=>V.validateRules([{id:"v1",kind:"ligature",sourceId:"f00002",glyphIndex:5,sequence:"z",feature:"liga"}],[...fonts.keys()]),/2–8/);
});
test("a redundant original mapping is not emitted as replacement",()=>{
 const same=new Map([...original].map(([cp,ref])=>[cp,{...ref}]));
 const x=V.buildRecipe({name:"No changes",baseId:"f00001",fonts,assignments:same,original,rules:[]});
 assert.equal(x.recipe.operations.length,0);
});
