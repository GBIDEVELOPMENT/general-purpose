/* Font Shelf local library. Stored only in this app/browser origin. */
'use strict';
const FontLibrary=(()=>{
 const DATABASE='fontshelf-library',VERSION=1;
 let opened;
 function open(){
  if(!('indexedDB' in window))return Promise.reject(Error('IndexedDB is unavailable'));
  return opened??=new Promise((resolve,reject)=>{
   const request=indexedDB.open(DATABASE,VERSION);
   request.onupgradeneeded=()=>{
    const db=request.result;
    for(const store of ['fonts','data','lists'])if(!db.objectStoreNames.contains(store))db.createObjectStore(store,{keyPath:'id'});
   };
   request.onerror=()=>reject(request.error||Error('Cannot open font library'));
   request.onsuccess=()=>{const db=request.result;db.onversionchange=()=>db.close();resolve(db)};
  }).catch(error=>{opened=null;throw error});
 }
 async function operation(stores,mode,callback){
  const db=await open();
  return new Promise((resolve,reject)=>{
   const tx=db.transaction(stores,mode);
   let value;
   try{value=callback(tx)}catch(e){tx.abort();reject(e);return}
   tx.oncomplete=()=>resolve(value);
   tx.onabort=()=>reject(tx.error||Error('Library operation cancelled'));
   tx.onerror=()=>reject(tx.error||Error('Library storage error'));
  });
 }
 async function all(store){
  const db=await open();
  return new Promise((resolve,reject)=>{
   const request=db.transaction(store,'readonly').objectStore(store).getAll();
   request.onsuccess=()=>resolve(request.result);
   request.onerror=()=>reject(request.error||Error('Library read failed'));
  });
 }
 async function get(store,id){
  const db=await open();
  return new Promise((resolve,reject)=>{
   const request=db.transaction(store,'readonly').objectStore(store).get(id);
   request.onsuccess=()=>resolve(request.result);
   request.onerror=()=>reject(request.error||Error('Library read failed'));
  });
 }
 // Metadata and font bytes commit in one transaction. A failed quota write
 // cannot leave a phantom saved font without its data.
 function save(meta,bytes){
  return operation(['fonts','data'],'readwrite',tx=>{
   tx.objectStore('fonts').put(meta);
   tx.objectStore('data').put({id:meta.id,bytes:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)});
  });
 }
 function update(meta){return operation(['fonts'],'readwrite',tx=>tx.objectStore('fonts').put(meta))}
 function remove(ids){
  return operation(['fonts','data'],'readwrite',tx=>{
   for(const id of ids){tx.objectStore('fonts').delete(id);tx.objectStore('data').delete(id)}
  });
 }
 function saveList(list){return operation(['lists'],'readwrite',tx=>tx.objectStore('lists').put(list))}
 function removeList(id){return operation(['lists'],'readwrite',tx=>tx.objectStore('lists').delete(id))}
 return Object.freeze({open,all,get,save,update,remove,saveList,removeList});
})();
