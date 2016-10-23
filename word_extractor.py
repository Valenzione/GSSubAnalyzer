import enchant
import nltk
import re

import threading

# Symbol	Meaning	        Example
# S	        sentence	    the man walked
# NP	    noun phrase	    a dog
# VP	    verb phrase	    saw a park
# PP	    prepositional   phrase	with a telescope
# Det	    determiner	    the
# N	        noun	        dog
# V	        verb	        walked
# P	        preposition	    in

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
    tokens = nltk.word_tokenize(subtitle_text)  # Create tokens from text
    words_num=len(tokens)

    tagged = nltk.pos_tag(tokens)  # Detect POS for each token

    # Count POS bumbers for every POS TODO: Delete at Release
    for tag_tuple in tagged:
        try:
            pos_number[tag_tuple[1]] += 1
        except KeyError:
            pos_number[tag_tuple[1]] = 1

    # If spell check is passed and POS is one of the candidate POS's, then append it to result list.
    for tag_tuple in tagged:
        for pos in candidate_pos:
            if (tag_tuple[1] == pos) and (spell_checker.check(tag_tuple[0])):
                result_list.append(tag_tuple[0].lower())

    fdist = nltk.FreqDist(tokens)  # Erase most popular?
    for x in fdist.most_common(words_num//10):
        if x[0].lower() in result_list:
            result_list.remove(x[0].lower())

    return set(result_list)


def remove_100(words):
    basic_words = open("dictionaries/100basic_words", "r")
    for word in basic_words:
        if word.rstrip() in words:
            words.remove(word.rstrip())
    return words
