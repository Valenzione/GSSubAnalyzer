import codecs
from datetime import datetime, timedelta

end_punct = ('.', '!', '?')
tags_replace = ('<i>', '</i>', '<b>', '</b>', '...')


def parseSRT(f_in):
    parsed_subtitle = []
    # Process with opening the input file.
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

    return parsed_subtitle


def chunkSRT(f_in, chunks_num):
    subtitle_chunks = list()
    lines = f_in.read().splitlines()
    for line in lines[::-1]:
        if '-->' in line and line.startswith('0'):
            last_line = line[line.find('-->') + 3:].replace(' ', '')
            break
    for line in lines:
        if '-->' in line and line.startswith('0'):
            first_line = line[line.find('-->') + 3:].replace(' ', '')
            break
    last_time = datetime.strptime(last_line, '%H:%M:%S,%f')
    first_time = datetime.strptime(first_line, '%H:%M:%S,%f')
    rest_time = (last_time - first_time) // chunks_num

    current_time = timedelta()
    current_chunk = 0
    for line in lines:
        if '-->' in line and line.startswith('0'):
            time_line = line[line.find('-->') + 3:].replace(' ', '')
            current_time = datetime.strptime(time_line, '%H:%M:%S,%f') - first_time
        if (current_time > rest_time * (current_chunk + 1)):
            current_chunk += 1
        if (len(subtitle_chunks) < current_chunk + 1):
            subtitle_chunks.append(line)
        else:
            subtitle_chunks[current_chunk] += line

    return subtitle_chunks
