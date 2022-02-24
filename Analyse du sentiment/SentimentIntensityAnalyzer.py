#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 17:32:04 2022

@author: user
"""
import math
from Constants import ConstantsClass
from TextAnalyzer import SentiText

import nltk.data


class SentimentIntensityAnalyzerClass:
    """
    Give a sentiment intensity score to sentences.
    """

    def __init__(self,lexicon_file="sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt",):
        self.lexicon_file = nltk.data.load(lexicon_file)
        self.lexicon = self.make_lex_dict()
        self.constants = ConstantsClass()


    def make_lex_dict(self):
        """
        Convert lexicon file to a dictionary
        """
        lex_dict = {}
        for line in self.lexicon_file.split("\n"):
            (word, measure) = line.strip().split("\t")[0:2]
            lex_dict[word] = float(measure)
        return lex_dict


    def polarity_scores(self, text):
        """
        Return a float for sentiment strength based on the input text.
        Positive values are positive valence, negative value are negative
        valence.
        """
        # text, words_and_emoticons, is_cap_diff = self.preprocess(text)
        sentitext = SentiText(
            text, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION
        )
        sentiments = []
        words_and_emoticons = sentitext.words_and_emoticons
        for item in words_and_emoticons:
            valence = 0
            i = words_and_emoticons.index(item)
            if (
                i < len(words_and_emoticons) - 1
                and item.lower() == "kind"
                and words_and_emoticons[i + 1].lower() == "of"
            ) or item.lower() in self.constants.BOOSTER_DICT:
                sentiments.append(valence)
                continue

            sentiments = self.sentiment_valence(valence, sentitext, item, i, sentiments)

        sentiments = self._but_check(words_and_emoticons, sentiments)

        return self.score_valence(sentiments, text)


    def sentiment_valence(self, valence, sentitext, item, i, sentiments):
        is_cap_diff = sentitext.is_cap_diff
        words_and_emoticons = sentitext.words_and_emoticons
        item_lowercase = item.lower()
        if item_lowercase in self.lexicon:
            # get the sentiment valence
            valence = self.lexicon[item_lowercase]

            # check if sentiment laden word is in ALL CAPS (while others aren't)
            if item.isupper() and is_cap_diff:
                if valence > 0:
                    valence += self.constants.C_INCR
                else:
                    valence -= self.constants.C_INCR

            for start_i in range(0, 3):
                if (
                    i > start_i
                    and words_and_emoticons[i - (start_i + 1)].lower()
                    not in self.lexicon
                ):
                    # dampen the scalar modifier of preceding words and emoticons
                    # (excluding the ones that immediately preceed the item) based
                    # on their distance from the current item.
                    s = self.constants.scalar_inc_dec(
                        words_and_emoticons[i - (start_i + 1)], valence, is_cap_diff
                    )
                    if start_i == 1 and s != 0:
                        s = s * 0.95
                    if start_i == 2 and s != 0:
                        s = s * 0.9
                    valence = valence + s
                    valence = self._never_check(
                        valence, words_and_emoticons, start_i, i
                    )
                    if start_i == 2:
                        valence = self._idioms_check(valence, words_and_emoticons, i)

                        # future work: consider other sentiment-laden idioms
                        # other_idioms =
                        # {"back handed": -2, "blow smoke": -2, "blowing smoke": -2,
                        #  "upper hand": 1, "break a leg": 2,
                        #  "cooking with gas": 2, "in the black": 2, "in the red": -2,
                        #  "on the ball": 2,"under the weather": -2}

            valence = self._least_check(valence, words_and_emoticons, i)

        sentiments.append(valence)
        return sentiments


    def _least_check(self, valence, words_and_emoticons, i):
        # check for negation case using "least"
        if (
            i > 1
            and words_and_emoticons[i - 1].lower() not in self.lexicon
            and words_and_emoticons[i - 1].lower() == "least"
        ):
            if (
                words_and_emoticons[i - 2].lower() != "at"
                and words_and_emoticons[i - 2].lower() != "very"
            ):
                valence = valence * self.constants.N_SCALAR
        elif (
            i > 0
            and words_and_emoticons[i - 1].lower() not in self.lexicon
            and words_and_emoticons[i - 1].lower() == "least"
        ):
            valence = valence * self.constants.N_SCALAR
        return valence

    def _but_check(self, words_and_emoticons, sentiments):
        words_and_emoticons = [w_e.lower() for w_e in words_and_emoticons]
        but = {"but"} & set(words_and_emoticons)
        if but:
            bi = words_and_emoticons.index(next(iter(but)))
            for sidx, sentiment in enumerate(sentiments):
                if sidx < bi:
                    sentiments[sidx] = sentiment * 0.5
                elif sidx > bi:
                    sentiments[sidx] = sentiment * 1.5
        return sentiments

    def _idioms_check(self, valence, words_and_emoticons, i):
        onezero = f"{words_and_emoticons[i - 1]} {words_and_emoticons[i]}"

        twoonezero = "{} {} {}".format(
            words_and_emoticons[i - 2],
            words_and_emoticons[i - 1],
            words_and_emoticons[i],
        )

        twoone = f"{words_and_emoticons[i - 2]} {words_and_emoticons[i - 1]}"

        threetwoone = "{} {} {}".format(
            words_and_emoticons[i - 3],
            words_and_emoticons[i - 2],
            words_and_emoticons[i - 1],
        )

        threetwo = "{} {}".format(
            words_and_emoticons[i - 3], words_and_emoticons[i - 2]
        )

        sequences = [onezero, twoonezero, twoone, threetwoone, threetwo]

        for seq in sequences:
            if seq in self.constants.SPECIAL_CASE_IDIOMS:
                valence = self.constants.SPECIAL_CASE_IDIOMS[seq]
                break

        if len(words_and_emoticons) - 1 > i:
            zeroone = f"{words_and_emoticons[i]} {words_and_emoticons[i + 1]}"
            if zeroone in self.constants.SPECIAL_CASE_IDIOMS:
                valence = self.constants.SPECIAL_CASE_IDIOMS[zeroone]
        if len(words_and_emoticons) - 1 > i + 1:
            zeroonetwo = "{} {} {}".format(
                words_and_emoticons[i],
                words_and_emoticons[i + 1],
                words_and_emoticons[i + 2],
            )
            if zeroonetwo in self.constants.SPECIAL_CASE_IDIOMS:
                valence = self.constants.SPECIAL_CASE_IDIOMS[zeroonetwo]

        # check for booster/dampener bi-grams such as 'sort of' or 'kind of'
        if (
            threetwo in self.constants.BOOSTER_DICT
            or twoone in self.constants.BOOSTER_DICT
        ):
            valence = valence + self.constants.B_DECR
        return valence

    def _never_check(self, valence, words_and_emoticons, start_i, i):
        if start_i == 0:
            if self.constants.negated([words_and_emoticons[i - 1]]):
                valence = valence * self.constants.N_SCALAR
        if start_i == 1:
            if words_and_emoticons[i - 2] == "never" and (
                words_and_emoticons[i - 1] == "so"
                or words_and_emoticons[i - 1] == "this"
            ):
                valence = valence * 1.5
            elif self.constants.negated([words_and_emoticons[i - (start_i + 1)]]):
                valence = valence * self.constants.N_SCALAR
        if start_i == 2:
            if (
                words_and_emoticons[i - 3] == "never"
                and (
                    words_and_emoticons[i - 2] == "so"
                    or words_and_emoticons[i - 2] == "this"
                )
                or (
                    words_and_emoticons[i - 1] == "so"
                    or words_and_emoticons[i - 1] == "this"
                )
            ):
                valence = valence * 1.25
            elif self.constants.negated([words_and_emoticons[i - (start_i + 1)]]):
                valence = valence * self.constants.N_SCALAR
        return valence

    def _punctuation_emphasis(self, sum_s, text):
        # add emphasis from exclamation points and question marks
        ep_amplifier = self._amplify_ep(text)
        qm_amplifier = self._amplify_qm(text)
        punct_emph_amplifier = ep_amplifier + qm_amplifier
        return punct_emph_amplifier

    def _amplify_ep(self, text):
        # check for added emphasis resulting from exclamation points (up to 4 of them)
        ep_count = text.count("!")
        if ep_count > 4:
            ep_count = 4
        # (empirically derived mean sentiment intensity rating increase for
        # exclamation points)
        ep_amplifier = ep_count * 0.292
        return ep_amplifier

    def _amplify_qm(self, text):
        # check for added emphasis resulting from question marks (2 or 3+)
        qm_count = text.count("?")
        qm_amplifier = 0
        if qm_count > 1:
            if qm_count <= 3:
                # (empirically derived mean sentiment intensity rating increase for
                # question marks)
                qm_amplifier = qm_count * 0.18
            else:
                qm_amplifier = 0.96
        return qm_amplifier

    def _sift_sentiment_scores(self, sentiments):
        # want separate positive versus negative sentiment scores
        pos_sum = 0.0
        neg_sum = 0.0
        neu_count = 0
        for sentiment_score in sentiments:
            if sentiment_score > 0:
                pos_sum += (
                    float(sentiment_score) + 1
                )  # compensates for neutral words that are counted as 1
            if sentiment_score < 0:
                neg_sum += (
                    float(sentiment_score) - 1
                )  # when used with math.fabs(), compensates for neutrals
            if sentiment_score == 0:
                neu_count += 1
        return pos_sum, neg_sum, neu_count

    def score_valence(self, sentiments, text):
        if sentiments:
            sum_s = float(sum(sentiments))
            # compute and add emphasis from punctuation in text
            punct_emph_amplifier = self._punctuation_emphasis(sum_s, text)
            if sum_s > 0:
                sum_s += punct_emph_amplifier
            elif sum_s < 0:
                sum_s -= punct_emph_amplifier

            compound = self.constants.normalize(sum_s)
            # discriminate between positive, negative and neutral sentiment scores
            pos_sum, neg_sum, neu_count = self._sift_sentiment_scores(sentiments)

            if pos_sum > math.fabs(neg_sum):
                pos_sum += punct_emph_amplifier
            elif pos_sum < math.fabs(neg_sum):
                neg_sum -= punct_emph_amplifier

            total = pos_sum + math.fabs(neg_sum) + neu_count
            pos = math.fabs(pos_sum / total)
            neg = math.fabs(neg_sum / total)
            neu = math.fabs(neu_count / total)

        else:
            compound = 0.0
            pos = 0.0
            neg = 0.0
            neu = 0.0

        sentiment_dict = {
            "neg": round(neg, 3),
            "neu": round(neu, 3),
            "pos": round(pos, 3),
            "compound": round(compound, 4),
        }

        return sentiment_dict


