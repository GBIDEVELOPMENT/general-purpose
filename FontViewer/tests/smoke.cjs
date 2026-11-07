'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const page=fs.readFileSync(path.join(root,'index.html'),'utf8');
const library=fs.readFileSync(path.join(root,'library.js'),'utf8');
const script=page.split("<script>\n'use strict';")[1]?.split('</script>')[0];
assert.ok(script,'Application script must exist');
new vm.Script("'use strict';"+script,{filename:'index-inline.js'});
new vm.Script(library,{filename:'library.js'});

assert.match(page,/ScribbleBoxDemo-gyWq\.ttf/);
assert.match(page,/P22%20Stanyan%20Regular%20Regular\.ttf/);
assert.match(page,/library\.js/);
assert.match(page,/id="libraryPanel"/);
assert.match(page,/id="newList"/);
assert.match(page,/id="viewList"/);
assert.match(page,/id="clear" class="danger" disabled>Hide all/);
assert.match(script,/FontLibrary\.save\(meta,raw\)/);
assert.match(script,/FontLibrary\.all\('fonts'\)/);
assert.match(script,/FontLibrary\.get\('data',meta\.id\)/);
assert.match(script,/FontLibrary\.remove\(ids\)/);
assert.match(script,/FontLibrary\.saveList\(list\)/);
assert.match(script,/meta\.hidden=true/);
assert.match(script,/meta\.tags=tags/);
assert.match(script,/requestAnimationFrame/);

const start=page.indexOf('const VARIANT_WORDS='),end=page.indexOf('const supported=',start);
assert.ok(start>=0&&end>start);
const helpers=new Function('safeName',page.slice(start,end)+';return {familyStem,relatedFaces};')(x=>String(x));
function related(a,b,sa='fonts.zip',sb=sa){
 return helpers.relatedFaces({familyName:a,source:sa},{familyName:b,source:sb});
}
const cases=[
 ['Zounderkite','Zounderkite 3D',true],
 ['Zounderkite','Zounderkite Super-Italic',true],
 ['Stoutface','Stoutface SC Small Caps',true],
 ['KBYoureJustMyType','KBYoureJustMyTypeThin',true],
 ['GargleCdRg-Bold','GargleExRg-Bold',true],
 ['Super Comic','Super Hockey',false],
 ['Patrick Hand','Unkempt Bold',false],
 ['DKJalebi','DKNewBeginnings',false]
];
for(const [a,b,expected] of cases)assert.equal(related(a,b,'one.zip','two.zip'),expected,a+' / '+b);
assert.equal(related('Patrick Hand','Unkempt Bold','combined.zip','combined.zip'),false);
console.log('Font Shelf: HTML, persistence contracts, and '+(cases.length+1)+' family grouping smoke checks passed.');
