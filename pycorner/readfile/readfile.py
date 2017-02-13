# -*- coding: utf-8 -*-
import numpy
from itertools import count

def dict(filename, cols=None, dtype=float, include=None, exclude='#', 
         delimiter='', removechar='#', hmode='1', linenum=1,
         hsep='', lower=False):
  """
  Creates a dictionary in which each chosen column in the file is an element
  of the dictionary, where keys correspond to column names.

  Uses the functions header and table to create a dictionary with the columns
  of the file (see each function's help).

  The file must have a header in which all column names are given.

  """
  if type(cols) in (str, int):
    cols = (cols,)
  full_output = False
  if cols is not None:
    if type(cols[0]) == str:
      full_output = True
  head = header(filename, cols=cols, removechar=removechar,
                hmode=hmode, linenum=linenum, hsep=hsep, lower=lower,
                full_output=full_output)
  if full_output:
    head, cols = head
  data = table(filename, cols=cols, dtype=dtype, include=include, 
               exclude=exclude, delimiter=delimiter)
  if type(data) == numpy.ndarray:
    if len(data.shape) == 1:
      dic = {head[0]: data}
    else:
      dic = {head[0]: data[0]}
      for i in range(1, len(head)):
        dic[head[i]] = data[i]
  else:
    dic = {head[0]: data[0]}
    for i in range(1, len(head)):
      dic[head[i]] = data[i]
  return dic

def header(filename, cols=None, removechar='#', hmode='1',
           linenum=0, hsep='', lower=False, full_output=False):
    """
    Returns the header of the file, which can be defined in various ways.
    
    Parameters
    ----------
    filename : str
        Name of the file
    cols : int/str or list of int/str's (default None, which takes all columns)
        Columns wanted in the output, either by number or by name (numbered
        starting at 0).
    removechar : str, optional (default '#')
        Character(s) to be removed from the first line, not part of the header.
        Used only when *mode=1*. Can also be None or False if not used.
    hmode : {'1', '2'}
        How the header is defined. mode '1' means column names are given in
        the first line, separated by spaces; mode '2' means they are given in
        separate lines at the top of the file with column numbers, as in
        SExtractor outputs. Note that the latter headers usually enumerate the
        columns starting from 1, which is corrected here. See below for
        further explanation
    linenum : int (default 0)
        The line number in which the header is located (count starts at 1). If
        *linenum=0* and *mode=1*, the header is assumed to be the first line
        starting with *removechar*.
    hsep : char (default ' ')
        Separator between column names. Typically <space> (default) or
        <comma>. Used only in *mode=1*.
    lower: boolean (default False)
        whether to return all column names in lower case
    full_output: bool (default False)
        if True, return the column numbers as well. Useful when the columns
        are defined from their names.

    Returns
    -------
    header : a list or numpy.ndarray with the desired column names


    THE *hmode* PARAMETER
    --------------------

        Definitions
        -----------
            hmode=1
        Single-line header given in line number *linenum*. The header line may
        start with any comment character which is specified in *removechar*.
        Column names are separated by *sep*. If *linenum=0*, the header will
        be assumed to be the first line starting with *removechar*.
            hmode=2
        Column names are given in separate lines with explanations, each of
        which starts with a '#', similar to the display of a FITS file header.
        Used, for instance, by SExtractor.
            hmode=3
        ApJ table format. File header contains a "byte-by-byte" description
        of the columns. No hashtags need to be present, but readfile can
        handle them if they are.

        Examples
        --------
        hmode=1
        Examples for different formats:
            removechar='#' :
            # ID  RA  Dec  redshift  mag_r
            removechar = '|' , sep = '|' :
            | ID | RA | Dec | redshift | mag_r |

        hmode=2
        # 1   ID                            Unique object identification
        # 2   RA                            J2000 Right Ascension (deg)
        # 3   Dec                           J2000 Declination (deg)
        # 4   redshift                      Object redshift
        # 5   mag_r                         Aperture magnitude in the r band
                                            (mag)

        hmode=3
        

    NOTES
    -----

        All leading and trailing spaces are removed from column names.

    """
    if cols is not None:
        tp = type(cols[0])
        if tp not in (int, str):
            raise TypeError('wrong type in cols, must be either str or int')
        for c in cols:
            if type(c) != tp:
                msg = 'All elements from cols must be of the same type'
                raise ValueError(msg)
    if removechar not in (False, None):
        if type(removechar) != str:
            raise TypeError('wrong type for removechar, should be str')

    head = []
    if type(cols) in (int, str):
        cols = (cols,)
    if cols is not None:
        if tp == str:
            colnums = []
    # horizontal header
    if hmode == '1':
        file = open(filename)
        if linenum > 0:
            for i in xrange(linenum):
                head = file.readline()
            if removechar:
                if head[:len(removechar)] == removechar:
                    head = head[len(removechar):]
        elif removechar:
            head = file.readline()
            if head[:len(removechar)] == removechar:
                head = head[len(removechar):]
        file.close()
        # split
        if hsep in ('', ' ', '\t'):
            head = head.split()
        else:
            head = head.replace('\n', '')
            head = head.split(hsep)
        # select columns
        if cols is not None:
            #aux = []
            if tp == str:
                aux = [h for h in head if h in cols]
                colnums = numpy.array([i for i, h in enumerate(head) \
                                       if h in cols])
            else:
                aux = [h for i, h in enumerate(head) if i in cols]
            head = aux

    # vertical header
    elif mode == '2':
        data = table(filename, cols=(1,2), dtype=(int,str), include='#')
        num  = data[0] # column numbers
        name = list(data[1]) # column names
        if cols is None:
            head = name
        else:
            head = []
            if tp == str:
                head = [i for i in cols if i in name]
                colnums = numpy.array([name.index(i) 
                                       for i in cols if i in name])
            else:
                head = [name[i] for i in xrange(len(num)) if num[i]-1 in cols]
            head = numpy.array(head, dtype=str)

    if lower:
        head = numpy.array([h.lower() for h in head])

    # remove leading and trailing spaces from each column name
    for i in xrange(len(head)):
        while head[i][0] == ' ':
            head[i] = head[i][1:]
        while head[i][-1] == ' ':
            head[i] = head[i][:-1]

    if cols is not None:
        if tp == int:
            colnums = cols
    if full_output:
        return head, colnums
    return head

def table(filename, cols=None, dtype=float, exclude='#', include=None, 
          delimiter='', whole=False, force_array=False, remove_spaces=True):
    """
    Returns a table with all the data in a file. Each column is returned as a
    numpy array.

    Parameters
    ----------
    filename : str
        Name of the file
    cols : int or list of ints (default None, which takes all columns)
        Columns wanted in the output (numbered starting at 0). If the file has
        columns that do not have data in one or more rows, only columns before
        those can be included.
    dtype : type or list of types (default float)
        A generic type for all columns or a type for each of the columns in
        *cols*. If *dtype* is a list of types, then it must be of the same 
        length of *cols*, or its length equal to the number of columns in the 
        file if cols==None. If a character cannot be converted to the desired
        type, the elements in the corresponding column will be strings.
    exclude : str or list of strings (default '#')
        Comment character(s), of any length. Lines starting with (any of the 
        elements of) *exclude* are not considered for the table.
    include : str or list of strings (default None)
        Lines to be included in the table must start with (any of the elements of) 
        *include*, (each of which) can be of any length. If given, it
        overrides *exclude*. Cannot have any spaces, and leading spaces in
        the file are ignored.
    delimiter : str (default ' ')
        Separator beween lines. Can be a string of any length.
    whole : boolean (default False) -- NOT YET IMPLEMENTED
        If True, the string or strings given in *include* or *exclude* are
        taken into account only if they are a full string, i.e., there is a
        *delimiter* character right after it.
    force_array : bool (default False)
        If True, each column is returned as an array even if the length of the
        column or row is one. This is useful if you are automatically dealing
        with arrays; by setting this, you always get the same format. By
        default, when each column or row has length 1, table() returns a
        single array with all the selected elements of the row/column.
    remove_spaces : bool (default True)
        If True, remove leading and trailing spaces from all string elements.
        NOT YET IMPLEMENTED

    Returns
    -------
    data : a list containing the selected columns in the file, each with the
        specified type. If dtype=all, a numpy array will be returned

    """
    if type(cols) in (int, str):
        cols = [cols]

    data = []
    if cols is not None:
        for i in cols:
            data.append([])

    file = open(filename)
    if include:
        if type(include) in (str, numpy.string_):
            include = [include]
        for line in file:
            for i in include:
                if line.replace(' ', '')[:len(i)] == i:
                    data = _append_single_line(data, line, delimiter,
                                               dtype, cols)
    elif exclude:
        if type(exclude) in (str, numpy.string_):
            exclude = [exclude]
        for line in file:
            write = True
            for e in exclude:
                if line[:len(e)] == e or line.replace(' ', '') == '\n':
                    write = False
                    break
                if write:
                    data = _append_single_line(data, line, delimiter,
                                               dtype, cols)
    else:
        for line in file:
            if line.replace(' ', '') != '\n':
                data = _append_single_line(data, line, delimiter, dtype, cols)

    #if remove_spaces:
        #for col in data:
            #if type(col[0]) == str:

    # if only one line is printed, don't want many arrays of length one but
    # one single array (if force_array is set to False)
    if not force_array:
        if len(data) > 1:
            if type(data[0]) == list:
                if len(data[0]) == 1:
                    table = []
                    if dtype is None:
                        for i in data:
                            try:
                                table.append(int(i[0]))
                            except ValueError:
                                try:
                                    table.append(float(i[0]))
                                except ValueError:
                                    table.append(i[0])
                    elif type(dtype) is type:
                        for i in data:
                            try:
                                table.append(dtype(i[0]))
                            except ValueError:
                                table.append(i[0])
                    else:
                        for i, tp in zip(data, dtype):
                            try:
                                table.append(tp(i[0]))
                            except ValueError:
                                table.append(i[0])
                    return table
        # the same if only one column is selected
        else:
            data = data[0]
            try:
                if len(data[0]) == 1:
                    try:
                        return dtype(data[0][0])
                    except ValueError:
                        return data[0][0]
            except TypeError:
                pass
            except IndexError:
                pass
            try:
                return numpy.array(data, dtype=dtype)
            except ValueError:
                return numpy.array(data, dtype=str)
    # many columns, many rows
    table = []
    if type(dtype) in (list, tuple, numpy.ndarray):
        for tp, row in zip(dtype, data):
            try:
                try:
                    table.append(numpy.array(row, dtype=tp))
                except ValueError:
                    table.append(numpy.array(row, dtype=str))
            except IndexError:
                print 'WARNING: No data selected from file', filename
                return []
    elif dtype is None:
        for row in data:
            try:
                try:
                    table.append(numpy.array(row, dtype=int))
                except ValueError:
                    try:
                        table.append(numpy.array(row, dtype=float))
                    except ValueError:
                        table.append(numpy.array(row, dtype=str))
            except IndexError:
                print 'WARNING: No data selected from file', filename
                return []
    else:
        for row in data:
            try:
                try:
                    table.append(numpy.array(row, dtype=dtype))
                except ValueError:
                    table.append(numpy.array(row, dtype=str))
            except IndexError:
                print 'WARNING: No data selected from file', filename
                return []
    if cols is not None:
        if len(cols) == 1:
            return table[0]
    return table

def _append_single_line(table, line, delimiter='', dtype=float, cols=None):
    """
    Auxiliary function, not meant to be used directly.

    Appends a single line to a table. Devised to iteratively make a table from
    a file. Can give a specified type to each field in the line (specified by 
    "dtype").

    """
    N = len(table)

    if delimiter in [' ', '', '\t']:
        line = line.split()
    else:
        line = line.replace('\n', '').split(delimiter)
    if type(dtype) in (list, numpy.ndarray, tuple):
        if cols is None:
            if len(dtype) == len(line):
                for i in range(len(line)):
                    try:
                        table[i].append(dtype[i](line[i]))
                    except IndexError:
                        table.append([])
                        table[i].append(dtype[i](line[i]))
            else:
                msg = 'array dtype has a different length than the line'
                msg += ' (dtype:%d; line:%d)' %(len(dtype), len(line))
                raise IndexError(msg)
        elif len(dtype) == len(cols):
            for i in xrange(len(cols)):
                table[i].append(dtype[i](line[cols[i]]))
            return table
        else:
            msg = 'arrays cols and dtype have different lengths in line'
            msg += ' (cols: %d; dtype:%d; line:%d)' \
                    %(len(cols), len(dtype), len(line))
            raise IndexError(msg)
                       
    elif type(dtype) == type:
        if cols is None:
            for i in range(len(line)):
                try:
                    try:
                        table[i].append(dtype(line[i]))
                    except ValueError:
                        table[i].append(line[i])
                except IndexError:
                    table.append([])
                    try:
                        table[i].append(dtype(line[i]))
                    except ValueError:
                        table[i].append(line[i])
        else:
            for i in range(len(cols)):
                try:
                    table[i].append(dtype(line[cols[i]]))
                except ValueError:
                    table[i].append(line[cols[i]])
        return table
    else:
        if cols is None:
            for l in line:
                try:
                    table[i].append(l)
                except IndexError:
                    table.append([])
                    table[i].append(l)
        else:
            table = [line[cols[i]] for i in xrange(len(cols))]
    return table
