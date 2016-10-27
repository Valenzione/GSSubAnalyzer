import codecs
import word_extractor

subtitle_reader = codecs.open('subtitles\\02.srt', "r", encoding='utf-8', errors='ignore')
raw_subtitle = subtitle_reader.read().splitlines()
word_extractor.extract_words(raw_subtitle, 6)

