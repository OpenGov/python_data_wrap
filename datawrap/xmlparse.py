#!/usr/bin/python
#  ************************************************************************
#
#                               EXCELREADER.PY
#
#  ************************************************************************
#
#    --- LICENSE ----------- (New BSD) ---
#
#    Copyright ( c ) 2007, Gregg Tavares (Greggman)
#
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are
#    met:
#
#    Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#    Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#    Neither the name of the Gregg Tavares nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
#    DESCRIPTION
#
#       Reads an Excel XML file and provides functions for accessing cels
#
#
#    HISTORY
#
#       05/18/07 GAT: Created.
#               09/11/07 GAT: Fixed issues with "in" vs "has_key". "in" doesn't work on all versions of python for the attr dicts
#               11/13/07 GAT: added style support and functions for maxRow and maxColumn
#               11/14/07 GAT: changed to use excel names for styles
#               11/15/07 GAT: added stuff to *attempt* to make it work in a *python* way. You can now access a cell with
#               11/18/14 MSeal: Fixed several naming errors, fixed characters appending instead of replaceming content
#
#                       import excelreader;
#                       xl = excelreader.ParseExcelXMLFile("SomeExcelFile.xml")
#                       print "cell B4 in the first sheet  = ", xl[0][4][2]
#                       print "cell B4 in the Sheet1       = ", xl["Sheet1"][4][2]
#                       print "num sheets                  = ", xl.len()
#           print "sheet names                 = ", xl.keys()
#           print "index of last row in Sheet1 = ", len(xl["Sheet1"])
#           sheet = xl["Sheet1"]
#           print "cell B4 in this sheet       = ", sheet[4][2]
#
#       The biggest issue is still that cells and rows are indexed from 1. The reason I think that is important
#       is if I number from 0 then if you are told to lookup cell B47 you'd use
#
#                       sheet[46][1] # for B47? yuck!! If I'm told 47 I want to type 47
#
#       But, the consequence is what to use for range etc.
#
#               # print all the cells in a sheet
#
#               for row in range(1, len(sheet[0]) + 1)
#                               for column in range(1, len(sheet[1] + 1)
#                                       print row, column, sheet[row][column]
#
#               11/15/07 GAT: utility functions IndexToColumn, ColumnToIndex, ParseCellSpec
#                     Also made it so you can reference stuff by excel cell spec if you want as in
#                     sheet['B7'] which is the same as sheet[7]['B'] which is the same as sheet[7][2]
#
#                     also I removed len() since there is no way for it not to be confusing. Use
#                     worksheet.GetMaxRow(), worksheet.GetMaxColumn() or for a loop use keys
#
#                                                       for row in worksheet.keys():
#                                                               for column in worksheet[row].keys():
#                                                                       cellValue = worksheet[row][column]
#                                                                       if cellValue == None:
#                                                                               cellValue = "*undef"
#                                                                       print "%c:%d (%s)  " % (64 + column, row, cellValue),
#                                                               print ""
#
#
# Downloaded from: https://code.google.com/p/script-automatic/source/browse/trunk/+script-automatic+--username+m.wawrzyniuk%40gmail.com/NotUsed/excelreader.py?r=69
#

import sys,re
from xml.sax.handler import ContentHandler
from xml.sax import parse
from optparse import OptionParser
from UserDict import UserDict

__specRe = re.compile("^([A-Z]+)(\d+)$", re.IGNORECASE)

def merge (dst, src):
        """put key/value pairs that exist in src but not in dst into dst"""
        for key in src.keys():
                if not dst.has_key(key):
                        dst[key] = src[key]

def IndexToColumn (ndx):
        """convert index to column. Eg: IndexToColumn(2) = "B", IndexToColumn(28) = "AB" """
        ndx -= 1
        col  = chr(ndx % 26 + 65)
        while (ndx > 25):
                ndx  = ndx / 26
                col  = chr(ndx % 26 + 64) + col
        return col

def ColumnToIndex (col):
        """convert column to index. Eg: ConvertInIndex("AB") = 28"""
        ndx = 0
        for c in col:
                ndx = ndx * 26 + ord(c.upper()) - 64
        return ndx

def ParseCellSpec (spec):
        """convert cell spec to row,col. Eg. ParseCellSpec("B5") = [2, 5]"""
        m = __specRe.match(spec)
        (column, row) = m.groups()
        return (int(row), ColumnToIndex(column))


class Row(UserDict):
        def __init__ (self, worksheet):
                UserDict.__init__(self)
                self.worksheet = worksheet # so we return consistant length
                self.finalized = False

        def __len__ (self):
                raise  AssertionError, "Do not use len() on a Row. Use worksheet.GetMaxColumn() or row.keys()"

        def __getitem__ (self,key):
                if self.finalized:
                        if isinstance(key, str):
                                key = ColumnToIndex(key)
                        if key > 0 and key <= self.worksheet.GetMaxColumn():
                                return self.GetCellValue(key)
                        else:
                                raise KeyError, key
                else:
                        return UserDict.__getitem__(self,key)

        def keys (self):
                if self.finalized:
                        return range(1, self.worksheet.GetMaxColumn() + 1)
                else:
                        return UserDict.keys(self)

        def values(self):
                values = []
                for key in self.keys():
                        values.append(self.GetCellValue(key))
                return values

        def friend_Finalize (self):
                self.finalized = True

        def GetCellValue (self, column, default = None):
                """ get a cell, return default if that cell does not exist
                        note that column and row START AT 1 same as excel
                """
                if isinstance(column, str):
                        column = ColumnToIndex(column)
                if self.has_key(column):
                        if UserDict.__getitem__(self, column).has_key("content"):
                                return UserDict.__getitem__(self, column)["content"]
                return default

        def GetCellValueNoFail (self, column):
                """ get a cell, if it does not exist fail
                note that column at row START AT 1 same as excel
                """
                cell = GetCellValue(self, column)
                if cell == None:
                        raise ValueError, "cell %d does not exist" % (column,)
                return cell

        def GetCellStyle (self, column):
                """ get the "style" of a cell
                        note: this merges default, column, row and the cell's style into the actual style for you returning a dictionary of styles
                        The values directly from excel with the relavent XML element appended to the name. Examples of style key/value pairs

                        --key--------------------value-----------------------
                        Alignment_ss:Vertical : Bottom
                        Font_ss:Color         : #0000FF
                        Font_x:Family             : Decorative
                        Font_ss:Size          : 11
                        Font_ss:FontName      : Algerian
                        Interior_ss:Pattern   : Solid
                        Interior_ss:Color     : #808000
                """
                if isinstance(column, str):
                        column = ColumnToIndex(column)
                style = { }
                # get style for cell
                if self.has_key(column):
                        if UserDict.__getitem__(self, column).has_key("style"):
                                merge(style, UserDict.__getitem__(self, column)["style"])
                return style

class Worksheet (UserDict):
        def __init__ (self, name, defaultStyle):
                UserDict.__init__(self)
                self.name           = name
                self.maxColumn      = 0
                self.maxRow         = 0
                self.rowStyles      = { }
                self.columnStyles   = { }
                self.defaultStyle   = defaultStyle
                self.finalized      = False

        def __len__ (self):
                raise  AssertionError, "Do not use len() on a worksheet. Use worksheet.GetMaxRow() or worksheet.keys()"

        def __getitem__ (self, key):
                if self.finalized:
                        if isinstance(key, str):
                                # assume it's a full cell spec,
                                (row,column) = ParseCellSpec(key)
                                return self[row][column]
                        if key > 0 and key <= self.maxRow:
                                return UserDict.__getitem__(self,key)
                        else:
                                raise KeyError, key
                else:
                        return UserDict.__getitem__(self,key)

        def keys (self):
                return range(1, self.maxRow + 1)

        def friend_Finalize (self):
                self.finalized = True

        def friend_addRow(self, rowNum, row):
                """used only by parser: adds a row of columns"""
                self[rowNum] = row
                if (rowNum > self.maxRow):
                        self.maxRow = rowNum

                for cellNum in row.keys():
                        if cellNum > self.maxColumn:
                                self.maxColumn = cellNum

                return row.friend_Finalize()

        def friend_addColumnStyle (self, column, style):
                """used only by parse: adds a column style"""
                self.columnStyles[column] = style

        def friend_addRowStyle (self, row, style):
                """used only by parse: adds a row style"""
                self.rowStyles[row] = style

        def HasCells (self):
                """returns True if there are any cells in this worksheet"""
                return self.maxRow > 0 and self.maxColumn > 0

        def GetName (self):
                """returns the name of the worksheet"""
                return self.name

        def GetMaxRow (self):
                """returns the index of the last used row.
                Excel rows are indexed starting at 1 not 0"""
                return self.maxRow

        def GetMaxColumn (self):
                """returns the index of the last used column.
                note: Excel columns are indexed starting at 1 not 0"""
                return self.maxColumn

        def GetCellValue (self, column, row = None, default = None):
                """ get a cell, return default if that cell does not exist
                        note that column and row START AT 1 same as excel
                """
                if row == None:
                        (row, column) = ParseCellSpec(column)
                if self.has_key(row):
                        return self[row].GetCellValue(column, default)
                return default

        def GetCellValueNoFail (self, column, row = None):
                """ get a cell, if it does not exist fail
                note that column at row START AT 1 same as excel
                """
                if row == None:
                        (row, column) = ParseCellSpec(column)
                cell = GetCellValue(self, column, row)
                if cell == None:
                        raise ValueError, "cell %d:%d does not exist" % (column, row)
                return cell

        def GetCellStyle (self, column, row = None):
                """ get the "style" of a cell
                        note: this merges default, column, row and the cell's style into the actual style for you returning a dictionary of styles
                        The values directly from excel with the relavent XML element appended to the name. Examples of style key/value pairs

                        --key--------------------value-----------------------
                        Alignment_ss:Vertical : Bottom
                        Font_ss:Color         : #0000FF
                        Font_x:Family             : Decorative
                        Font_ss:Size          : 11
                        Font_ss:FontName      : Algerian
                        Interior_ss:Pattern   : Solid
                        Interior_ss:Color     : #808000
                """
                if row == None:
                        (row, column) = ParseCellSpec(column)
                style = { }
                # get style for cell
                if self.has_key(row):
                        merge(style, self[row].GetCellStyle(column))
                # merge with row style
                if self.rowStyles.has_key(row):
                        merge(style, self.rowStyles[row])
                # merge with column style
                if isinstance(column, str):
                        column = ColumnToIndex(column)
                if self.columnStyles.has_key(column):
                        merge(style, self.columnStyles[column])
                # merge with default style
                merge(style, self.defaultStyle)
                return style

        def GetColumnNumber (self, columnName):
                """returns the column number for a given column heading name, 0 if not found"""
                for row in range(1, self.maxRow + 1):
                        for column in range(1, self.maxColumn + 1):
                                if self.GetCellValue(column, row, "") == columnName:
                                        return column
                return 0

        def DumpAsCSV (self, separator=",", file=sys.stdout):
                """dump as a comma separated value file"""
                for row in range(1, self.maxRow + 1):
                        sep = ""
                        for column in range(1, self.maxColumn + 1):
                                file.write("%s\"%s\"" % (sep, self.GetCellValue(column, row, "")))
                                sep = separator
                        file.write("\n")

class ExcelFile:
        """Excel file. A collection of worksheets"""
        def __init__ (self):
                self.worksheets = []
                self.worksheetsByName = { }
                self.styles           = { }
                self.defaultStyle     = None

        def __len__ (self):
                return len(self.worksheets)

        def keys(self):
                return self.worksheetsByName.keys()

        def values(self):
                return self.worksheetsByName.values()

        def items (self):
                return self.worksheetsByName.items()

        def __getitem__ (self, key):
                return self.GetWorksheet(key)

        def friend_AddWorksheet (self, worksheet):
                self.worksheets.append(worksheet)
                self.worksheetsByName[worksheet.GetName()] = worksheet

        def friend_AddStyle (self, style):
                self.styles[style["name"]] = style
                if self.defaultStyle == None:
                        self.defaultStyle = style

        def GetStyle (self, styleName):
                return self.styles[styleName]

        def GetDefaultStyle (self):
                return self.defaultStyle

        def GetWorksheets (self):
                return self.worksheets

        def GetWorksheet(self, nameOrNumber):
                """get a sheet by number"""
                if isinstance(nameOrNumber, int):
                        return self.worksheets[nameOrNumber]
                else:
                        return self.worksheetsByName[nameOrNumber]

class ExcelToSparseArrayHandler(ContentHandler):
        """sax handler to parse an xml file worksheets with sparse arrays
           access sheets in order with handler.worksheets[sheetNum]
           or by name with handler.GetSheet(name)
        """
        def __init__ (self, excelfile):
                self.excelfile        = excelfile
                self.currentWorksheet = None
                self.currentRow       = None
                self.currentCell      = None
                self.currentRowNum    = 0
                self.currentColumnNum = 0
                self.currentRowSpan   = 0
                self.inCell           = False
                self.mergeAcross      = None
                self.currentContents  = ""

        def characters (self, content):
                if self.inCell:
                        if self.currentContents:
                                self.currentContents += content
                        else:
                                self.currentContents = content
                        if self.mergeAcross:
                                for column in range(1, self.mergeAcross + 1):
                                        self.currentRow[self.currentColumnNum + column] = self.currentRow[self.currentColumnNum]
                                self.mergeAcross = None

        def start_Table (self, attrs):
                self.columnStyles = { } # clear the styles as they are only relavent for one table
                self.currentColumnNum = 0

        def start_Column (self, attrs):
                self.currentColumnNum = int(attrs.get("ss:Index", str(self.currentColumnNum + 1)))
                span = int(attrs.get("ss:Span", "1"))
                for col in range(0, span):
                        if attrs.has_key("ss:StyleID"):
                                self.currentWorksheet.friend_addColumnStyle(self.currentColumnNum + col, self.excelfile.GetStyle(attrs["ss:StyleID"]))
                self.currentColumnNum += span - 1

        def start_Worksheet (self, attrs):
                self.currentWorksheet = Worksheet(attrs["ss:Name"], self.excelfile.GetDefaultStyle());
                self.currentRowNum = 0
                self.excelfile.friend_AddWorksheet(self.currentWorksheet)

        def end_Worksheet (self):
                self.currentWorksheet.friend_Finalize()

        def start_Row (self, attrs):
                self.currentColumnNum = 0
                newRowNum = int(attrs.get("ss:Index", str(self.currentRowNum + 1)))
                for rowNum in range(self.currentRowNum + 1, newRowNum):
                        emptyRow = Row(self.currentWorksheet)
                        self.currentWorksheet.friend_addRow(rowNum, emptyRow)
                self.currentRowNum   = newRowNum
                self.currentRow      = Row(self.currentWorksheet)
                self.currentRowStyle = None
                self.currentRowSpan  = int(attrs.get("ss:Span", "1"))
                for row in range(0, self.currentRowSpan):
                        if attrs.has_key("ss:StyleID"):
                                self.currentWorksheet.friend_addRowStyle(self.currentRowNum + row, self.excelfile.GetStyle(attrs["ss:StyleID"]))

        def end_Row (self):
                for row in range(0, self.currentRowSpan):
                        self.currentWorksheet.friend_addRow(self.currentRowNum + row, self.currentRow)
                self.currentColumnNum += self.currentRowSpan - 1
                self.currentRowSpan = 0

        def start_Cell (self, attrs):
                self.currentColumnNum = int(attrs.get("ss:Index", str(self.currentColumnNum + 1)))
                self.mergeAcross = attrs.get("ss:MergeAcross", None)
                self.currentRow[self.currentColumnNum] = { }
                if attrs.has_key("ss:StyleID"):
                        self.currentRow[self.currentColumnNum]["style"] = self.excelfile.GetStyle(attrs["ss:StyleID"])

        def start_Data (self, attrs):
                self.currentContents = ""
                self.inCell = True

        def end_Data (self):
                self.currentRow[self.currentColumnNum]["content"] = self.currentContents
                self.inCell = False

        def start_Style (self, attrs):
                style = {
                        "name" : attrs["ss:ID"],
                }
                self.currentStyle = style
                self.excelfile.friend_AddStyle(style)

        def __addStyles (self, name, attrs):
                for key in attrs.keys():
                        self.currentStyle[name + "_" + key] = attrs[key]

        def start_Alignment (self, attrs):
                self.__addStyles("Alignment", attrs)

        def start_Font (self, attrs):
                self.__addStyles("Font", attrs)

        def start_Interior (self, attrs):
                self.__addStyles("Interior", attrs)

        def start_Borders (self, attrs):
                self.__addStyles("Borders", attrs)

        def start_NumberFormat (self, attrs):
                self.__addStyles("NumbefFormat", attrs)

        def start_Protection (self, attrs):
                self.__addStyles("Protection", attrs)

        def end_Style (self):
                self.currneStyle = None

        def startElement (self, name, attrs):
                '''if there's a start method for this element, call it
                '''
                func = getattr(self, 'start_' + name, None)
                if func:
                        func(attrs)

        def endElement (self, name):
                '''if there's an end method for this element, call it
                '''
                func = getattr(self, 'end_' + name, None)
                if func:
                        func()


def ParseExcelXMLFile(filename):
        """parse an excel file

                typical usage:

                import exceldump;
                xl = exceldump.ParseExcelXMLFile("SomeExcelFile.xml")
                worksheet = xl.GetWorksheets(0) # get first worksheet
                print worksheet.GetCellValue(1,1) # print contents of cell A1
        """

        excelfile = ExcelFile()
        excelHandler = ExcelToSparseArrayHandler(excelfile)
        parse(filename, excelHandler)
        return excelfile

if __name__=="__main__":
        argParser = OptionParser(usage="usage: %prog [options] excel-XML-file")
        argParser.add_option("-?", action="help",                                       help="show this help message and exit")
        argParser.add_option("-v", action="store_true",  dest="verbose", default=False, help="print lots of info")
        argParser.add_option("-d", action="store_true",  dest="debug",   default=False, help="pass debug flag to tools")

        (options, args) = argParser.parse_args()

        if len(args) < 1:
                argParser.print_help()
                sys.exit(0)

        xlXMLFileName = args[0]

        xl = ParseExcelXMLFile(xlXMLFileName)

        # example: dump it all
        print "-----------------"
        for worksheet in xl.GetWorksheets():
                print "worksheet : %s" % (worksheet.GetName(), )
                print "maxRow    : %d" % (worksheet.GetMaxRow(), )
                print "maxColumn : %d" % (worksheet.GetMaxColumn(), )
                for row in range(1, worksheet.GetMaxRow() + 1):
                        for column in range(1, worksheet.GetMaxColumn() + 1):
                                print "%c:%d (%s)  " % (64 + column, row, worksheet.GetCellValue(column, row, "*undef*")),
                        print ""

        # example: dump it all python style
        print "-----------------"
        for worksheet in xl:
                print "worksheet : %s" % (worksheet.GetName(), )
                print "maxRow    : %d" % (worksheet.GetMaxRow(), )
                print "maxColumn : %d" % (worksheet.GetMaxColumn(), )
                for row in worksheet.keys():
                        for column in worksheet[row].keys():
                                cellValue = worksheet[row][column]
                                if cellValue == None:
                                        cellValue = "*undef"
                                print "%c:%d (%s)  " % (64 + column, row, cellValue),
                        print ""

        # dump styles
        print "-----------------"
        for worksheet in xl.GetWorksheets():
                print "worksheet : %s" % (worksheet.GetName(), )
                print "maxRow    : %d" % (worksheet.GetMaxRow(), )
                print "maxColumn : %d" % (worksheet.GetMaxColumn(), )
                for row in range(1, worksheet.GetMaxRow() + 1):
                        for column in range(1, worksheet.GetMaxColumn() + 1):
                                style = worksheet.GetCellStyle(column, row)
                                print "%c:%d (%s)  " % (64 + column, row, style),
                        print ""
        print "-----------------"

        # example: make csv using first worksheet
        worksheet = xl.GetWorksheet(0)

        worksheet.DumpAsCSV(",", sys.stdout)
