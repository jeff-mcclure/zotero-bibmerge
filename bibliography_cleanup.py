"""
Created on Wed Mar  9 22:10:46 2022
Thesis: name, year, title, MASc. Thesis or PhD Thesis, university, url
Article: names, year, title, journal, volume (number), pages, url
Textbook: names, year, title, edition, publisher, url
Conference:
"""

LIBNAME = ['My Library','My Collection']

content = []
for bibname in LIBNAME:
    with open(f'{bibname}.bib', encoding='utf8') as f:
        content.append(f.read())

for bib_idx, contents in enumerate(content):
    entries = contents.split('@')
    for idx, entry in enumerate(entries):
        entry_lines = entry.splitlines()
        subidx_todelete = []
        for subidx, text in enumerate(entry_lines):
            if subidx == 0:
                continue
            if any(x in text for x in ['urldate =', 'abstract =', 'file =', 'language =', 'note =', 'keywords =']):
                subidx_todelete.append(subidx)

        for index in reversed(subidx_todelete):
            del entry_lines[index]

        entries[idx] = '\n'.join(entry_lines)

    with open(f'{LIBNAME[bib_idx]}_clean.bib', 'w', encoding='utf8') as f:
        f.write('@' + '\n@'.join(sorted(entries[1:])))
