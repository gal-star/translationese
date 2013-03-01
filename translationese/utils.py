"""Various utilities for translationese analysis"""

def output_filter_ngram(ngram):
    """Returns the ngram in a form suitable for ARFF output.

    >>> output_filter_ngram(('a','b','c'))
    'a b c'
    """
    return " ".join(ngram)

def flatten_list(l):
    """Returns a flat list given a list of lists.

    >>> flatten_list([[1,2],[3,4],[5,6]])
    [1, 2, 3, 4, 5, 6]
    """

    return [ item for sublist in l for item in sublist ]

def is_proper_noun(token_tag_pair):
    """Given a pair of a token and a tag, returns True if it represents a
    proper noun.

    >>> import nltk
    >>> nltk.pos_tag(nltk.word_tokenize("Impressive! John defeated Jim!"))
    ... # doctest: +NORMALIZE_WHITESPACE
    [('Impressive', 'JJ'), ('!', 'NN'), ('John', 'NNP'), ('defeated', 'VBD'),
    ('Jim', 'NNP'), ('!', '.')]
    >>> is_proper_noun(('Impressive', 'JJ'))
    False
    >>> is_proper_noun(('John', 'NNP'))
    True
    """

    token, tag = token_tag_pair
    return tag.startswith("NNP")
