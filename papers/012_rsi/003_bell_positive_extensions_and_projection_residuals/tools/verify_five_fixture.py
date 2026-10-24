"""Read-only binding of the rational certificate vectors to Lean integer data."""
from fractions import Fraction
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'data/five_setting_certificates.json').read_text())
source = (ROOT/'lean4/Bell/FiveData.lean').read_text(encoding='utf-8')


def array(name):
    matches = re.findall(r'^def '+name+r'\s.*:= !\[([^\]]+)\]$', source, re.M)
    if len(matches) != 1:
        raise ValueError('Missing or ambiguous Lean vector: '+name)
    return [int(x.strip()) for x in matches[0].split(',')]


for side, zname, xname in [(0, 'az', 'ax'), (1, 'bz', 'bx')]:
    expected = [[Fraction(z, 185), Fraction(x, 185)]
                for z, x in zip(array(zname), array(xname))]
    assert expected == [[Fraction(z), Fraction(x)] for z, x in data['directions'][side]]
for key, ids, values in [('q', 'qid', 'qn'), ('gamma', 'hid', 'hn')]:
    indices, numerators = array(ids), array(values)
    assert len(indices) == len(numerators) == len(set(indices))
    assert {str(i): Fraction(v, 136900) for i, v in zip(indices, numerators)} == {
        i: Fraction(v) for i, v in data[key].items()}
for key, name in [('cf_dual', 'y'), ('negative_dual', 'z')]:
    assert array(name) == [Fraction(data[key].get(str(i), '0')) for i in range(100)]
print('PASS exact Lean/Python binding: 10 directions and four certificate vectors')
