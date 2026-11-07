import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {resolve,dirname} from 'node:path';
import {IDBFactory} from 'fake-indexeddb';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const source=await readFile(resolve(root,'library.js'),'utf8');

function boot(factory){
 const window={indexedDB:factory};
 const globals={indexedDB:factory,window,Promise,Uint8Array,ArrayBuffer};
 const context=vm.createContext(globals);
 vm.runInContext(source,context,{filename:'library.js'});
 return vm.runInContext('FontLibrary',context);
}

test('font byte store and metadata commit together and survive a fresh app context',async()=>{
 const db=new IDBFactory(),lib=boot(db);
 await lib.open();
 const original=new Uint8Array([0,1,2,3,4]);
 const meta={id:'fs1',key:'sha-1',name:'Stencil Bold',familyName:'Stencil',hidden:false,tags:[],familyTags:[]};
 await lib.save(meta,original);
 original[1]=99;
 const data=await lib.get('data','fs1');
 assert.deepEqual([...new Uint8Array(data.bytes)],[0,1,2,3,4]);
 assert.equal((await lib.get('fonts','fs1')).hidden,false);

 const second=boot(db);
 assert.equal((await second.get('fonts','fs1')).name,'Stencil Bold');
 assert.deepEqual([...new Uint8Array((await second.get('data','fs1')).bytes)],[0,1,2,3,4]);
 await second.update({...meta,hidden:true,tags:['bold'],familyTags:['favourite']});
 assert.equal((await lib.get('fonts','fs1')).hidden,true);
 assert.deepEqual(Array.from((await lib.get('fonts','fs1')).familyTags),['favourite']);
 assert.deepEqual([...new Uint8Array((await lib.get('data','fs1')).bytes)],[0,1,2,3,4]);
});

test('failed metadata cloning does not leave orphaned bytes',async()=>{
 const lib=boot(new IDBFactory());
 await assert.rejects(lib.save({id:'broken',notCloneable:()=>42},new Uint8Array([1,2,3])));
 assert.equal(await lib.get('fonts','broken'),undefined);
 assert.equal(await lib.get('data','broken'),undefined);
});

test('lists keep stable face identities through hide and restore, deleting bytes is explicit',async()=>{
 const db=new IDBFactory(),lib=boot(db);
 for(const [id,name] of [['fs1','Family Bold'],['fs2','Family Regular'],['fs3','Other Face']]){
  await lib.save({id,name,hidden:false,tags:[],familyTags:[]},new Uint8Array([id.length,10]));
 }
 const list={id:'list1',title:'Favourite lettering',ids:['fs1','fs2']};
 await lib.saveList(list);
 await lib.update({id:'fs1',name:'Family Bold',hidden:true,tags:[],familyTags:[]});
 assert.deepEqual([...new Uint8Array((await lib.get('data','fs1')).bytes)],[3,10]);
 assert.deepEqual(Array.from((await lib.get('lists','list1')).ids),['fs1','fs2']);
 await lib.update({id:'fs1',name:'Family Bold',hidden:false,tags:[],familyTags:[]});
 assert.equal((await lib.get('fonts','fs1')).hidden,false);
 await lib.remove(['fs1','fs2']);
 assert.equal(await lib.get('fonts','fs1'),undefined);
 assert.equal(await lib.get('data','fs1'),undefined);
 assert.equal(await lib.get('fonts','fs2'),undefined);
 assert.equal(await lib.get('data','fs2'),undefined);
 assert.equal((await lib.get('fonts','fs3')).name,'Other Face');
 list.ids=[];
 await lib.saveList(list);
 assert.equal((await lib.get('lists','list1')).ids.length,0);
 await lib.removeList('list1');
 assert.equal(await lib.get('lists','list1'),undefined);
});

test('bulk writes and reads preserve independent font identities',async()=>{
 const lib=boot(new IDBFactory());
 const count=48;
 for(let i=0;i<count;i++)await lib.save({id:'fs'+i,name:'Glyph '+i,hidden:i%2===0},new Uint8Array([i]));
 assert.equal((await lib.all('fonts')).length,count);
 assert.equal((await lib.all('data')).length,count);
 await lib.remove(Array.from({length:count/2},(_,i)=>'fs'+(i*2)));
 assert.equal((await lib.all('fonts')).length,count/2);
 assert.equal((await lib.all('data')).length,count/2);
});
