"""Render the canonical Bell manuscript with its source digest."""
from pathlib import Path
import hashlib,os,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];STEM=ROOT.name
md=ROOT/(STEM+".md")
source=md.read_text(encoding="utf-8")
header,body=source.split("</div>",1)
if not header.startswith('<div align="center">'):
    raise ValueError("The manuscript must start with its centered title block")
def field(pattern):
    match=re.search(pattern,header,re.M)
    if not match:raise ValueError("Missing title-block field: "+pattern)
    return match.group(1).strip()
title=field(r'^# (.+)$');subtitle=field(r'^### (.+)$')
author=field(r'^\*\*Author:\*\* (.+)$')
date=field(r'^\*\*Date:\*\* (.+)$');version=field(r'^\*\*Version:\*\* (.+)$')
def tex_escape(value):
    escapes={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$',
             '#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}',
             '^':r'\textasciicircum{}'}
    return ''.join(escapes.get(c,c) for c in value)
title_block='\n'.join([r'\begin{center}',
    r'{\LARGE\bfseries '+tex_escape(title)+r'\par}',r'\vspace{0.6em}',
    r'{\large '+tex_escape(subtitle)+r'\par}',r'\vspace{1em}',
    tex_escape(author)+r'\par',tex_escape(date)+r'\par',
    r'\textbf{Version:} '+tex_escape(version)+r'\par',r'\end{center}'])
with tempfile.TemporaryDirectory(prefix="bell-pdf-") as td:
    w=Path(td);tex=w/(STEM+".tex")
    render_source=w/'body.md';render_source.write_text(body,encoding='utf-8')
    subprocess.run(["pandoc",str(render_source),"-s","--from","markdown+tex_math_dollars+tex_math_single_backslash","--to","latex","--no-highlight","--wrap","preserve","--include-in-header",str(ROOT/"scripts/preamble.tex"),"-V","geometry:margin=1in","-o",str(tex)],check=True)
    text=tex.read_text(encoding="utf-8");marker="manuscript-sha256:"+hashlib.sha256(md.read_bytes()).hexdigest()
    text=text.replace("\\begin{document}","\\hypersetup{pdftitle={"+tex_escape(title)+"},pdfsubject={"+marker+"}}\n\\begin{document}\n"+title_block)
    tex.write_text(text,encoding="utf-8")
    env=dict(os.environ,SOURCE_DATE_EPOCH="1792800000",FORCE_SOURCE_DATE="1")
    for _ in range(3):
        cp=subprocess.run(["xelatex","-interaction=nonstopmode","-halt-on-error",tex.name],cwd=w,env=env,capture_output=True)
        if cp.returncode:raise RuntimeError(cp.stdout.decode("utf-8",errors="replace"))
    log=(w/(STEM+".log")).read_text(encoding="utf-8",errors="replace")
    if "Missing character:" in log:raise RuntimeError("PDF has a missing glyph")
    if "Overfull " in log:raise RuntimeError("PDF has an overfull box; inspect the layout before release")
    target=ROOT/"docs/pdf_build.log";pending=target.with_name(target.name+".writing")
    pending.write_text(log,encoding="utf-8");os.replace(pending,target)
    for suffix in [".tex",".pdf",".log",".aux"] + ([".toc"] if (w/(STEM+".toc")).exists() else []):
        target=ROOT/(STEM+suffix);temp=target.with_suffix(suffix+".writing");shutil.copyfile(w/(STEM+suffix),temp);os.replace(temp,target)
print("PASS rendered source-bound Bell PDF and TeX")
