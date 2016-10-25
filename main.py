import codecs

import text_extractor
import word_extractor
import word_analyzer
import kmeans

subtitle_reader = codecs.open('subtitles\\01.srt', "r", encoding='utf-8', errors='ignore')
subtitle_chunks = text_extractor.chunkSRT(subtitle_reader, 5)
subtitle_reader = codecs.open('subtitles\\01.srt', "r", encoding='utf-8', errors='ignore')
parsed_sentences = text_extractor.parseSRT(subtitle_reader)
sub_text = ''.join(str(elem) for elem in parsed_sentences)
candidates_words = word_extractor.rough_result_set(sub_text)

candidates_words = word_extractor.remove_ogden(candidates_words)
print("Amount of candidate words:", len(candidates_words))

for chunk in subtitle_chunks:
    print(subtitle_chunks.index(chunk))
    for word in candidates_words:
        if word in chunk:
            print(word)
