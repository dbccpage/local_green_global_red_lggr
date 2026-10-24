from pathlib import Path
import fitz, json
root=Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\012_rsi\000_relational_reasoning_and_rsi_impossibility')
work=Path(__file__).parent
p=root/'relational_reasoning_and_rsi_impossibility_monograph.pdf'
with fitz.open(p) as doc:
    selected={0}
    for i,page in enumerate(doc):
        if 'What the earlier finite RSI theorem' in page.get_text(): selected.add(i)
        if 'HiGHS supplies' in page.get_text(): selected.add(i)
    for i in sorted(selected):
        doc[i].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(work/f'paper_page_{i+1}.png')
    print(json.dumps({'pages':len(doc),'inspected_pages':[i+1 for i in sorted(selected)]}))
