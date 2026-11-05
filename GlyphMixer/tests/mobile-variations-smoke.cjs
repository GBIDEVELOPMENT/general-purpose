/* Targeted Chromium mobile acceptance. Run after npm install --no-save playwright. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
async function main(){
 const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
 const page=await browser.newPage({
  viewport:{width:412,height:892},deviceScaleFactor:2.6,
  isMobile:true,hasTouch:true,acceptDownloads:true
 });
 const errors=[];
 page.on('pageerror',err=>errors.push(err.message));
 page.on('console',message=>{if(message.type()==='error')errors.push(message.text())});
 await page.addInitScript(()=>{
   try{Object.defineProperty(window,'showSaveFilePicker',{configurable:true,value:undefined})}catch{}
 });
 try{
   await page.goto('http://127.0.0.1:8765/GlyphMixer/',{waitUntil:'domcontentloaded',timeout:30000});
   await page.locator('#baseFiles').setInputFiles('GlyphMixer/test-fonts/Unkempt.zip');
   await page.locator('#workspace').waitFor({state:'visible',timeout:45000});
   const baseCount=await page.evaluate(()=>window.GlyphMixerBridge.getState().fonts.size);
   await page.locator('#sourceFiles').setInputFiles('GlyphMixer/test-fonts/besty.zip');
   await page.waitForFunction(count=>window.GlyphMixerBridge?.getState().fonts.size>count && !window.GlyphMixerBridge.getState().busy,baseCount,{timeout:45000});
   await page.locator('[data-tab="variations"]').click();
   await page.locator('#varNewAlternate').click();
   await page.locator('#varTarget').fill('n');
   await page.locator('#varSource').selectOption({index:(await page.locator('#varSource option').count())-1});
   await page.locator('#varGlyph').fill('n');
   await page.locator('#varFeature').selectOption('calt');
   await page.locator('#varContext').selectOption('repeat');
   await page.locator('#varSaveRule').click();
   assert.equal(await page.locator('.variation-rule').count(),1);
   const state=await page.evaluate(()=>({
     rules:window.GlyphMixerBridge.getState().variations,
     sources:window.GlyphMixerBridge.getState().fonts.size,
     width:document.documentElement.scrollWidth,viewport:innerWidth
   }));
   assert.equal(state.rules[0].target,110);
   assert.ok(state.sources>baseCount);
   assert.ok(state.width<=state.viewport+2,"Mobile screen has unexpected horizontal overflow.");
   const [download]=await Promise.all([
     page.waitForEvent('download',{timeout:15000}),
     page.locator('#saveProject').click()
   ]);
   const filename=await download.suggestedFilename();
   assert.ok(filename.endsWith('.glyphmix'),filename);
   const dir=fs.mkdtempSync(path.join(os.tmpdir(),'glyphmixer-mobile-'));
   const bundle=path.join(dir,filename);
   await download.saveAs(bundle);
   assert.ok(fs.statSync(bundle).size>100000);
   // Compile in a Web Worker through the genuine fontTools engine.
   await page.locator('#varBuild').click();
   await page.locator('#varExport').waitFor({state:'visible'});
   await page.waitForFunction(()=>!document.querySelector('#varExport').disabled, null,{timeout:180000});
   const compiled=await page.evaluate(()=>({
     fontLoaded:document.fonts.check('24px "GlyphMixerAdvanced"'),
     status:document.querySelector('#varBuildStatus').textContent,
     css:getComputedStyle(document.querySelector('#varShaped')).fontFeatureSettings,
     font:getComputedStyle(document.querySelector('#varShaped')).fontFamily
   }));
   assert.ok(compiled.fontLoaded);
   assert.match(compiled.status,/Built [0-9]+ glyphs/);
   assert.match(compiled.css,/calt/);
   assert.match(compiled.font,/GlyphMixerAdvanced/);
   // Verify real browser shaping: GSUB must alter the second n in nn.
   await page.locator('#varProofText').fill('nn');
   // Sample the SAME element before and after toggling. Comparing different
   // elements confounds glyph differences with subpixel raster alignment.
   await page.locator('#varCaltEnabled').uncheck();
   const without=await page.locator('#varShaped').screenshot();
   await page.locator('#varCaltEnabled').check();
   const withContext=await page.locator('#varShaped').screenshot();
   assert.ok(!without.equals(withContext),'Native browser shaping must visibly substitute contextual glyph');
   await page.locator('#varCaltEnabled').uncheck();
   const offAgain=await page.locator('#varShaped').screenshot();
   assert.ok(without.equals(offAgain),'Disabling calt must restore the initial pixels on the same element');
   await page.locator('#varCaltEnabled').check();
   fs.mkdirSync('GlyphMixer/build',{recursive:true});
   await page.screenshot({path:'GlyphMixer/build/mobile-variations-compiled.png',fullPage:true});
   // Reload to prove project save/open restores original bytes and rules from disk.
   await page.reload({waitUntil:'domcontentloaded'});
   await page.locator('#projectFile').setInputFiles(bundle);
   await page.waitForFunction(count=>window.GlyphMixerBridge.getState().variations.length===1 &&
     window.GlyphMixerBridge.getState().fonts.size===count,state.sources,{timeout:45000});
   const restored=await page.evaluate(()=>window.GlyphMixerBridge.getState().variations[0]);
   assert.equal(restored.target,110);
   assert.equal(restored.context,'repeat');
   fs.mkdirSync('GlyphMixer/build',{recursive:true});
   await page.locator('[data-tab="variations"]').click();
   await page.screenshot({path:'GlyphMixer/build/mobile-variations-smoke.png',fullPage:true});
   if(errors.length)console.log('Browser console observations:',errors.slice(0,8));
   console.log(JSON.stringify({ok:true,projectBytes:fs.statSync(bundle).size,rule:restored,
     compilation:compiled,sources:state.sources,viewport:state.viewport},null,2));
 }finally{await browser.close()}
}
main().catch(err=>{console.error(err);process.exitCode=1});
