from pathlib import Path
import fitz,json
root=Path.cwd()
out=Path(r'C:\Users\a343o\.codex\visualizations\2026\10\21\01a15f49-0b77-7152-8513-136fd3bd1071\contextual_review_20261023')
doc=fitz.open(root/'contextual_prediction_monograph.pdf')
selected={0}
for i,page in enumerate(doc):
    if 'Version 1.8.3 repairs' in page.get_text() or 'process termination' in page.get_text(): selected.add(i)
for i in sorted(selected):
    doc[i].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(out/f'pdf_page_{i+1}.png')
print(json.dumps({'pages':len(doc),'preview_pages':[i+1 for i in sorted(selected)]}))
