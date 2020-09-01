import json
import sys
import query_lib as ql

with open('affricate_gaps_fillers.json', 'r', encoding='utf-8') as inp:
    gap_fillers = json.load(inp)

for k, x in gap_fillers.items():
    if x is None:
        continue
    a, b, c = k[1:-1].split()
    quadruple = a, b, c, x
    print(quadruple)
    if not len(ql.oppositions(quadruple, 'voice')) == 2 and len(ql.oppositions(quadruple, 'place')) == 2:
        sys.exit(1)