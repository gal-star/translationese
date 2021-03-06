"""\
Implementation of Cohesive Markers hypothesis.

Origin: On the Features of Translationese, VV, NO & SW
        4.2 Explicitation, Cohesive Markers
"""

import nltk
from translationese.utils import sparse_dict_increment

COHESIVE_MARKERS = ["as for",
"as to",
"because",
"besides",
"but",
"consequently",
"despite",
"even if",
"even though",
"except",
"further",
"furthermore",
"hence",
"however",
"in addition",
"in conclusion",
"in other words",
"in spite",
"instead",
"is to say",
"maybe",
"moreover",
"nevertheless",
"on account of",
"on the contrary",
"on the other hand",
"otherwise",
"referring to",
"since",
"so",
"the former",
"the latter",
"therefore",
"this implies",
"though",
"thus",
"with reference to",
"with regard to",
"yet",
"concerning"]

def quantify(analysis):
    result = {}
    
    tokenized_markers = [(marker,nltk.word_tokenize(marker)) for marker in COHESIVE_MARKERS]
    text = analysis.tokens()
    
    for i, _ in enumerate(text):
        for (marker,tokenized) in tokenized_markers:
            if (tokenized == text[i:i+len(tokenized)]):
                sparse_dict_increment(result, marker)

    pairs = [ (marker, float(result[marker]) / len(text)) for marker in result.keys()]
    
    return dict(pairs)
