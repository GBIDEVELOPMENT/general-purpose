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
assert.match(page,/src="\.\/vendor\/fflate\.js"/);
assert.match(page,/import\('\.\/vendor\/fontkit\.js'\)/);
assert.doesNotMatch(page,/https:\/\/(?:cdn\.jsdelivr\.net|esm\.sh)/);
for(const file of ['fontkit.js','fflate.js']){
 const bundle=path.join(root,'.generated','vendor',file);
 assert.ok(fs.statSync(bundle).size>1000,'Missing local vendor asset '+file);
}
const android=fs.readFileSync(path.join(root,'android','app','src','main','java','dev','gbidevelopment','fontshelf','MainActivity.java'),'utf8');
const gradle=fs.readFileSync(path.join(root,'android','app','build.gradle'),'utf8');
assert.match(android,/WebViewAssetLoader/);
assert.match(android,/ACTION_OPEN_DOCUMENT/);
assert.match(gradle,/\.generated\/vendor/);
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
assert.match(script,/meta\.familyTags=tags/);
assert.match(script,/groupedCacheKey/);
assert.match(script,/font-shelf-preview/);
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
 ['GargleCdRg-Bold','GargleExRg-Bold',false],
 ['Super Comic','Super Hockey',false],
 ['Patrick Hand','Unkempt Bold',false],
 ['DKJalebi','DKNewBeginnings',false]
];
for(const [a,b,expected] of cases)assert.equal(related(a,b,'one.zip','two.zip'),expected,a+' / '+b);
assert.equal(related('GargleCdRg-Bold','GargleExRg-Bold','gargle.zip','gargle.zip'),true);
assert.equal(related('Patrick Hand','Unkempt Bold','combined.zip','combined.zip'),false);
console.log('Font Shelf: HTML, persistence contracts, and '+(cases.length+1)+' family grouping smoke checks passed.');
