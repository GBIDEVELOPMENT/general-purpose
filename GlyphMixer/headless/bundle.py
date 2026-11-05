"""Compile mobile .glyphmix project ZIP with embedded fonts using the shared engine."""
import json
import re
import tempfile
import zipfile
from pathlib import Path

MAX_MEMBERS=300
MAX_PROJECT_BYTES=160*1024*1024
MAX_FONT_BYTES=30*1024*1024

def compile_bundle(core, bundle_path, output=None):
    E=core.RecipeError
    root=core.ROOT
    bundle_path=core.root_path(str(bundle_path.relative_to(root)), must_exist=True)
    if bundle_path.stat().st_size>MAX_PROJECT_BYTES:
        raise E("Project exceeds 160 MB.")
    with zipfile.ZipFile(bundle_path) as archive:
        items=archive.infolist()
        names=[i.filename for i in items]
        if len(names)>MAX_MEMBERS or len(names)!=len(set(names)):
            raise E("Duplicate or excessive ZIP entries.")
        if sum(i.file_size for i in items)>MAX_PROJECT_BYTES:
            raise E("Unpacked project exceeds 160 MB.")
        if "project.json" not in names:
            raise E("Project manifest is missing.")
        manifest=json.loads(archive.read("project.json"))
        if not isinstance(manifest,dict) or manifest.get("version")!=1:
            raise E("Unsupported Glyph Mixer project.")
        entries=manifest.get("fonts")
        assignments=manifest.get("assignments")
        rules=manifest.get("variations",[])
        if not isinstance(entries,list) or not 1<=len(entries)<=80:
            raise E("Invalid font manifest.")
        if not isinstance(assignments,list) or len(assignments)>100000:
            raise E("Invalid assignment map.")
        if not isinstance(rules,list) or len(rules)>300:
            raise E("Invalid variation rule list.")
        folder_root=root/"GlyphMixer/build"
        folder_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="bundle-",dir=folder_root) as directory:
            path=Path(directory)
            sources={}
            fonts={}
            for entry in entries:
                if not isinstance(entry,dict):
                    raise E("Invalid embedded font.")
                alias,member=entry.get("id"),entry.get("file")
                if not isinstance(alias,str) or not core.VALID_SOURCE.fullmatch(alias) or alias in sources:
                    raise E("Invalid or duplicate font identifier.")
                if not isinstance(member,str) or not re.fullmatch(r"fonts/[A-Za-z0-9_.-]{1,80}",member):
                    raise E("Invalid embedded font path.")
                if member not in names or archive.getinfo(member).file_size>MAX_FONT_BYTES:
                    raise E("Embedded font missing or too large.")
                ext=Path(member).suffix.lower()
                if ext not in core.EXTENSIONS:
                    raise E("Unsupported embedded font format.")
                staged=path/(alias+ext)
                staged.write_bytes(archive.read(member))
                relative=str(staged.relative_to(root))
                sources[alias]={"path":relative}
                fonts[alias],_=core.open_font(sources[alias])
            base=manifest.get("baseId")
            if base not in sources:
                raise E("Project base font missing.")
            base_font=fonts[base]
            cmap=base_font.getBestCmap() or {}
            base_order=base_font.getGlyphOrder()
            operations=[]
            targets=set()
            for entry in assignments:
                if not isinstance(entry,list) or len(entry)!=2 or not isinstance(entry[1],dict):
                    raise E("Invalid assignment.")
                cp,ref=entry
                if not isinstance(cp,int) or cp<=0 or cp>0x10ffff or 0xd800<=cp<=0xdfff or cp in targets:
                    raise E("Duplicate or invalid codepoint.")
                targets.add(cp)
                alias,index=ref.get("fontId"),ref.get("glyphIndex")
                if alias not in fonts or not isinstance(index,int) or index<0 or index>=len(fonts[alias].getGlyphOrder()):
                    raise E("Invalid source glyph in assignment.")
                if alias==base and cmap.get(cp)==base_order[index]:
                    continue
                operations.append({"action":"reassign","source":alias,"destination":cp,
                                   "glyph_index":index,"strict":True})
            for rule in rules:
                if not isinstance(rule,dict):
                    raise E("Malformed variation rule.")
                alias,index=rule.get("sourceId"),rule.get("glyphIndex")
                if alias not in fonts or not isinstance(index,int) or index<0 or index>=len(fonts[alias].getGlyphOrder()):
                    raise E("Invalid glyph in variation rule.")
                op={"source":alias,"glyph_index":index,"strict":True}
                if rule.get("kind")=="ligature":
                    op.update(action="ligature",sequence=rule.get("sequence"),feature=rule.get("feature","liga"))
                elif rule.get("kind")=="alternate":
                    cp=rule.get("target")
                    if cp not in targets:
                        raise E("Variation destination absent from character map.")
                    feature=rule.get("feature","aalt")
                    features=[feature]
                    context=rule.get("context","none")
                    if context!="none":
                        features.append("calt")
                    if feature=="rand":
                        features.append("aalt")
                    op.update(action="alternate",target=cp,features=list(dict.fromkeys(features)))
                    if context=="repeat":
                        op["context"]="adjacent-repeat"
                    elif context in ("before","after","both"):
                        context_def={}
                        if context in ("before","both"):
                            context_def["preceded_by"]=rule.get("before")
                        if context in ("after","both"):
                            context_def["followed_by"]=rule.get("after")
                        op["context"]=context_def
                    elif context!="none":
                        raise E("Invalid variation context.")
                else:
                    raise E("Unknown variation type.")
                operations.append(op)
            for source in fonts.values():
                source.close()
            if len(operations)>300:
                raise E("Project exceeds 300 headless operations; consolidate mappings.")
            family=manifest.get("name") or "Glyph Mixer Hybrid"
            recipe={"version":1,"name":family,"base":base,
                    "sources":sources,"operations":operations}
            if output is None:
                output=core.root_path("GlyphMixer/build/"+core.safe_name(family)+".ttf")
            result=core.build(recipe,output)
            result["mobile_project"]=str(bundle_path.relative_to(root))
            output.with_suffix(".report.json").write_text(
                json.dumps(result,indent=2,ensure_ascii=False)+"\n")
            return result
