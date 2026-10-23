'use strict';
// Dependency-free smoke and behavior checks for the standalone Expository browser.
// Run: node --test tools/expository/expository.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const source = html.match(/<script>([\s\S]+?)<\/script>/)?.[1];
function fakeNode(tag='DIV') {
  return {
    tagName:tag.toUpperCase(),children:[],value:'',textContent:'',style:{},classList:{add(){},remove(){},contains(){return false}},
    append(...nodes){this.children.push(...nodes)},replaceChildren(...nodes){this.children=nodes},
    remove(){},querySelector(){return null},setAttribute(){},getAttribute(){return null},
    addEventListener(){},focus(){},click(){},get isConnected(){return true}
  };
}
function boot() {
 const elements = new Map(),urls=[];
 const get = id => {
  if (!elements.has(id)) elements.set(id,fakeNode());
  return elements.get(id);
 };
 get('scope').value='folder';
 const document={getElementById:get,createElement:fakeNode,createTextNode:s=>({textContent:s}),addEventListener(){},activeElement:fakeNode()};
 const history={replaceState(_a,_b,u){urls.push(u)}};
 const location={hash:'',pathname:'/index.html',search:'',href:'https://example.test/index.html'};
 const localStorage={getItem(){return null},setItem(){}};
 // Remove only the page-load bootstrap. Actual application functions execute unmodified.
 const pos=source.indexOf('const match=location.hash.slice(1)');
 assert.ok(pos>0, 'page-load bootstrap located');
 const isolated='return '+source.slice(0,pos).trimStart()+
  'return {state,treeAdd,expandAncestors,paintTree,currentMatches,updateHash,withMediaType,resetSession,compareReady};\n})();';
 const app=new Function('document','history','location','localStorage','Option',isolated)(
   document,history,location,localStorage,function Option(name,value){return {name,value}}
 );
 return {app,get,urls};
}
test('browser source parses and controls have matching elements',()=>{
 assert.ok(source, 'inline script exists');
 assert.doesNotThrow(()=>new vm.Script(source));
 for(const id of ['tree','scope','filter','copyFolder','copyFile','disconnect','preview','prevPreview','nextPreview'])
   assert.ok(html.includes('id="'+id+'"'), id+' exists');
});
test('folder index produces ancestry; collapsible tree limits DOM rows',()=>{
 const {app,get}=boot();
 app.treeAdd('design/storyboards/P0');app.treeAdd('design/proposals');
 assert.ok(app.state.tree.has('design/storyboards'));
 app.paintTree();
 assert.equal(get('tree').children.length,1,'collapsed top-level row only');
 app.state.expanded.add('design');app.paintTree();
 assert.equal(get('tree').children.length,3,'expanding shows immediate children');
 app.expandAncestors('design/storyboards/P0');
 assert.ok(app.state.expanded.has('design/storyboards'));
 app.paintTree();
 assert.equal(get('tree').children.length,4,'expanding ancestors exposes leaf');
});
test('repo-wide names and recursive image views match expected paths',()=>{
 const {app,get}=boot();
 app.state.indexReady=true;
 app.state.indexEntries=[
 {type:'file',name:'a.svg',path:'design/proposals/a.svg'},
 {type:'file',name:'b.png',path:'design/proposals/sub/b.png'},
 {type:'file',name:'app.js',path:'src/app.js'}];
 get('scope').value='repo';get('filter').value='proposals';
 assert.deepEqual(app.currentMatches().map(x=>x.name),['a.svg','b.png']);
 get('scope').value='images';get('filter').value='';app.state.path='design/proposals';
 assert.deepEqual(app.currentMatches().map(x=>x.name),['a.svg','b.png']);
 app.state.path='src';assert.equal(app.currentMatches().length,0);
 app.state.indexReady=false;app.state.indexError=false;assert.equal(app.currentMatches(),null);
 app.state.indexError=true;app.state.items=[{type:'file',name:'local.png',path:'src/local.png'}];
 assert.equal(app.currentMatches().length,1,'fallback to current-folder images');
});
test('share hashes retain repository slash and never contain credentials',()=>{
 const {app,urls}=boot();
 app.state.repo='gamesbyian/Glimpse';app.state.branch='main';app.state.path='design/proposals';app.state.token='SECRET_TEST_TOKEN';
 app.updateHash('design/proposals/sample image.svg');
 assert.equal(urls.at(-1),'#gamesbyian/Glimpse/main/design/proposals?file=design%2Fproposals%2Fsample%20image.svg');
 assert.ok(!urls.at(-1).includes('SECRET_TEST_TOKEN'));
});
test('format-specific preview blob type and explicit session reset',()=>{
 const {app,get}=boot();
 const blob=app.withMediaType(new Blob(['<svg/>']), 'figure.svg');
 assert.equal(blob.type,'image/svg+xml');
 app.state.token='SECRET_TEST_TOKEN';app.state.repo='gamesbyian/Glimpse';
 app.state.cache.set('private','data');app.treeAdd('private/folder');
 app.resetSession();
 assert.equal(app.state.token,'');assert.equal(app.state.repo,'');
 assert.equal(app.state.cache.size,0);assert.equal(app.state.tree.size,0);
 assert.equal(get('breadcrumbs').textContent,'No repository selected');
});
test('security invariants avoid persistent tokens and external scripts',()=>{
 assert.ok(!/localStorage\.setItem\([^)]*(?:token|pat|credential)/i.test(source));
 assert.ok(!/<script\s+[^>]*src=/i.test(html),'no remote script dependency');
 assert.ok(!/\beval\s*\(/.test(source),'no eval of remote file contents');
 assert.ok(html.includes('prefers-reduced-motion'));
});

test('pinned visual comparisons require two different images on the same repo and branch',()=>{
 const {app}=boot();
 app.state.repo='gamesbyian/Glimpse';app.state.branch='main';
 app.state.preview={name:'B.svg',path:'design/B.svg'};app.state.currentBlob=new Blob(['B']);
 app.state.pinned={item:{name:'A.svg',path:'design/A.svg'},blob:new Blob(['A']),repo:'gamesbyian/Glimpse',branch:'main'};
 assert.equal(app.compareReady(),true);
 app.state.preview={name:'A.svg',path:'design/A.svg'};assert.equal(app.compareReady(),false,'cannot compare file to itself');
 app.state.preview={name:'notes.md',path:'design/notes.md'};assert.equal(app.compareReady(),false,'only image compare');
 app.state.preview={name:'B.svg',path:'design/B.svg'};app.state.pinned.branch='other';assert.equal(app.compareReady(),false,'no cross-branch retained blob');
});
