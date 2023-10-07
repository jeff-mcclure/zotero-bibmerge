# zotero-bibmerge
A simple program that cleans and merges two bibliography files, for use with BibTeX in creating LaTeX documents. 

The cleaning involves deleting abstract, urldate, file, language, note, keywords, and shorttitle fields.

The merging involves only copying bibliography entries which are not shared between the two files. In the case of duplicates, the entry in the main bibliography file is saved. 
