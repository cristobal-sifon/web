import argparse
import os
import re
import numpy
import sys


"""
Create a new bib file containing only the references used in a given texfile,
from a "master" bibfile.

"""


def main():
    args = read_args()

    # go!
    citations, inputfiles = readtex(args.texfile)
    if len(inputfiles) > 0:
        for ifile in inputfiles:
            if not os.path.isfile(ifile):
                print 'Warning: file {0} not found'.format(ifile)
                continue
            cit, inp = readtex(ifile)
            if len(inp) > 0:
                for i in inp:
                    cit = numpy.append(cit, readtex(i)[0])
            citations = numpy.append(citations, cit)

    # read bibfile for full references
    fullrefs, lastnames = readbib(args.bibfile, citations)

    # the indices to use in order to print alphabetically
    j = sorted(range(len(lastnames)), key=lambda k: lastnames[k])
    # print out!
    out = open(args.output, 'w')
    for i in j:
        for line in fullrefs[i]:
            print >>out, line
        print >>out, ''
    out.close()
    return


def readtex(texfile):
    """
    look for \cite objects line by line and save all input files to look at
    them afterwards

    """
    print texfile
    carry = False
    citations = []
    inputfiles = []
    folders = texfile.split('/')[:-1]
    if len(folders) == 0:
        path = ''
    else:
        path = os.path.join(*folders)
    #if not os.path.isfile(texfile):
        #return None, None
    tex = open(texfile)
    for line in tex:
        # discard commented text
        if '%' in line:
            j = line.index('%')
            if line[j-1] != '\\':
                line = line[:j]
        else:
            line = line.replace('\n', '')
        # find inputs
        j = [s.start() for s in re.finditer('\input{', line)]
        j2 = [s.start() for s in re.finditer('\include{', line)]
        j = numpy.array(numpy.append(j, j2), dtype=int)
        if len(j) > 0:
            for i in j:
                subline = line[i:]
                end = subline.index('}')
                if subline[:5] == 'input':
                    start = 6
                elif subline[:7] == 'include':
                    start = 8
                ifile = subline[start:end]
                if ifile[-4:] != '.tex':
                    ifile += '.tex'
                inputfiles.append(ifile)
        if carry:
            j = [s.start() for s in re.finditer('{', line)]
            if len(j) == 0:
                continue
            for i in j:
                subline = line[i:]
                if '{' in subline:
                    start = subline.index('{') + 1
                else:
                    start = 0
                if '}' in subline:
                    end = subline.index('}')
                    carry = False
                else:
                    end = len(subline) + 1
                refs = subline[start:end].split(',')
                for r in refs:
                    if r not in citations:
                        citations.append(r)
        j = [s.start() for s in re.finditer('\cite', line)]
        if len(j) == 0:
            continue
        # bug: when using e.g., \Cref{} within the square brackets
        # of \citep, it is the argument of \Cref that is read
        # rather than that of \citep!
        for i in j:
            subline = line[i:]
            # to allow for pathological cases like
            # "\citep[see \ref{s:data} and][]{sifon13}
            while '{' in subline:
                start = subline.index('{') + 1
                if '}' in subline:
                    end = subline.index('}')
                else:
                    end = len(subline)
                refs = subline[start:end].split(',')
                for r in refs:
                    if r.strip() not in citations:
                        citations.append(r.strip())
                # to allow for pathological cases like
                # "\citep[see \ref{s:data} and][]{sifon13}
                subline = subline[end+1:]
            else:
                carry = True
    tex.close()
    return citations, inputfiles


def readbib(bibfile, citations):
    """
    read the input bibfile and return references
    """
    citations = [c.lower() for c in citations]
    fullrefs = []
    lastnames = []
    go = False
    bib = open(bibfile)
    for il, line in enumerate(bib):
        if line[0] == '@':
            try:
                ref = line.split()[0].split('{')[1]
            except IndexError:
                msg = 'IndexError: wrong format for line\n'
                msg += line
                print msg
                continue
            if ref[-1] != ',':
                print ' ** ERROR ** reference %s in line #%d of %s is' \
                      %(ref, il+1, bibfile),
                print ' missing a comma at the end. Please fix and run again.'
                continue
            ref = ref[:-1]
            if ref.lower() in citations:
                fullrefs.append([])
                go = True
        if go:
            words = line.split()
            if len(words) == 0:
                continue
            if 'author=' in words[0].lower():
                words[0] = words[0].split('=')
                words = [w for word in words for w in word]
            if words[0].lower() == 'author':
                j = [i for i, w in enumerate(words) \
                     if w.lower() not in ('author', '=', 'and') and '.' not in w]
                authors = []
                for i in j:
                    if words[i][0] == '{' and words[i][-2:] == '},':
                        this_author = words[i].replace('{', '')
                        authors.append(this_author.replace('},', ''))
                    elif words[i][0] == '{':
                        this_author = words[i].replace('{', '')
                    elif words[i][-2:] == '},':
                        this_author += ' ' + words[i].replace('},', '')
                        authors.append(this_author)
                lastnames.append(' '.join(authors))
            if words[0] == '}':
                fullrefs[-1].append(line.replace('\n', ''))
                go = False
            else:
                fullrefs[-1].append(line.replace('\n', ''))
    bib.close()
    return fullrefs, lastnames


def print_help():
    """
    help is always useful!
    """
    msg = '\nUsage: python makebib.py texfile\n\n'
    msg += 'This code will read all the references in a .tex file'
    msg += ' and write a .bib file containing all\n'
    msg += 'of them once and ordered alphabetically.'
    msg += ' The output file will be called bibliography.bib and\n'
    msg += 'will be located in the same folder as the'
    msg += ' input .tex file.'
    print msg
    return


def read_args():
    parser = argparse.ArgumentParser()#description=print_help())
    add = parser.add_argument
    add('texfile')
    hlp = 'input bib file. All references used in the tex file will be'
    hlp += ' extracted from this file and placed in the output.'
    add('-b', dest='bibfile', default='input.bib', help=hlp)
    hlp = 'output bib file. If full (relative) path is not given, the output'
    hlp += ' is placed in the same folder as the input tex file.'
    add('-o', dest='output', default='bibliography.bib', help=hlp)
    args = parser.parse_args()

    if args.texfile[-4:] != '.tex':
        msg = 'Error: must provide a .tex latex file'
        print msg
        exit()
    # if the full path is not given, the output is placed
    # in the same folder as the input tex file.
    if args.output[0] != '/' and args.output[:2] != './' \
            and len(args.texfile.split('/')) > 1:
        args.output = os.path.join('/'.join(args.texfile.split('/')[:-1]),
                                   args.output)

    return args

main()
