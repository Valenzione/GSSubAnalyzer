import codecs
import json
import random
import string

from datetime import datetime, timedelta
import enchant
import nltk
import re

import threading

import time
from nltk.stem.wordnet import WordNetLemmatizer

# Symbol	Meaning	        Example
# S	        sentence	    the man walked
# NP	    noun phrase	    a dog
# VP	    verb phrase	    saw a park
# PP	    prepositional   phrase	with a telescope
# Det	    determiner	    the
# N	        noun	        dog
# V	        verb	        walked
# P	        preposition	    in
import text_extractor
import word_info

'''
Following code get parsed srt files as input and produces a set of candidate words for
lexical analysis.
1.Tokenize and POS-tag words.
2.Check for POS and spelling. Produce set of candidate words from this.
3.Get result from Entity Extractor and remove those items from set of candidate words
'''
candidate_pos = ('VBD', 'VBG', 'VB', 'RB', 'JJS', 'RBR', 'NN', 'NNS', 'VBZ', 'VBP')
persons = []  # list with person names.
spell_checker = enchant.Dict("en_US")  # Check spelling and eliminate all wrong spelled words

final_entities = set()


# def jsonify(final_words):
#     result_list = list()
#     for x in final_words:
#         dict_record = dict()
#         dict_record['word'] = x[0]
#         dict_record['lemma'] = x[1]
#         dict_record['pos'] = x[2]
#         dict_record['start_time'] = str(x[3].total_seconds()*1000)
#         dict_record['end_time'] = str(x[4].total_seconds()*1000)
#         dict_record['translation'] = word_info.get_translation(x[1])
#         dict_record['definition'] = word_info.get_defenition(x[1], x[2])
#         dict_record['example'] = word_info.get_example(x[1])
#         result_list.append(dict_record)
#     return json.dumps(result_list)


def extract_words(filename, word_num_to_ex, difficulty):
    subtitle_reader = codecs.open('uploads/' + filename, "r", encoding='utf-8', errors='ignore')
    raw_subtitle = subtitle_reader.read().splitlines()
    parsed_sentences = text_extractor.parseSRT(raw_subtitle)
    sub_text = ''.join(str(elem) for elem in parsed_sentences)
    words_data, lemmed_words = rough_result_set(sub_text)
    lemmed_words = remove_basic_words(lemmed_words)
    lemmed_words = remove_top_american(lemmed_words)
    lemmed_words = remove_tier(lemmed_words, difficulty * 2)
    words_data = [record for record in words_data if record[1] in lemmed_words]
    timed_words_data = get_timedelta(words_data, raw_subtitle)
    print("Timed words: ", len(timed_words_data), "Words: ", len(words_data), "Unique lemmas:", len(lemmed_words))
    mltest = open("mltest.txt", "a+")
    mltest.write(str(words_data))
    mltest.close()
    if (len(lemmed_words) < word_num_to_ex):
        word_num_to_ex = len(lemmed_words) // 2

    last_wordtime = timed_words_data[::-1][0][4]
    first_wordtime = timed_words_data[0][4]

    time_delta = (last_wordtime - first_wordtime) / word_num_to_ex
    borders = list()
    border = first_wordtime

    for x in range(0, word_num_to_ex):
        border += time_delta
        borders.append(border)

    print(borders)

    timeline = list()
    for x in borders:
        borderlist = list()
        for w in timed_words_data:
            wordtime = w[4]
            if wordtime <= x:
                timed_words_data.remove(w)
                borderlist.append(w)
            else:
                timeline.append(borderlist)
                break
    timeline.append(borderlist)

    final_words = list()

    for x in timeline:
        if x:
            final_words.append(random.choice(x))

    return final_words


def get_timedelta(words_data, raw_subtitle):
    timed_words_data = list()
    subtitle_blocks = text_extractor.extractBlocks(raw_subtitle)
    translator = str.maketrans({key: " " for key in string.punctuation})

    duplicates = list()

    for block in subtitle_blocks[1:]:
        block[2] = re.sub("<[^>]*>", "", block[2])
        block[2] = block[2].translate(translator)

        for record in words_data:
            if (record[0] in block[2].split(" ")):
                block[2] = block[2].replace(record[0], "", 1)
                tuple_list = list(record)
                time_from, time_to = block[1][0:29].split(" --> ")

                time_from = datetime.strptime(time_from, "%H:%M:%S.%f")
                time_from = timedelta(hours=time_from.hour, minutes=time_from.minute,
                                      seconds=time_from.second)

                time_to = datetime.strptime(time_to, "%H:%M:%S.%f")
                time_to = timedelta(hours=time_to.hour, minutes=time_to.minute,
                                    seconds=time_to.second)

                tuple_list.append(time_from)
                tuple_list.append(time_to)
                record = tuple(tuple_list)

                for item in timed_words_data:
                    iteml = list(item)[:3]
                    if iteml == tuple_list[:3]:
                        duplicates.append(record)
                        break
                timed_words_data.append(record)

    for itemt in timed_words_data:
        for item in duplicates:
            if (item[:2] == itemt[:2]):
                if (item in timed_words_data):
                    timed_words_data.remove(item)

    return timed_words_data


def rough_result_set(subtitle_text):
    result_list = list()  # list with candidate words
    lemmatizer = WordNetLemmatizer()
    lemmed_set = set()
    tokens = nltk.word_tokenize(subtitle_text)  # Create tokens from text

    names = codecs.open('dictionaries/allNames', "r", encoding='utf-8', errors='ignore').read().splitlines()

    tagged = nltk.pos_tag(tokens)  # Detect POS for each token

    # If spell check is passed and POS is one of the candidate POS's, then append it to result list.
    for tag_tuple in tagged:
        for pos in candidate_pos:
            if (tag_tuple[1] == pos):
                new_word = tag_tuple[0].lower()

                if (tag_tuple[1] in ('VBD', 'VBG', 'VBP', 'VB', 'VBZ')):
                    new_word = lemmatizer.lemmatize(tag_tuple[0], 'v')
                if (tag_tuple[1] in ('NN', 'NNS')):
                    new_word = lemmatizer.lemmatize(tag_tuple[0], 'n')

                # remove names
                if tag_tuple[0].lower() in names or new_word.lower() in names:
                    continue

                if (spell_checker.check(new_word)) and len(new_word) > 2 and spell_checker.check(tag_tuple[0]):
                    result_list.append((tag_tuple[0], new_word.lower(), tag_tuple[1]))
                    lemmed_set.add(new_word.lower())

    # remove 10% of most popular tokens
    fdist = nltk.FreqDist(tokens)
    for x in fdist.most_common(len(tokens) // 10):
        for item in result_list:
            if item[0] == x:
                result_list.remove(item)
                if item[1] in lemmed_set:
                    lemmed_set.remove(item[1])

    return result_list, lemmed_set


# Check user level! Thousands of words, or ogden basical-level

def remove_basic_words(words):
    basic_words = open("dictionaries/basicDictionary", "r")
    for word in basic_words:
        if word.rstrip() in words:
            words.remove(word.rstrip())
    return words


def remove_ogden(words):
    basic_words = open("dictionaries/ogden_basic", "r")
    for word in basic_words:
        if word.rstrip() in words:
            words.remove(word.rstrip())
    return words


def remove_top_american(words):
    basic_words = open("dictionaries/popularityDict", "r")
    for word in basic_words:
        if word.rstrip() in words:
            words.remove(word.rstrip())
    return words


# Tiers are 500 words!
def remove_tier(words, tier):
    basic_words = open("dictionaries/10tiersDictionary", "r")
    b_words = basic_words.read().splitlines()
    for word in b_words[:tier * 500]:
        if word.rstrip() in words:
            words.remove(word.rstrip())
    return words


def show_help():
    for tag in candidate_pos:
        nltk.help.upenn_tagset(tag)


def extract_entities(subtitle_sentences):
    entities = set()

    for sentence in subtitle_sentences:
        tokens = nltk.word_tokenize(sentence)
        pos_tagged = nltk.pos_tag(tokens)
        tree_chunk = nltk.chunk.ne_chunk(pos_tagged)
        for child_node in tree_chunk:
            # print(child_node) #TODO: Gavnokod
            name = ""
            node_text = str(child_node)
            if "PERSON" in node_text:
                name = node_text.replace("PERSON ", "")
            if "GPE" in node_text:
                name = node_text.replace("GPE ", "")
            if "ORGANIZATION" in node_text:
                name = node_text.replace("ORGANIZATION ", "")
            if name != "":
                name = re.sub("(\/.{2,4})((?=\))|(?=\s))", "", name)[
                       1:-1]  # delete all tags with regexp and without first and last char
                entities.add(name.lower())
    print(entities)


def extract_entities_multithread(subtitle_sentences):
    number_threads = len(subtitle_sentences) // 300 + 1
    threads = []
    for i in range(0, number_threads):
        thread = threading.Thread(target=extract_entities, args=(subtitle_sentences[300 * i:300 * (i + 1)],))
        threads.insert(i, thread)
        thread.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()
    print(final_entities)
