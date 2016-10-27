import codecs
from datetime import datetime, timedelta

end_punct = ('.', '!', '?')
tags_replace = ('<i>', '</i>', '<b>', '</b>', '...')


def parseSRT(raw_subtitle):
    parsed_subtitle = []
    # Process with opening the input file.
    # !remove blank lines!
    lines = filter(None, (line.rstrip() for line in raw_subtitle))

    incomplete_sentence = ""
    # remove unnecessary lines and write it to a new file
    for line in lines:
        # Ignore the numeric ID of each text
        if line.isdigit() and len(line) < 6:
            continue
        # Ignore the time indicator such as '00:00:12,340'
        if line.startswith('0'):
            continue
        # Ignore some trivial attributes such as '<font>~</font>'
        if line.startswith('<font'):
            continue
        if line.startswith('['):
            continue

        for tag in tags_replace:
            line = line.replace(tag, '')

        incomplete_sentence += line + ' '

        if line.endswith(end_punct):
            parsed_subtitle.append(incomplete_sentence)
            incomplete_sentence = ""

    return parsed_subtitle

def extractBlocks(raw_subtitle):
    blocks = list()
    buffer = list()
    for line in raw_subtitle:
        if not line.strip():
            blocks.append(buffer)
            buffer = list()
        else:
            if (len(buffer) >= 3):
                buffer.append(buffer.pop(2) + " " + line)
            else:
                buffer.append(line)

    return blocks
