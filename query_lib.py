from typing import List
from collections import defaultdict
from itertools import combinations
import pandas
from IPAParser_2_0 import parse_consonant


### Helpers ###


def congruent(f1, f2):
    if f1 == f2:
        return True
    if f1 < f2:
        ordered = (f1, f2)
    else:
        ordered = (f2, f1)
    if ordered in {
        ('bilabial', 'labio-dental'),
        ('alveolar', 'dental')
    }:
        return True
    return False


### Segment processing ###


def feature_difference(p1, p2):
    parse1 = parse_consonant(p1)
    parse2 = parse_consonant(p2)
    parse_differences = {}
    for k in parse1:
        if k == 'glyph':
            continue
        if parse1[k] != parse2[k]:
            parse_differences[k] = {
                'p1': parse1[k],
                'p2': parse2[k]
            }
    return parse_differences


### Inventory processing ###


def one_inventory_per_glottocode(d: pandas.DataFrame) -> List[int]:
    """
    Selects one inventory per glottocode from the table.
    Inventories with biggest InventoryIDs are selected.
    """
    codes_to_ids = defaultdict(set)
    for t in d.itertuples():
        codes_to_ids[t.Glottocode].add(t.InventoryID)
    return [max(v) for v in codes_to_ids.values()]


def get_inventory(data_frame, glottocode):
    return list(data_frame.loc[data_frame.Glottocode == glottocode].Phoneme)


def all_segments_parsable(inventory):
    for p in inventory:
        try:
            parse_consonant(p)
        except:
            return False
    return True


def get_manners(inventory, manners):
    return sorted(filter(
        lambda x: parse_consonant(x).get('manner', None) in manners,
        inventory
    ))


def get_voices(inventory, voices):
    return sorted(filter(
        lambda x: parse_consonant(x).get('voice', None) in voices,
        inventory
    ))


def voice_opp_in(inventory, manner):
    segs = get_manners(inventory, manner)
    opps = oppositions(segs, 'voice')
    if opps == {}:
        return False
    else:
        return opps


def oppositions(consonants, feature, others_same=True):
    """
    Returns pairs of consonants opposed by the value of
    a feature while values of all other features are kept
    fixed (default) or a free to vary.
    """
    results = {}
    for c1, c2 in combinations(consonants, 2):
        parse1 = parse_consonant(c1)
        parse2 = parse_consonant(c2)
        if feature not in parse1 or feature not in parse2:
            continue
        if parse1[feature] != parse2[feature]:
            if others_same:
                other_are_same = True
                for k in parse1:
                    if k == feature or k == 'glyph': 
                        continue
                    elif k in {
                        'additional articulations',
                        'pre-features'
                    }:
                        if sorted(parse1[k]) != sorted(parse2[k]):
                            other_are_same = False
                            break
                    else:
                        if not congruent(parse1[k], parse2[k]):
                            other_are_same = False
                            break
                if other_are_same:
                    results[(c1, c2)] = (parse1[feature], parse2[feature])
            else:
                results[(c1, c2)] = (parse1[feature], parse2[feature])
    return results