import json
import pandas as pd
import query_lib as ql


def alveolar_dental(p1, p2):
    fd = ql.feature_difference(p1, p2)
    if len(fd) == 1 and 'place' in fd and sorted(
        [fd['place']['p1'], fd['place']['p2']]
    ) == ['alveolar', 'dental']:
        return True
    else:
        return False


def different(a, b, c, x):
    """
    Checks if the phoneme x is not too close
    to a, b, c to constitute a meaningful opposition.
    """
    if x in (a, b, c):
        return False
    if ql.feature_difference(a, x) == {} or ql.feature_difference(b, x) == {} or ql.feature_difference(c, x) == {}:
        return False
    if alveolar_dental(a, x) or alveolar_dental(b, x) or alveolar_dental(c, x):
        return False
    return True


if __name__ == '__main__':
    with open('fricative_gaps.json', 'r', encoding='utf-8') as inp:
        gaps = json.load(inp)
    d = pd.read_csv('phoible_working_sample.csv', low_memory=False)
    segments = list(d.Phoneme.unique())
    reference_segments = ql.get_manners(segments, ['fricative'])

    result = {}
    for key in gaps:
        a, b, c = key[1:-1].split()
        for d in filter(lambda x: different(a, b, c, x), reference_segments):
            quadruple = a, b, c, d
            opps_list_voice = list(ql.oppositions(quadruple, 'voice'))
            opps_list_place = list(ql.oppositions(quadruple, 'place'))
            if len(opps_list_voice) == 2 and len(opps_list_place) == 2:
                print(f'{key} -> {d}')
                result[key] = d
                break
        else:
            print(f'{key} cannot be filled.')
            result[key] = None
    with open('fricative_gaps_fillers.json', 'w', encoding='utf-8') as out:
        json.dump(result, out, indent=2, ensure_ascii=False)