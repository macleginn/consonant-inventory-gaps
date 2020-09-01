import json
from itertools import combinations
from collections import defaultdict
from typing import List, Dict
import pandas as pd
import query_lib as ql


def enumerate_triples(data_frame: pd.DataFrame, manners: List[str]) -> Dict[str, List[str]]:
    result = defaultdict(list)
    for gltc in data_frame.Glottocode.unique():
        table = data_frame.loc[data_frame.Glottocode == gltc]
        segments = list(table.Phoneme)
        stops = ql.get_manners(segments, manners)
        for triple in combinations(stops, 3):
            if len(list(ql.oppositions(triple, 'voice'))) == 1 and len(list(ql.oppositions(triple, 'place'))) == 1:
                a, b, c = triple
                plug_found = False
                for d in filter(lambda x: x not in triple, stops):
                    quadruple = a, b, c, d
                    if len(ql.oppositions(quadruple, 'voice')) == 2 and len(ql.oppositions(quadruple, 'place')) == 2:
                        plug_found = True
                        break
                if not plug_found:
                    result[f'/{" ".join(triple)}/'].append(gltc)
    return result


def compute_rankings(gap_fillers: Dict[str, List[str]]) -> pd.DataFrame:
    return pd.DataFrame.from_records(
        sorted(({k: len(v) for k, v in gap_fillers.items()}).items(), key=lambda x: x[1], reverse=True),
        columns=['phoneme', 'count']
    )


def load_json(path):
    with open(path, 'r', encoding='utf-8') as inp:
        return json.load(inp)


if __name__ == '__main__':
    # Load and clean-up data
    # data = pd.read_csv('phoible.csv')
    # data = data.loc[d.SegmentClass == 'consonant']
    # sample = ql.one_inventory_per_glottocode(data)
    # parsable_sample = set()
    # for inv_id in sample:
    #     inventory = list(data.loc[data.InventoryID == inv_id].Phoneme)
    #     if ql.all_segments_parsable(inventory):
    #         parsable_sample.add(inv_id)
    # data = data.loc[d.apply(lambda row: row.InventoryID in parsable_sample, axis=1)]
    # data.to_csv('phoible_working_sample.csv', index=False)
    # print(f'Sample size: {len(parsable_sample)}')

    data = pd.read_csv('phoible_working_sample.csv', low_memory=False)
    print(f'Sample size: {len(list(data.Glottocode.unique()))}')

    # First we identify gap-detecting triples using the same code and then associate
    # the triples with gap-filling segments by a combinations of exhaustive search
    # and manual checking. Otherwise we will overcount gaps in languages with
    # systems like
    #    t  k
    # b  d  g
    # because both /b d t/ and /b g k/ are gap-detecting triples.

    print('Processing stops...')
    with open('stop_gaps.json', 'w', encoding='utf-8') as out:
        json.dump(enumerate_triples(data, ['stop']), out, indent=2, ensure_ascii=False)
    print('Processing fricatives...')
    with open('fricative_gaps.json', 'w', encoding='utf-8') as out:
        json.dump(enumerate_triples(data, ['fricative']), out, indent=2, ensure_ascii=False)
    print('Processing affricates...')
    with open('affricate_gaps.json', 'w', encoding='utf-8') as out:
        json.dump(enumerate_triples(data, ['affricate']), out, indent=2, ensure_ascii=False)

    # Now run fill_gaps on all these files and correct manually if needed, then
    # run check_gap_fillers to make sure that all gaps are identified correctly.

    # Replace triples with actual missing segments for each file.
    with open('fricative_gaps_fillers.json', 'r', encoding='utf-8') as inp:
        affricate_gap_fillers = json.load(inp)
    with open('fricative_gaps.json', 'r', encoding='utf-8') as inp:
        affricate_triple_dict = json.load(inp)
    affricate_result = defaultdict(set)
    for k, v in affricate_triple_dict.items():
        key = affricate_gap_fillers[k]
        if key is not None:
            for gltc in v:
                affricate_result[key].add(gltc)
    with open('fricative_gaps_postprocessed.json', 'w', encoding='utf-8') as out:
        json.dump({k: sorted(v) for k,v in affricate_result.items()}, out, indent=2, ensure_ascii=False)

    # Compute statistics
    f_rankings = compute_rankings(load_json('fricative_gaps_postprocessed.json'))
    s_rankings = compute_rankings(load_json('stop_gaps_postprocessed.json'))
    a_rankings = compute_rankings(load_json('affricate_gaps_postprocessed.json'))
    all_rankings = pd.concat([f_rankings, s_rankings, a_rankings])
    all_rankings.sort_values(by='count', ascending=False, inplace=True)
    all_rankings.to_csv('stats.csv')
