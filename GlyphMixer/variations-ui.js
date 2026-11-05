(function(){
"use strict";
const $=id=>document.getElementById(id);
const bridge=window.GlyphMixerBridge, V=window.GlyphMixerVariations;
if(!bridge||!V){console.error("Variations integration unavailable");return}
const state=()=>bridge.getState();
let editId=null,mode="alternate",worker=null,compiled=null,compiledFace=null,compiledUrl=null,compiledRevision=-1;
let busy=false,nextBuildId=0,activeId=null,activeRevision=-1;
function notice(text,bad=false){bridge.notice(text,bad)}
function el(tag,cls,text){
 const node=document.createElement(tag);
 if(cls)node.className=cls;
 if(text!==undefined)node.textContent=text;
 return node;
}
function setStatus(text,bad=false){
 const node=$("varBuildStatus");node.textContent=text;node.style.color=bad?"var(--bad)":"var(--muted)";
}
function freeCompiled(){
 if(compiledFace){try{document.fonts.delete(compiledFace)}catch{}}
 if(compiledUrl)URL.revokeObjectURL(compiledUrl);
 compiledFace=null;compiledUrl=null;compiled=null;compiledRevision=-1;
 $("varExport").disabled=true;
 $("varPlain").style.fontFamily="";
 $("varShaped").style.fontFamily="";
}
function changed(){
 state().version++;
 freeCompiled();
 setStatus("Rules changed. Build again to see actual OpenType behaviour.");
 render();
}
function sourceOptions(){
 const select=$("varSource");
 const selected=select.value;select.replaceChildren();
 for(const rec of state().fonts.values()){
  const opt=el("option","",rec.name);opt.value=rec.id;select.append(opt);
 }
 if(state().fonts.has(selected))select.value=selected;
 else if(state().fonts.size)select.value=[...state().fonts.keys()][0];
}
function adjustForm(){
 const lig=mode==="ligature";
 $("varTargetWrap").hidden=lig;
 $("varSequenceWrap").hidden=!lig;
 $("varAltOptions").hidden=lig;
 $("varLigatureOptions").hidden=!lig;
 const context=$("varContext").value;
 $("varBeforeWrap").hidden=lig||!(context==="before"||context==="both");
 $("varAfterWrap").hidden=lig||!(context==="after"||context==="both");
 const hint=lig?
  "Choose the outline to display for this sequence. Its original Unicode characters remain the stored text.":
  context==="repeat"?"A consecutive repeated letter will use a different glyph. Multiple alternates can cycle through a sequence.":
  context==="none"?"This alternate is selected by applications that enable its OpenType feature.":
  "This substitution applies when the neighboring text matches the characters you specify.";
 $("varHint").textContent=hint;
}
function editRule(rule){
 const isExisting=!!rule;
 editId=rule?.id||null;
 mode=rule?.kind||"alternate";
 $("varForm").hidden=false;
 $("varFormTitle").textContent=isExisting?"Edit variation":mode==="alternate"?"New alternate glyph":"New ligature";
 sourceOptions();
 if(rule&&state().fonts.has(rule.sourceId))$("varSource").value=rule.sourceId;
 else if(state().fonts.size>1){
  $("varSource").value=[...state().fonts.keys()].find(id=>id!==state().baseId)||state().baseId;
 }
 $("varTarget").value=rule?.kind==="alternate"?V.hex(rule.target):"n";
 $("varSequence").value=rule?.sequence||"th";
 $("varGlyph").value=rule?"#"+rule.glyphIndex:mode==="ligature"?"t":"n";
 $("varFeature").value=rule?.kind==="alternate"?rule.feature:"calt";
 $("varContext").value=rule?.context||"repeat";
 $("varBefore").value=rule?.before?String.fromCodePoint(rule.before):"o";
 $("varAfter").value=rule?.after?String.fromCodePoint(rule.after):"e";
 $("varLigatureFeature").value=rule?.kind==="ligature"?rule.feature:"liga";
 adjustForm();
 $("varForm").scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"instant":"smooth",block:"start"});
 $("varTarget").focus({preventScroll:true});
}
function closeEditor(){
 $("varForm").hidden=true; editId=null;
}
function glyphIndexFor(rec,input){
 const value=String(input||"").trim();
 if(value.startsWith("#")){
  if(!/^#\d+$/.test(value))throw Error("Use # followed by a glyph index.");
  const index=Number(value.slice(1));
  if(index<0||index>=rec.font.glyphs.length)throw Error("Source glyph index is outside this font.");
  return index;
 }
 const cp=V.point(value);
 if(cp===null)throw Error("Source glyph: enter a character, U+hex, or #index.");
 const cmap=window.GlyphMixerCore.glyphMappings(rec.font);
 const index=cmap.get(cp);
 if(index===undefined)throw Error(rec.name+" does not contain "+V.hex(cp)+".");
 return index;
}
function submitRule(event){
 event.preventDefault();
 const sourceId=$("varSource").value,rec=state().fonts.get(sourceId);
 if(!rec){notice("Add a source font first.",true);return}
 try{
  const glyphIndex=glyphIndexFor(rec,$("varGlyph").value);
  const rule={id:editId||"v"+Date.now().toString(36)+Math.random().toString(36).slice(2,8),
   kind:mode,sourceId,glyphIndex};
  if(mode==="alternate"){
   const cp=V.point($("varTarget").value);
   if(cp===null)throw Error("Choose a valid destination character or U+code.");
   if(!state().assignments.has(cp))throw Error("Destination "+V.hex(cp)+" is not in the character map. Add it on the Map tab first.");
   rule.target=cp;
   rule.feature=$("varFeature").value;
   rule.context=$("varContext").value;
   if(rule.context==="before"||rule.context==="both"){
    rule.before=V.point($("varBefore").value);
    if(rule.before===null)throw Error("Enter a valid previous letter.");
   }
   if(rule.context==="after"||rule.context==="both"){
    rule.after=V.point($("varAfter").value);
    if(rule.after===null)throw Error("Enter a valid following letter.");
   }
   if(rule.context==="before"||rule.context==="both"){
    if(!state().assignments.has(rule.before))throw Error("Previous character must exist in the destination map.");
   }
   if(rule.context==="after"||rule.context==="both"){
    if(!state().assignments.has(rule.after))throw Error("Following character must exist in the destination map.");
   }
  }else{
   rule.sequence=$("varSequence").value;
   rule.feature=$("varLigatureFeature").value;
   for(const c of rule.sequence){
    if(!state().assignments.has(c.codePointAt(0)))throw Error("Add every ligature character to the Map first: "+c);
   }
  }
  const next=state().variations.slice();
  const index=next.findIndex(x=>x.id===rule.id);
  if(index<0)next.push(rule);else next[index]=rule;
  V.validateRules(next,[...state().fonts.keys()],{mapped:new Set(state().assignments.keys())});
  state().variations=next;
  closeEditor(); changed();notice("OpenType rule saved.");
 }catch(error){notice(error.message,true)}
}
function render(){
 const rules=state().variations||[];
 const heading=$("varCount");
 heading.textContent=rules.length?rules.length+" rule"+(rules.length===1?"":"s"):"No variations yet";
 const list=$("varRuleList");list.replaceChildren();
 if(!rules.length){
  list.append(el("div","variation-empty","Try an alternate n for repeated nn, or make a decorative th ligature. Add as many alternatives as you like."));
  return;
 }
 for(const rule of rules){
  const source=state().fonts.get(rule.sourceId);
  const card=el("article","variation-rule");
  const canvas=el("canvas","");canvas.width=56;canvas.height=46;canvas.style.height="46px";canvas.style.width="56px";
  if(source)bridge.drawGlyph(canvas,rule.sourceId,rule.glyphIndex);
  const summary=el("div");
  summary.append(el("h3","",V.describeRule(rule)));
  summary.append(el("p","",(source?.name||"Missing source")+" · glyph #"+rule.glyphIndex));
  if(rule.kind==="alternate")summary.append(el("p","",V.hex(rule.target)+" · "+rule.feature+(rule.context!=="none"?" + calt":"")));
  else summary.append(el("p","","OpenType "+rule.feature));
  const actions=el("div","rule-buttons");
  const edit=el("button","button secondary","Edit");edit.type="button";edit.setAttribute("aria-label","Edit "+V.describeRule(rule));
  edit.onclick=()=>editRule(rule);
  const remove=el("button","button secondary","Remove");remove.type="button";remove.setAttribute("aria-label","Remove "+V.describeRule(rule));
  remove.onclick=()=>{
   state().variations=state().variations.filter(r=>r.id!==rule.id);
   changed();
  };
  actions.append(edit,remove);card.append(canvas,summary,actions);list.append(card);
 }
}
function drawProof(){
 const text=$("varProofText").value||" ";
 for(const id of ["varPlain","varShaped"])$(id).textContent=text;
 if(compiledFace){
  for(const id of ["varPlain","varShaped"])$(id).style.fontFamily='"GlyphMixerAdvanced",sans-serif';
 }
 $("varPlain").style.fontFeatureSettings='"calt" 0, "salt" 0, "rand" 0, "ss01" 0, "ss02" 0, "dlig" 0, "liga" 0';
 $("varShaped").style.fontFeatureSettings=[
  '"calt" '+Number($("varCaltEnabled").checked),
  '"ss01" '+Number($("varSs01Enabled").checked),
  '"ss02" '+Number($("varSs02Enabled").checked),
  '"dlig" '+Number($("varDligEnabled").checked),
  '"liga" 1'
 ].join(", ");
}
function setBusy(isBusy){
 busy=isBusy;
 $("varBuild").disabled=isBusy;
 $("varExport").disabled=isBusy||!compiled;
}
async function build(){
 if(busy)return;
 let data;
 try{
  data=V.buildRecipe({
   name:$("familyName").value,baseId:state().baseId,fonts:state().fonts,
   assignments:state().assignments,original:state().original,rules:state().variations
  });
 }catch(error){notice(error.message,true);setStatus(error.message,true);return}
 setBusy(true);freeCompiled();
 activeRevision=state().version;
 setStatus("Preparing local compilation…");
 const id=++nextBuildId;activeId=id;
 try{
  if(!worker){
   worker=new Worker("compiler-worker.js",{type:"module"});
   worker.addEventListener("message",async({data:msg})=>{
    if(msg.id!==activeId)return;
    if(msg.type==="status"){setStatus(msg.stage);return}
    if(msg.type==="error"){
      setStatus(msg.message,true);notice("Build failed: "+msg.message,true);setBusy(false);return;
    }
    if(msg.type==="built"){
      try{
       if(state().version!==activeRevision)throw Error("Project changed while building. Build the newer version.");
       const bytes=new Uint8Array(msg.bytes);
       const url=URL.createObjectURL(new Blob([bytes],{type:"font/ttf"}));
       let fontFace;
       try{
        fontFace=new FontFace("GlyphMixerAdvanced",'url("'+url+'")');
        await fontFace.load();
        document.fonts.add(fontFace);
       }catch(error){URL.revokeObjectURL(url);throw error}
       freeCompiled();compiled=bytes;compiledUrl=url;compiledFace=fontFace;compiledRevision=activeRevision;
       setStatus("Built "+msg.report.glyphs+" glyphs · "+msg.report.alternate_characters+" alternate characters · features: "+
         (msg.report.features.join(", ")||"none")+(msg.report.warnings.length?" · "+msg.report.warnings.length+" warnings":""));
       $("varExport").disabled=false;drawProof();
       notice("Real OpenType font built. Toggle its features to compare shaping.");
      }catch(error){setStatus(error.message,true);notice(error.message,true)}
      finally{setBusy(false)}
    }
   });
   worker.addEventListener("error",event=>{
    setStatus("Local compiler worker crashed: "+event.message,true);
    setBusy(false);
    worker?.terminate();worker=null;
   });
  }
  const payload=data.fontBytes.map(font=>({path:font.path,bytes:new Uint8Array(font.bytes).slice().buffer}));
  worker.postMessage({type:"build",id,recipe:data.recipe,fonts:payload},payload.map(item=>item.bytes));
 }catch(error){setStatus(error.message,true);setBusy(false);notice(error.message,true)}
}
async function exportCompiled(){
 if(!compiled||compiledRevision!==state().version){
  notice("Build the current project before exporting.",true);return;
 }
 try{
  const filename=window.GlyphMixerCore.slug($("familyName").value)+".ttf";
  await bridge.saveFile(()=>Promise.resolve(new Blob([compiled],{type:"font/ttf"})),
    filename,"ttf","font/ttf");
 }catch(error){notice("Export failed: "+error.message,true)}
}
function onProjectChanged(){
 closeEditor();
 freeCompiled();render();
 setStatus("Ready to compile. Source fonts stay on your device.");
 drawProof();
}
$("varNewAlternate").onclick=()=>editRule(null);
$("varNewLigature").onclick=()=>{editRule(null);mode="ligature";$("varFormTitle").textContent="New ligature";adjustForm();$("varSequence").focus()};
$("varCancel").onclick=closeEditor;
$("varForm").onsubmit=submitRule;
$("varContext").onchange=adjustForm;
$("varBuild").onclick=build;
$("varExport").onclick=exportCompiled;
$("varProofText").addEventListener("input",drawProof);
for(const id of ["varCaltEnabled","varSs01Enabled","varSs02Enabled","varDligEnabled"])$(id).addEventListener("change",drawProof);
bridge.setVariationHooks({render,onProjectChanged});
render();drawProof();
})();