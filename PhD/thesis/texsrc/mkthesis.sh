#!/bin/bash

## Make each chapter

name[1]="one"
name[2]="two"
name[3]="three"
name[4]="four"
name[5]="five"
name[6]="six"

for i in {1..5}
#for i in 3
do

    file=${name[$i]}
    chapter=chapter${i}/
    root=$chapter$file
    bib=bib${i}.bib

    python makebib.py ${root}.tex -b input.bib -o ./$bib
    rm ${file}.aux
    xelatex -no-pdf $root && bibtex $root
    mv ${root}.bbl .
    rm ${file}.aux
    xelatex -no-pdf $root && xelatex -no-pdf $root && \
        xelatex -no-pdf $root && xelatex $root
    mv $bib $chapter
    mv ${file}.* $chapter

done

## Make entire thesis

python makebib.py thesis.tex -b input.bib -o bibliography.bib
xelatex -no-pdf thesis && bibtex thesis && \
    xelatex -no-pdf thesis && xelatex thesis

