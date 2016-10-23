import text_extractor
import word_extractor
import word_analyzer
import kmeans

parsed_sentences = text_extractor.parseSRT("harry-potter-and-the-deathly-hallows-part-1-yify-english.srt")
sub_text = ''.join(str(elem) for elem in parsed_sentences)
candidates_words = word_extractor.rough_result_set(sub_text)

candidates_words = word_extractor.remove_100(candidates_words)
print("Amount of candidate words: " + str(len(candidates_words)))
kmeans.fitKMeans(candidates_words)
