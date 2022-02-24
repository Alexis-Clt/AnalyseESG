#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 17:26:19 2022

@author: user
"""

import math
import re
import string

from nltk.util import pairwise


class ConstantsClass:
    """
    A class to keep lists and constants.
    """

    ##Constants##
    # (empirically derived mean sentiment intensity rating increase for booster words)
    B_INCR = 0.293
    B_DECR = -0.293

    # (empirically derived mean sentiment intensity rating increase for using
    # ALLCAPs to emphasize a word)
    C_INCR = 0.733

    N_SCALAR = -0.74

    NEGATE = {
        "aint",
        "arent",
        "cannot",
        "cant",
        "couldnt",
        "darent",
        "didnt",
        "doesnt",
        "ain't",
        "aren't",
        "can't",
        "couldn't",
        "daren't",
        "didn't",
        "doesn't",
        "dont",
        "hadnt",
        "hasnt",
        "havent",
        "isnt",
        "mightnt",
        "mustnt",
        "neither",
        "don't",
        "hadn't",
        "hasn't",
        "haven't",
        "isn't",
        "mightn't",
        "mustn't",
        "neednt",
        "needn't",
        "never",
        "none",
        "nope",
        "nor",
        "not",
        "nothing",
        "nowhere",
        "oughtnt",
        "shant",
        "shouldnt",
        "uhuh",
        "wasnt",
        "werent",
        "oughtn't",
        "shan't",
        "shouldn't",
        "uh-uh",
        "wasn't",
        "weren't",
        "without",
        "wont",
        "wouldnt",
        "won't",
        "wouldn't",
        "rarely",
        "seldom",
        "despite",
    }

    # booster/dampener 'intensifiers' or 'degree adverbs'
    # https://en.wiktionary.org/wiki/Category:English_degree_adverbs

    BOOSTER_DICT = {
        "absolutely": B_INCR,
        "amazingly": B_INCR,
        "awfully": B_INCR,
        "completely": B_INCR,
        "considerably": B_INCR,
        "decidedly": B_INCR,
        "deeply": B_INCR,
        "effing": B_INCR,
        "enormously": B_INCR,
        "entirely": B_INCR,
        "especially": B_INCR,
        "exceptionally": B_INCR,
        "extremely": B_INCR,
        "fabulously": B_INCR,
        "flipping": B_INCR,
        "flippin": B_INCR,
        "fricking": B_INCR,
        "frickin": B_INCR,
        "frigging": B_INCR,
        "friggin": B_INCR,
        "fully": B_INCR,
        "fucking": B_INCR,
        "greatly": B_INCR,
        "hella": B_INCR,
        "highly": B_INCR,
        "hugely": B_INCR,
        "incredibly": B_INCR,
        "intensely": B_INCR,
        "majorly": B_INCR,
        "more": B_INCR,
        "most": B_INCR,
        "particularly": B_INCR,
        "purely": B_INCR,
        "quite": B_INCR,
        "really": B_INCR,
        "remarkably": B_INCR,
        "so": B_INCR,
        "substantially": B_INCR,
        "thoroughly": B_INCR,
        "totally": B_INCR,
        "tremendously": B_INCR,
        "uber": B_INCR,
        "unbelievably": B_INCR,
        "unusually": B_INCR,
        "utterly": B_INCR,
        "very": B_INCR,
        "almost": B_DECR,
        "barely": B_DECR,
        "hardly": B_DECR,
        "just enough": B_DECR,
        "kind of": B_DECR,
        "kinda": B_DECR,
        "kindof": B_DECR,
        "kind-of": B_DECR,
        "less": B_DECR,
        "little": B_DECR,
        "marginally": B_DECR,
        "occasionally": B_DECR,
        "partly": B_DECR,
        "scarcely": B_DECR,
        "slightly": B_DECR,
        "somewhat": B_DECR,
        "sort of": B_DECR,
        "sorta": B_DECR,
        "sortof": B_DECR,
        "sort-of": B_DECR,
    }

    # check for special case idioms using a sentiment-laden keyword known to SAGE
    SPECIAL_CASE_IDIOMS = {
        "the shit": 3,
        "the bomb": 3,
        "bad ass": 1.5,
        "yeah right": -2,
        "cut the mustard": 2,
        "kiss of death": -1.5,
        "hand to mouth": -2,
    }

    # for removing punctuation
    REGEX_REMOVE_PUNCTUATION = re.compile(f"[{re.escape(string.punctuation)}]")

    PUNC_LIST = [
        ".",
        "!",
        "?",
        ",",
        ";",
        ":",
        "-",
        "'",
        '"',
        "!!",
        "!!!",
        "??",
        "???",
        "?!?",
        "!?!",
        "?!?!",
        "!?!?",
    ]

    def __init__(self):
        pass


    def negated(self, input_words, include_nt=True):
        """
        Determine if input contains negation words
        """
        neg_words = self.NEGATE
        if any(word.lower() in neg_words for word in input_words):
            return True
        if include_nt:
            if any("n't" in word.lower() for word in input_words):
                return True
        for first, second in pairwise(input_words):
            if second.lower() == "least" and first.lower() != "at":
                return True
        return False


    def normalize(self, score, alpha=15):
        """
        Normalize the score to be between -1 and 1 using an alpha that
        approximates the max expected value
        """
        norm_score = score / math.sqrt((score * score) + alpha)
        return norm_score


    def scalar_inc_dec(self, word, valence, is_cap_diff):
        """
        Check if the preceding words increase, decrease, or negate/nullify the
        valence
        """
        scalar = 0.0
        word_lower = word.lower()
        if word_lower in self.BOOSTER_DICT:
            scalar = self.BOOSTER_DICT[word_lower]
            if valence < 0:
                scalar *= -1
            # check if booster/dampener word is in ALLCAPS (while others aren't)
            if word.isupper() and is_cap_diff:
                if valence > 0:
                    scalar += self.C_INCR
                else:
                    scalar -= self.C_INCR
        return scalar