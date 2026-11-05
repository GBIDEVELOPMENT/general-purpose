/* Glyph Mixer on-device OpenType compiler. Heavy Python/WASM work stays off the UI thread.
 * Only initialized when the user explicitly chooses Build & Preview.
 * Never uploads user fonts to a server. CDN requests fetch runtime/dependencies only.
 */
const PYODIDE_CDN="https://cdn.jsdelivr.net/pyodide/v0.29.5/full/";
let engine=null,ready=null,busy=false;
const report=(id,stage)=>self.postMessage({id,type:"status",stage});
async function ensureRuntime(id){
 if(ready)return ready;
 ready=(async()=>{
   report(id,"Loading the on-device Python engine (first build only)…");
   const {loadPyodide}=await import(PYODIDE_CDN+"pyodide.mjs");
   engine=await loadPyodide({indexURL:PYODIDE_CDN});
   report(id,"Installing the OpenType compiler…");
   await engine.loadPackage("micropip");
   await engine.runPythonAsync("import micropip\nawait micropip.install('fonttools==4.63.0', deps=False)");
   report(id,"Preparing the compiler…");
   engine.FS.mkdirTree("/workspace/GlyphMixer/headless");
   const source=await fetch(new URL("headless/cli.py",self.location.href),{cache:"force-cache"});
   if(!source.ok)throw Error("Cannot load headless compiler source.");
   engine.FS.writeFile("/workspace/GlyphMixer/headless/cli.py",await source.text());
   engine.runPython("import sys\nsys.path.insert(0, '/workspace')\nfrom GlyphMixer.headless.cli import build, root_path");
   return engine;
 })().catch(error=>{ready=null;engine=null;throw error});
 return ready;
}
self.onmessage=async({data})=>{
 if(!data||data.type!=="build"||busy)return;
 busy=true;
 const {id,recipe,fonts}=data;
 try {
   if(!recipe||!Array.isArray(fonts)||fonts.length>80)throw Error("Invalid compilation request.");
   const py=await ensureRuntime(id);
   py.FS.mkdirTree("/workspace/GlyphMixer/browser-fonts");
   py.FS.mkdirTree("/workspace/GlyphMixer/build");
   report(id,"Transferring source fonts into the local compiler…");
   for(const item of fonts){
     if(!/^GlyphMixer\/browser-fonts\/[a-zA-Z0-9_-]{1,48}\.(ttf|otf|woff)$/.test(item.path))
       throw Error("Invalid font path in browser recipe.");
     const bytes=new Uint8Array(item.bytes);
     if(bytes.byteLength>30*1024*1024)throw Error("Source exceeds 30 MB.");
     py.FS.writeFile("/workspace/"+item.path,bytes);
   }
   py.globals.set("glyph_recipe_json",JSON.stringify(recipe));
   report(id,"Building outlines and OpenType substitution tables…");
   py.runPython(
     "import json\n"+
     "glyph_build_report = build(json.loads(glyph_recipe_json), root_path('GlyphMixer/build/advanced-preview.ttf'))\n"+
     "glyph_build_json = json.dumps(glyph_build_report)"
   );
   const json=py.globals.get("glyph_build_json");
   const dataOut=py.FS.readFile("/workspace/GlyphMixer/build/advanced-preview.ttf");
   const owned=dataOut.slice();
   py.globals.delete("glyph_recipe_json");
   self.postMessage({id,type:"built",report:JSON.parse(json),bytes:owned.buffer},[owned.buffer]);
 }catch(error){
   self.postMessage({id,type:"error",message:String(error?.message||error)});
 }finally{busy=false}
};