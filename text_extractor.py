import codecs

end_punct = ('.', '!', '?')
tags_replace = ('<i>', '</i>', '<b>', '</b>', '...')


def parseSRT(subtitle_name):
    parsed_subtitle = []
    # Process with opening the input file.
    with codecs.open('subtitles/'+subtitle_name, "r", encoding='utf-8', errors='ignore') as f_in:
        # !remove blank lines!
        lines = filter(None, (line.rstrip() for line in f_in))

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

    f_in.close()
    return parsed_subtitle
