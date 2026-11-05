const test=require('node:test');
const assert=require('node:assert/strict');
const core=require('../core.js');
test('parses codepoints without confusing decimal and hexadecimal',()=>{
 assert.equal(core.parseCodepoint('A'),65);
 assert.equal(core.parseCodepoint('★'),0x2605);
 assert.equal(core.parseCodepoint('U+1F642'),0x1f642);
 assert.equal(core.parseCodepoint('0x0041'),65);
 assert.equal(core.parseCodepoint('#65'),65);
 assert.equal(core.parseCodepoint(''),null);
 assert.equal(core.parseCodepoint('word'),null);
 assert.equal(core.parseCodepoint('U+D800'),null);
 assert.equal(core.parseCodepoint('U+110000'),null);
});
test('builds cmap from source tables and rejects surrogate/noncharacters',()=>{
 const font={tables:{cmap:{glyphIndexMap:{65:1,9733:2,55296:3,65535:4}}}};
 assert.deepEqual([...core.glyphMappings(font).entries()],[[65,1],[9733,2]]);
});
test('supports mapped glyph arrays when cmap is unavailable',()=>{
 const font={glyphs:{length:3,get(i){return [{}, {unicode:65,unicodes:[65,192]}, {unicode:66,unicodes:[66]}][i]}}};
 assert.deepEqual([...core.glyphMappings(font).entries()],[[65,1],[192,1],[66,2]]);
});
const project={
 version:1,name:'A Hybrid',baseId:'f00001',
 fonts:[{id:'f00001',file:'fonts/0001.ttf'},{id:'f00002',file:'fonts/0002.otf'}],
 assignments:[[65,{fontId:'f00002',glyphIndex:6}],[9733,{fontId:'f00001',glyphIndex:1}]]
};
test('validates self-contained project references',()=>{
 assert.equal(core.validateProject(project),project);
 assert.throws(()=>core.validateProject({...project,baseId:'not-found'}),/missing/);
 assert.throws(()=>core.validateProject({...project,fonts:[{id:'f00001',file:'../escape'}]}),/invalid/);
 assert.throws(()=>core.validateProject({...project,assignments:[[0xd800,{fontId:'f00001',glyphIndex:1}]]}),/invalid/);
 assert.throws(()=>core.validateProject({...project,assignments:[[65,{fontId:'missing',glyphIndex:1}]]}),/invalid/);
});
test('keeps cubic and quadratic Bezier geometry when scaling',()=>{
 const commands=[
 {type:'M',x:1,y:2},{type:'L',x:3,y:4},{type:'Q',x1:5,y1:6,x:7,y:8},
 {type:'C',x1:9,y1:10,x2:11,y2:12,x:13,y:14},{type:'Z'}];
 const calls=[],path={
 moveTo(...v){calls.push(['M',...v])},lineTo(...v){calls.push(['L',...v])},
 quadTo(...v){calls.push(['Q',...v])},curveTo(...v){calls.push(['C',...v])},
 close(){calls.push(['Z'])}
 };
 core.transformCommands(commands,2,path);
 assert.equal(calls.length,5);
 assert.deepEqual(calls[0],['M',2,4]);
 assert.deepEqual(calls[1],['L',6,8]);
 assert.equal(calls[2][0],'C');
 for(const [i,n] of [[1,26/3],[2,32/3],[3,34/3],[4,40/3],[5,14],[6,16]])
   assert.ok(Math.abs(calls[2][i]-n)<1e-8);
 assert.deepEqual(calls[3],['C',18,20,22,24,26,28]);
 assert.deepEqual(calls[4],['Z']);
});
test('assembles a glyph assigned to another Unicode position and scales its em',()=>{
 class Path { constructor(){this.commands=[]} moveTo(x,y){this.commands.push(['M',x,y])}lineTo(x,y){this.commands.push(['L',x,y])}quadTo(){}curveTo(){}close(){} }
 class Glyph { constructor(props){Object.assign(this,props)} }
 class Font { constructor(props){Object.assign(this,props)}toArrayBuffer(){return new Uint8Array([79,84,84,79]).buffer} }
 const makeFont=(upm,advance)=>({unitsPerEm:upm,ascender:upm*.8,descender:-upm*.2,
 glyphs:{length:2,get(index){return {advanceWidth:advance,path:{commands:[{type:'M',x:100,y:200},{type:'L',x:300,y:400}]}}}}});
 const fonts=new Map([['base',{font:makeFont(1000,600)}],['other',{font:makeFont(2000,1400)}]]);
 const assignments=new Map([[0x41,{fontId:'other',glyphIndex:1}]]);
 const result=core.buildFont({Path,Glyph,Font},fonts,assignments,'base','My Hybrid');
 assert.equal(result.font.glyphs[1].unicode,65);
 assert.equal(result.font.glyphs[1].advanceWidth,700);
 assert.deepEqual(result.font.glyphs[1].path.commands,[['M',50,100],['L',150,200]]);
 assert.deepEqual([...new Uint8Array(result.bytes)],[79,84,84,79]);
});
