from hyphen import Hyphenator, dict_info


def syllables(word):
    h_en = Hyphenator('en_US')
    syllables = h_en.syllables(word)
    return syllables


def return_difficulty(word):
    syllables_count = len(syllables(word))
    return syllables_count
