(function(root,factory){
  const api=factory();
  if(typeof module==="object" && module.exports) module.exports=api;
  else root.GlyphMixerVariations=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
const MAX_RULES=300, MAX_CODEPOINT=0x10ffff;
const GOOD_FEATURES=new Set(["aalt","salt","rand","ss01","ss02","calt"]);
const TYPES=new Set(["alternate","ligature"]);
const CONTEXTS=new Set(["none","repeat","before","after","both"]);
function point(value){
 if(typeof value==="number")return validPoint(value)?value:null;
 const text=String(value??"").trim();
 if(!text)return null;
 let cp=null;
 if(/^U\+[0-9A-F]{1,6}$/i.test(text))cp=parseInt(text.slice(2),16);
 else if(/^0x[0-9A-F]{1,6}$/i.test(text))cp=parseInt(text.slice(2),16);
 else if([...text].length===1)cp=text.codePointAt(0);
 return validPoint(cp)?cp:null;
}
function validPoint(cp){
 return Number.isInteger(cp)&&cp>0&&cp<=MAX_CODEPOINT
   && !(cp>=0xd800&&cp<=0xdfff) && !(cp>=0xfdd0&&cp<=0xfdef)
   && (cp&0xfffe)!==0xfffe;
}
function hex(cp){return "U+"+cp.toString(16).toUpperCase().padStart(4,"0")}
function describeRule(rule) {
 if(rule.kind==="ligature")return rule.sequence+" → glyph #"+rule.glyphIndex+" · "+rule.feature;
 const target=String.fromCodePoint(rule.target);
 if(rule.context==="repeat")return target+" · alternate when repeated";
 if(rule.context==="before")return target+" · after "+String.fromCodePoint(rule.before);
 if(rule.context==="after")return target+" · before "+String.fromCodePoint(rule.after);
 if(rule.context==="both")return target+" · between "+String.fromCodePoint(rule.before)+" and "+String.fromCodePoint(rule.after);
 return target+" · "+rule.feature+" alternate";
}
function validateRules(rules, sourceIds, options={}) {
 if(!Array.isArray(rules)||rules.length>MAX_RULES)throw Error("Variation project must contain at most 300 rules.");
 const ids=new Set(sourceIds), seen=new Set();
 const mapped=options.mapped instanceof Set?options.mapped:null;
 return rules.map((rule,index)=>{
  const where="Rule "+(index+1);
  if(!rule||typeof rule!=="object"||!TYPES.has(rule.kind)||
     typeof rule.id!=="string"||!/^v[a-z0-9_-]{1,40}$/i.test(rule.id)||seen.has(rule.id))
   throw Error(where+": invalid or duplicate rule ID.");
  seen.add(rule.id);
  if(!ids.has(rule.sourceId))throw Error(where+": source font is missing.");
  if(!Number.isInteger(rule.glyphIndex)||rule.glyphIndex<0||rule.glyphIndex>200000)
   throw Error(where+": source glyph index must be a nonnegative integer.");
  if(rule.kind==="ligature"){
   if(typeof rule.sequence!=="string"||[...rule.sequence].length<2||[...rule.sequence].length>8)
    throw Error(where+": ligature needs 2–8 characters.");
   if(rule.feature!=="liga" && rule.feature!=="dlig")throw Error(where+": choose liga or dlig.");
   for(const ch of rule.sequence)if(!validPoint(ch.codePointAt(0)))throw Error(where+": invalid ligature sequence.");
  }else{
   if(!validPoint(rule.target))throw Error(where+": destination character invalid.");
   if(mapped&&!mapped.has(rule.target))throw Error(where+": add the destination character to the map first.");
   if(!GOOD_FEATURES.has(rule.feature))throw Error(where+": invalid OpenType feature.");
   if(!CONTEXTS.has(rule.context))throw Error(where+": invalid context.");
   if((rule.context==="before"||rule.context==="both")&&!validPoint(rule.before))
    throw Error(where+": previous character missing.");
   if((rule.context==="after"||rule.context==="both")&&!validPoint(rule.after))
    throw Error(where+": following character missing.");
  }
  return {...rule};
 });
}
function safeSuffix(filename) {
 const match=/\.(ttf|otf|woff)$/i.exec(String(filename));
 return match?match[1].toLowerCase():"otf";
}
function assignedChanges(assignments,original) {
 return [...assignments].filter(([cp,ref])=>{
  const start=original.get(cp);
  return !start||ref.fontId!==start.fontId||ref.glyphIndex!==start.glyphIndex;
 }).sort(([a],[b])=>a-b);
}
function buildRecipe({name,baseId,fonts,assignments,original,rules}) {
 if(!fonts.has(baseId))throw Error("Choose a base font first.");
 const allIds=[...fonts.keys()];
 validateRules(rules,allIds,{mapped:new Set(assignments.keys())});
 const sources={};
 const fontBytes=[];
 for(const [id,rec] of fonts) {
  const path="GlyphMixer/browser-fonts/"+id+"."+safeSuffix(rec.filename);
  sources[id]={path};
  fontBytes.push({path,bytes:rec.bytes});
 }
 const operations=[];
 for(const [cp,ref] of assignedChanges(assignments,original)) {
  if(!fonts.has(ref.fontId))throw Error("A replacement source is missing.");
  operations.push({action:"reassign",source:ref.fontId,destination:hex(cp),glyph_index:ref.glyphIndex,strict:true});
 }
 for(const rule of rules) {
  const operation={action:rule.kind,source:rule.sourceId,glyph_index:rule.glyphIndex,strict:true};
  if(rule.kind==="ligature"){
   operation.sequence=rule.sequence;
   operation.feature=rule.feature;
  }else{
   operation.target=hex(rule.target);
   const features=[rule.feature];
   if(rule.context!=="none"&&!features.includes("calt"))features.push("calt");
   if(rule.feature==="rand"&&!features.includes("aalt"))features.push("aalt");
   operation.features=features;
   if(rule.context==="repeat")operation.context="adjacent-repeat";
   if(rule.context==="before")operation.context={preceded_by:hex(rule.before)};
   if(rule.context==="after")operation.context={followed_by:hex(rule.after)};
   if(rule.context==="both")operation.context={preceded_by:hex(rule.before),followed_by:hex(rule.after)};
  }
  operations.push(operation);
 }
 if(operations.length>300)throw Error("This project exceeds the 300-operation headless limit. Consolidate replacements into ranges.");
 const safeName=String(name||"Hybrid Font").trim().slice(0,100)||"Hybrid Font";
 return {recipe:{version:1,name:safeName,base:baseId,sources,operations,
   output:"GlyphMixer/build/advanced-preview.ttf"},fontBytes};
}
return {MAX_RULES,point,validPoint,hex,describeRule,validateRules,assignedChanges,buildRecipe};
});