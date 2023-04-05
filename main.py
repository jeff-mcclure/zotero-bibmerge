"""
GUI program: 
-Select two .bib files to merge and clean.
-New .bib file saved to working directory.
"""

from tkinter import Tk, Frame, Button, Entry, filedialog
import re

# font and color theme
theme = lambda: None
theme.bfont = ('TkTextFont', 12, 'bold')
theme.dirfont = ('TkDefaultFont', 9)
theme.fcolor = "#FFFFFF"
theme.bgcolor = "#191919"
theme.bgcolor2 = "#46515C"
theme.bgcolor3 = "#333130"
theme.btncolor = "#2F546E"

class App:
    # Main app
    def __init__(self):
        root = Tk()
        root.title('Bibliography Merge')
        root.configure(bg=theme.bgcolor)

        fileBtn = cButton(root, "    Select Files    ", lambda: self.import_files(), theme)
        fileBtn.grid(row=0, column=0, sticky='N', padx=3, pady=5)
        self.fileEntry = Entry(root, width=50, bd=0, bg=theme.bgcolor2, highlightbackground=theme.fcolor, highlightthickness=1, fg=theme.fcolor)
        self.fileEntry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        mergeBtn = cButton(root, "    Merge Files    ", lambda: self.merge_files(), theme)
        mergeBtn.grid(row=1, column=0, sticky='N', padx=3, pady=5)

        root.geometry("500x200+200+200")
        root.wm_attributes("-topmost", 1)
        root.mainloop()

    def import_files(self):
        self.filenames = filedialog.askopenfilenames(title = "Select two .bib files to clean and merge.")
        self.fileEntry.insert(0, self.filenames)

    def merge_files(self):
        # clean files
        contents = [None] * len(self.filenames)
        for idx, bibname in enumerate(self.filenames):
            with open(f'{bibname}', encoding='utf8') as f:
                contents[idx] = f.read()

        for bib_idx, content in enumerate(contents):
            entries = content.split('@')
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

            with open(f'{self.filenames[bib_idx]}_clean.bib', 'w', encoding='utf8') as f:
                f.write('@' + '\n@'.join(sorted(entries[1:])))

        # merge files
        with open(f'{self.filenames[0]}_clean.bib', encoding='utf8') as f:
            entries1 = f.read().split('@')
        with open(f'{self.filenames[1]}_clean.bib', encoding='utf8') as f:
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

        with open(f'merged.bib', 'w', encoding='utf8') as f:
            f.write('@' + '\n@'.join(sorted(entries1[1:])))


class BibEntry:
    # BibTeX entry object
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

class cButton(Frame):
    # Control button
    def __init__(self, parent, btn_label, btn_command, theme, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.theme = theme
        self['highlightthickness'] = 1

        if type(btn_label) == str:
            self.Button = Button(self, text=btn_label, command=btn_command, font=theme.dirfont, bg=theme.bgcolor3, fg=theme.fcolor, bd=1, highlightthickness=0, activebackground=theme.btncolor, padx=15, pady=0, relief='flat')
        else:
            self.Button = Button(self, textvariable=btn_label, command=btn_command, font=theme.dirfont, bg=theme.bgcolor3, fg=theme.fcolor, bd=1, highlightthickness=0, activebackground=theme.btncolor, padx=15, pady=0, relief='flat')
        self.Button.pack(side="right")
        self.Button.bind('<Enter>', self.hover)
        self.Button.bind('<Leave>', self.leave)

    def hover(self, event):
        event.widget.configure(bg=self.theme.bgcolor2, relief='sunken')

    def leave(self, event):
        event.widget.configure(bg=self.theme.bgcolor3, relief='flat')

if __name__ == "__main__":
    app = App()
