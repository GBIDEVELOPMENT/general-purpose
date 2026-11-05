const test=require('node:test');
const assert=require('node:assert/strict');
const opentype=require('opentype.js');
const core=require('../core.js');
function pathOfQuadratic() {
 const p=new opentype.Path();
 p.moveTo(100,0);
 p.quadTo(400,900,700,0);
 p.lineTo(100,0);
 p.close();
 return p;
}
function buildSource(name, upm, glyphPath) {
 const n=new opentype.Glyph({name:'.notdef',advanceWidth:500,path:new opentype.Path()});
 const glyph=new opentype.Glyph({name:'A',unicode:65,advanceWidth:upm*.75,path:glyphPath});
 return new opentype.Font({familyName:name,styleName:'Regular',unitsPerEm:upm,
 ascender:upm*.8,descender:-upm*.2,glyphs:[n,glyph]});
}
test('real opentype.js writer exports mixed OTF with remapped TrueType-style quadratic outlines',()=>{
 const a=new opentype.Path();a.moveTo(0,0);a.lineTo(500,700);a.lineTo(500,0);a.close();
 const base=buildSource('BaseFont',1000,a);
 const donor=buildSource('DonorFont',2000,pathOfQuadratic());
 const records=new Map([['base',{font:base}],['donor',{font:donor}]]);
 const assignments=new Map([[65,{fontId:'base',glyphIndex:1}],[0x2605,{fontId:'donor',glyphIndex:1}]]);
 const output=core.buildFont(opentype,records,assignments,'base','Mixed Geometry');
 const reparsed=opentype.parse(output.bytes);
 assert.ok(reparsed.charToGlyphIndex('A')>0);
 assert.ok(reparsed.charToGlyphIndex('★')>0);
 assert.equal(reparsed.unitsPerEm,1000);
 const donorGlyph=reparsed.charToGlyph('★');
 assert.equal(donorGlyph.advanceWidth,750);
 assert.ok(donorGlyph.path.commands.some(cmd=>cmd.type==='C'),'quadratic must be represented by cubic CFF curves');
 assert.ok(donorGlyph.path.commands.every(cmd=>cmd.type!=='Q'),'OTF writer should not contain raw Q');
 assert.equal(reparsed.getEnglishName('fontFamily'),'Mixed Geometry');
});
