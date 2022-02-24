#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 17:33:33 2022

@author: user
"""

from itertools import product

class SentiText:
    """
    Identify sentiment-relevant string-level properties of input text.
    """

    def __init__(self, text, punc_list, regex_remove_punctuation):
        if not isinstance(text, str):
            text = str(text.encode("utf-8"))
        self.text = text
        self.PUNC_LIST = punc_list
        self.REGEX_REMOVE_PUNCTUATION = regex_remove_punctuation
        self.words_and_emoticons = self._words_and_emoticons()
        # doesn't separate words from
        # adjacent punctuation (keeps emoticons & contractions)
        self.is_cap_diff = self.allcap_differential(self.words_and_emoticons)


    def _words_plus_punc(self):
        """
        Returns mapping of form:
        {
            'cat,': 'cat',
            ',cat': 'cat',
        }
        """
        no_punc_text = self.REGEX_REMOVE_PUNCTUATION.sub("", self.text)
        # removes punctuation (but loses emoticons & contractions)
        words_only = no_punc_text.split()
        # remove singletons
        words_only = {w for w in words_only if len(w) > 1}
        # the product gives ('cat', ',') and (',', 'cat')
        punc_before = {"".join(p): p[1] for p in product(self.PUNC_LIST, words_only)}
        punc_after = {"".join(p): p[0] for p in product(words_only, self.PUNC_LIST)}
        words_punc_dict = punc_before
        words_punc_dict.update(punc_after)
        return words_punc_dict

    def _words_and_emoticons(self):
        """
        Removes leading and trailing puncutation
        Leaves contractions and most emoticons
            Does not preserve punc-plus-letter emoticons (e.g. :D)
        """
        wes = self.text.split()
        words_punc_dict = self._words_plus_punc()
        wes = [we for we in wes if len(we) > 1]
        for i, we in enumerate(wes):
            if we in words_punc_dict:
                wes[i] = words_punc_dict[we]
        return wes

    def allcap_differential(self, words):
        """
        Check whether just some words in the input are ALL CAPS

        :param list words: The words to inspect
        :returns: `True` if some but not all items in `words` are ALL CAPS
        """
        is_different = False
        allcap_words = 0
        for word in words:
            if word.isupper():
                allcap_words += 1
        cap_differential = len(words) - allcap_words
        if 0 < cap_differential < len(words):
            is_different = True
        return is_different