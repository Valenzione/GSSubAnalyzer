import enchant
import nltk
import re

import threading
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

'''
Following code get parsed srt files as input and produces a set of candidate words for
lexical analysis.
1.Tokenize and POS-tag words.
2.Check for POS and spelling. Produce set of candidate words from this.
3.Get result from Entity Extractor and remove those items from set of candidate words
'''
candidate_pos = ('VBD', 'VBG', 'VB', 'RB', 'JJS', 'RBR', 'NN', 'NNS', 'VBZ', 'VBP')
pos_number = {}  # dictionary for number of pos
persons = []  # list with person names.
result_list = []  # list with candidate words
spell_checker = enchant.Dict("en_US")  # Check spelling and eliminate all wrong spelled words

final_entities = set()


def extract_words(raw_subtitle, extracted_number):
    parsed_sentences = text_extractor.parseSRT(raw_subtitle)
    sub_text = ''.join(str(elem) for elem in parsed_sentences)
    words_data, lemmed_words = rough_result_set(sub_text)
    lemmed_words = remove_basic_words(lemmed_words)
    lemmed_words = remove_top_american(lemmed_words)
    lemmed_words = remove_tier(lemmed_words, 5)
    words_data = [record for record in words_data if record[1] in lemmed_words]
    print(len(words_data), len(lemmed_words))
    timed_words_data = get_timedelta(words_data, raw_subtitle)
    for tuple in timed_words_data:
        print(tuple)


def get_timedelta(words_data, raw_subtitle):
    timed_words_data = list()
    subtitle_blocks = text_extractor.extractBlocks(raw_subtitle)
    for block in subtitle_blocks:
        current_found_words = set();
        for record in words_data:
            if (record[0] in block[2]) and (len(record) == 3) and not (record[0] in current_found_words):
                current_found_words.add(record[0])
                tuple_list = list(record)
                time_from, time_to = block[1].split(" --> ")
                tuple_list.append(time_from)
                tuple_list.append(time_to)
                record = tuple(tuple_list)
                timed_words_data.append(record)
    return timed_words_data


def show_help():
    for tag in candidate_pos:
        nltk.help.upenn_tagset(tag)


def extract_entities(subtitle_sentences):
    entities = set()
    print(len(subtitle_sentences))
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


def rough_result_set(subtitle_text):
    lemmatizer = WordNetLemmatizer()
    lemmed_set = set();
    tokens = nltk.word_tokenize(subtitle_text)  # Create tokens from text

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
                if (spell_checker.check(new_word)) and len(new_word) > 2 and spell_checker.check(tag_tuple[0]):
                    result_list.append((tag_tuple[0], new_word.lower(), tag_tuple[1]))
                    lemmed_set.add(new_word.lower())
                    # fdist = nltk.FreqDist(tokens)  # Erase 10% of most popular words among tokens.
                    # for x in fdist.most_common(words_num // 10):
                    #     if x[0].lower() in result_list:
                    #         result_list.remove(x[0].lower())

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
