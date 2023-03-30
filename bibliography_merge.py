"""
Merge 2 .bib files
"""
import re

BIB1 = 'My Library_clean.bib'
BIB2 = 'My Collection_clean.bib'

class BibEntry:
    def __init__(self, bibentry):

        # initialize
        self.type = ''
        self.author = ''
        self.journal = ''
        self.title = ''
        self.year = ''
        self.volume = ''
        self.number = ''
        self.pages = ''
        self.doi = ''

        entry_lines = bibentry.splitlines()

        # find bib entry type
        match = re.findall(r'\b\w+\b', entry_lines[0])
        self.type = match[0]

        for subidx, text in enumerate(entry_lines[1:]):
            match = re.findall(r'\b\w+\b', text)
            try:
                if match[0] == 'author':
                    match = re.findall(r'{.+}', text)
                    self.author = match[0].strip('{}').strip('{}')
                elif match[0] == 'journal':
                    match = re.findall(r'{.+}', text)
                    self.journal = match[0].strip('{}').strip('{}')
                elif match[0] == 'title':
                    match = re.findall(r'{.+}', text)
                    self.title = match[0].strip('{}').strip('{}')
                elif match[0] == 'year':
                    match = re.findall(r'\d\d\d\d', text)
                    self.year = match[0]
                elif match[0] == 'volume':
                    match = re.findall(r'{\d+}', text)
                    self.volume = match[0].strip('{}').strip('{}')
                elif match[0] == 'number':
                    match = re.findall(r'{.+}', text)
                    self.number = match[0].strip('{}').strip('{}')
                elif match[0] == 'pages':
                    match = re.findall(r'{.+}', text)
                    self.pages = match[0].strip('{}').strip('{}')
                elif match[0] == 'doi':
                    match = re.findall(r'{.+}', text)
                    self.doi = match[0].strip('{}').strip('{}')
            except:
                continue

# Read in bibliography entries from the two .bib files to be merged
with open(f'{BIB1}', encoding='utf8') as f:
    entries1 = f.read().split('@')
with open(f'{BIB2}', encoding='utf8') as f:
    entries2 = f.read().split('@')

# Read in one bibliography into a list of classes
bibentries = [BibEntry(entry) for entry in entries1[1:]]

# Loop through other bibliography and check for matches, then merge
for entry in entries2[1:]:
    bibcheck = BibEntry(entry)
    match = False
    # check for matches using year and title
    for bibentry in bibentries:
        
        if bibcheck.year == bibentry.year:
            checktitle = re.sub(r'[{}]', '', bibcheck.title).lower()
            bibtitle = re.sub(r'[{}]', '', bibentry.title).lower()

            if len(set(checktitle.split()) & set(bibtitle.split()))/max(len(set(checktitle.split())), len(set(bibtitle.split()))) > 0.9:
                match = True
                print(bibtitle)
                print(checktitle)
    if not match:
        entries1.append(entry)

with open(f'_merged.bib', 'w', encoding='utf8') as f:
    f.write('@' + '\n@'.join(sorted(entries1[1:])))

print(f'Processed {len(entries1)+len(entries2)} BibTeX entries.')