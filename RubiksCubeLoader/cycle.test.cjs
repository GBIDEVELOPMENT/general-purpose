// Run: node --test RubiksCubeLoader/cycle.test.cjs
// Uses Node's built-in test runner and VM. No browser dependencies.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function harness(filename) {
  const html=fs.readFileSync(path.join(__dirname,filename),'utf8');
  const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
  assert.ok(script, 'standalone HTML has inline JS');
  const elements=new Map();
  class Node {
    constructor(){this.attrs={};this.listeners={};this.children=[];this.textContent='';this.value='';}
    setAttribute(k,v){this.attrs[k]=v;}
    append(node){this.children.push(node);}
    replaceChildren(...nodes){this.children=nodes;}
    addEventListener(k,fn){this.listeners[k]=fn;}
    removeEventListener(k){delete this.listeners[k];}
  }
  const doc={
    hidden:false,
    getElementById(id){if(!elements.has(id))elements.set(id,new Node());return elements.get(id);},
    createElementNS(){return new Node();},
    createDocumentFragment(){return new Node();},
    addEventListener(){},
    removeEventListener(){}
  };
  const raf=[];
  const context={
    document:doc,
    matchMedia:()=>({matches:false,addEventListener(){},removeEventListener(){}}),
    requestAnimationFrame(fn){raf.push(fn);return raf.length;},
    cancelAnimationFrame(){},
    IntersectionObserver:class{observe(){} disconnect(){}},
    console
  };
  context.window=context;
  vm.runInNewContext(script,context,{filename,timeout:5000});
  let now=0;
  function advance(milliseconds){
    const frames=Math.ceil(milliseconds/50);
    for(let i=0;i<frames;i++){
      now+=50;
      const cb=raf.shift();
      if(cb)cb(now);
    }
  }
  return {api:context.window?.rubiksLoader||context.rubiksLoader,advance,elements};
}
for(const file of ['index.html','small-cube.html']){
  test(file+' continuous cycle is genuinely solved at each transition',()=>{
    const h=harness(file);
    const a=h.api;
    assert.ok(a, 'public API available');
    a.start({mode:'cycle',seed:20261106,turnMs:200,scrambleLength:6});
    assert.equal(a.inspect().solved,false);
    // Start begins solving an already-scrambled cube.
    h.advance(6*200+50);
    assert.equal(a.inspect().phase,'scramble');
    assert.equal(a.inspect().solved,true);
    h.advance(6*200);
    assert.equal(a.inspect().phase,'solve');
    assert.equal(a.inspect().solved,false);
    h.advance(6*200);
    assert.equal(a.inspect().phase,'scramble');
    assert.equal(a.inspect().solved,true);
    assert.ok(a.inspect().cycles>=2);
    a.setPalette('original');
    assert.equal(a.inspect().solved,true,'palette changes do not alter state');
  });
}
