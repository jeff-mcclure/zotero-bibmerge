"""
GUI program: 
-Select: two .bib files to merge and clean.
-Merge: the new merged.bib file is saved to the same directory as the main .bib file.
"""

from tkinter import Tk, Frame, Button, Entry, filedialog, StringVar, Label
import re
import os

# Font and color theme definition
theme = lambda: None
theme.bfont = ('TkTextFont', 12, 'bold')
theme.dirfont = ('TkDefaultFont', 9)
theme.fcolor = "#FFFFFF"
theme.bgcolor = "#191919"
theme.bgcolor2 = "#46515C"
theme.bgcolor3 = "#333130"
theme.btncolor = "#2F546E"

class App:
    def __init__(self):
        # GUI window and buttons
        root = Tk()
        root.title('zotero-bibmerge')
        root.configure(bg=theme.bgcolor)

        self.mainbib_txt = StringVar()
        self.mergebib_txt = StringVar()
        self.status_txt = StringVar()
        self.status_txt.set('Select a main .bib file and a second .bib file to merge with it.')

        mainbibBtn = cButton(root, "   Main .bib path   ", lambda: self.import_files(self.mainbib_txt), theme)
        mainbibBtn.grid(row=0, column=0, sticky='NW', padx=3, pady=5)
        self.mainbibEntry = Entry(root, width=50, textvariable=self.mainbib_txt, bd=0, bg=theme.bgcolor2, highlightbackground=theme.fcolor, highlightthickness=1, fg=theme.fcolor)
        self.mainbibEntry.grid(row=0, column=1, sticky='NE', padx=5, pady=5)

        mergebibBtn = cButton(root, " Merge .bib path ", lambda: self.import_files(self.mergebib_txt), theme)
        mergebibBtn.grid(row=1, column=0, sticky='NW', padx=3, pady=5)
        self.mergebibEntry = Entry(root, width=50, textvariable=self.mergebib_txt, bd=0, bg=theme.bgcolor2, highlightbackground=theme.fcolor, highlightthickness=1, fg=theme.fcolor)
        self.mergebibEntry.grid(row=1, column=1, sticky='NE', padx=5, pady=5)

        statusLbl = Label(root, textvariable=self.status_txt, font=theme.dirfont, bg=theme.bgcolor3, fg=theme.fcolor)
        statusLbl.grid(row=2, column=0, columnspan = 2, sticky='SW', padx=5, pady=5)

        mergeBtn = cButton(root, "    Merge .bibs    ", lambda: self.merge_files(self.mainbib_txt, self.mergebib_txt, self.status_txt), theme)
        mergeBtn.grid(row=2, column=1, sticky='SE', padx=5, pady=5)

        root.grid_columnconfigure(0,weight=1)
        root.grid_columnconfigure(1,weight=10)
        root.grid_rowconfigure([0,1,2],weight=1)
        root.geometry("500x200+200+200")
        root.wm_attributes("-topmost", 1)
        root.mainloop()

    def import_files(self, entry_txt):
        # Select file dialog
        self.filename = filedialog.askopenfilename(title = "Select .bib file.")
        entry_txt.set(self.filename)

    def merge_files(self, main_txt, merge_txt, status_txt):
        # Clean files
        self.filenames = [main_txt.get(), merge_txt.get()]
        dir_path = os.path.dirname(main_txt.get())

        for bib_name in self.filenames:
            with open(f'{bib_name}', encoding='utf8') as f:
                entries = f.read().split('@')

            for entry_idx, entry in enumerate(entries):
                entry_lines = entry.splitlines()

                # Deletes irrelevant lines in bib entry
                line_idx_todelete = []
                delete_switch = False
                for line_idx, line in enumerate(entry_lines):
                    if line_idx == 0:
                        continue
                    if any(x in line for x in ['urldate =', 'abstract =', 'file =', 'language =', 'note =', 'keywords =', 'shorttitle =']):
                        line_idx_todelete.append(line_idx)
                        delete_switch = True
                        continue
                    if delete_switch:
                        if any(x in line for x in ['title =', 'volume =', 'issn =', 'url =', 'doi =', 'journal =', 'author =', 'month =', 'year =', 'pages =', 'number =', 'address =', 'booktitle = ', 'publisher =', 'isbn =', 'type =', 'school =', 'institution =', 'edition =', 'series =', 'editor =']) or line == '}':
                            delete_switch = False
                            continue
                        line_idx_todelete.append(line_idx)
 
                for line_idx in reversed(line_idx_todelete):
                    del entry_lines[line_idx]
                entries[entry_idx] = '\n'.join(entry_lines)
            with open(bib_name.strip('.bib') + '_clean.bib', 'w', encoding='utf8') as f:
                f.write('@' + '\n@'.join(sorted(entries[1:])))

        # Merge files
        with open(self.filenames[0].strip('.bib') + '_clean.bib', encoding='utf8') as f:
            entries1 = f.read().split('@')
        with open(self.filenames[1].strip('.bib') + '_clean.bib', encoding='utf8') as f:
            entries2 = f.read().split('@')

        # Read in one bibliography into a list of classes
        bibentries = [BibEntry(entry) for entry in entries1[1:]]

        # Loop through the second bibliography and ignore duplicates, then merge
        duplicate_count = 0
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
                        duplicate_count += 1
            if not match:
                entries1.append(entry)

        with open(f'{dir_path}\merged.bib', 'w', encoding='utf8') as f:
            f.write('@' + '\n@'.join(sorted(entries1[1:])))
        
        status_txt.set(f'Bib merge completed. {duplicate_count} duplicate(s) were detected.')
        print(f'Bib merge completed. {duplicate_count} duplicate(s) were detected.')


class BibEntry:
    # BibTeX entry object
    def __init__(self, bibentry):
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

        # Find bib entry type
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
