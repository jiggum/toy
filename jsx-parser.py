import re
import sys

patternWithOutBackSlash = r"(?!\\(?:\\\\)*)"
patternString = r"((?:\"\"\")|[`'\"])"
patternAnnotationOpen = r"((?://)|(?:/\*))"
patternAnnotationClose = r"((?:\\n)|(?:\*/))"
patternAnnotationTotal = re.compile("(%s)"%("|".join([patternAnnotationOpen[1:-1], patternAnnotationOpen[1:-1]]))).pattern
patternTagOpen = r"((?:<((?:(?!\W).)*)))"
patternTagOpenPerfect = r"((?:<((?:(?!\W).)*)>))"
patternTagClose = r"((?:/>))"
patternTagClosePerfect = r"((?:</((?:(?!\W).)*)>))"
patternTagTotal = re.compile("(%s)"%("|".join([patternTagOpenPerfect[1:-1], patternTagOpen[1:-1], patternTagClosePerfect[1:-1], patternTagClose[1:-1]]))).pattern
patternOpen = re.compile("(%s%s)"%(r"(?!\\(?:\\\\)*)", "|".join([patternString[1:-1], patternAnnotationOpen[1:-1], patternTagOpenPerfect[1:-1], patternTagOpen[1:-1]]))).pattern
patternClose = re.compile("(%s%s)"%(r"(?!\\(?:\\\\)*)", "|".join([patternString[1:-1], patternAnnotationClose[1:-1], patternTagClosePerfect[1:-1], patternTagClose[1:-1]]))).pattern
patternTotal = re.compile("(%s%s)"%(r"(?!\\(?:\\\\)*)", "|".join([patternString[1:-1], patternAnnotationTotal[1:-1], patternTagTotal[1:-1]]))).pattern

# index
def isPattern(symbol):
    return matchExactly(patternTotal, symbol)
def isPatternOpen(symbol):
    return matchExactly(patternOpen, symbol)
def isPatternClose(symbol):
    return matchExactly(patternClose, symbol)
def isPatternString(symbol):
    return matchExactly(patternString, symbol)
def isPatternAannotation(symbol):
    return matchExactly(patternAnnotationTotal, symbol)
def isPatternTagOpen(symbol):
    return matchExactly(patternTagOpen, symbol)
def isPatternTagOpenPerfect(symbol):
    return matchExactly(patternTagOpenPerfect, symbol)
def isPatternTagClose(symbol):
    return matchExactly(patternTagClose, symbol)
def isPatternTagClosePerfect(symbol):
    return matchExactly(patternTagClosePerfect, symbol)
def matchExactly(reg, symbol):
    return re.match(r"^" + reg + r"$", symbol)

def getPatternlPair(srcSymbol):
    symbolPairs=[
        ("\"\"\"","\"\"\""),
        ("`","`"),
        ("'","'"),
        ("\"","\""),
        ("(",")"),
        (")","("),
        ("[","]"),
        ("]","["),
        ("{","}"),
        ("}","{"),
        ("${","}"),
        ("}","${"),
        ("//","\\n"),
        ("\\n","//"),
        ("/*","*/"),
        ("*/","/*"),
    ]
    #openTag ex) <span
    openTagMatch = matchExactly(patternTagOpen, srcSymbol)
    if openTagMatch:
        openTag = openTagMatch.groups()[0]
        openTagName = openTagMatch.groups()[1]
        symbolPairs.append((openTag,">"))
        symbolPairs.append((">", openTag))
        symbolPairs.append((openTag,"\\>"))
        symbolPairs.append(("\\>", openTag))
    #openTagPerfect ex) <span>
    openTagPerfectMatch = matchExactly(patternTagOpenPerfect, srcSymbol)
    if openTagPerfectMatch:
        openTagPerfect = openTagPerfectMatch.groups()[0]
        openTagPerfectName = openTagPerfectMatch.groups()[1]
        symbolPairs.append((openTagPerfect,"</%s>"%(openTagPerfectName)))
        symbolPairs.append(("</%s>"%(openTagPerfectName),openTagPerfect))        
    #closeTag ex) /> or </span>
    closeTagMatch = re.match(patternTagClose, srcSymbol) 
    if closeTagMatch:
        closeTag = closeTagMatch.groups()[0]
        closeTagName = closeTagMatch.groups()[1]   
        symbolPairs.append((closeTag,">"))
        symbolPairs.append((closeTag,"</%s>"%(closeTagName)))
        symbolPairs.append((">", closeTag))
        symbolPairs.append(("</%s>"%(closeTagName),closeTag))
    return [symbol[1] for symbol in symbolPairs if symbol[0] == srcSymbol]

def findPatternClose(targetSymbol, string, openSymbolStacks=[]):
    index = 0
    while True:
        searchedSymbolMatch = re.search(patternTotal, string[index:])
        if not searchedSymbolMatch:
            return
        index += searchedSymbolMatch.start()
        searchedSymbol = searchedSymbolMatch.groups()[0]
        if searchedSymbol == targetSymbol:
            print 1, openSymbolStacks
            return index, openSymbolStacks[:-1]
        #print searchedSymbol, targetSymbol
        if isPatternOpen(searchedSymbol):
            _closeSymbol = getPatternlPair(searchedSymbol)[0]
            _string = string[index + 1:]
            _openSymbolStacks =openSymbolStacks + [searchedSymbol]
            _index, openSymbolStacks = findPatternClose(_closeSymbol, _string, _openSymbolStacks)
            index += _index + 1
        index+=1



def parseString(string, openSymbolStacks=[]):
    print "%sStart Parsing, opensymbolStacks : %s"%("¦¢ " * len(openSymbolStacks), openSymbolStacks)
    startIndex = 0
    endIndex = 0
    while True:
        startIndex = endIndex
        print ("%sParsing Loop string : %s"%("¦¢ " * len(openSymbolStacks), len(string) - startIndex > 30 and string[startIndex:startIndex+30] + "  ..." or string[startIndex:])).replace("\n", "\\n")
        searchedSymbolMatch = re.search(patternTotal, string[startIndex:])
        if not searchedSymbolMatch:
            print "%sThere Is No Searched Symbol"%("¦¢ " * len(openSymbolStacks))
            return
        searchedSymbol = searchedSymbolMatch.groups()[0]        
        #print "%sSearched Symbol : %s"%("¦¢ " * len(openSymbolStacks), searchedSymbol)
        startIndex += searchedSymbolMatch.start()
        endIndex = startIndex + len(searchedSymbol)
        if openSymbolStacks:
            #Detacted CloseSC
            if openSymbolStacks[-1] in getPatternlPair(searchedSymbol): 
                print "%sFinded Close Tag : %s"%("¦¢ " * len(openSymbolStacks), searchedSymbol)
                return startIndex, endIndex
            #If Parents' Symbol is String Symbol ex) ` | ' | "
            if isPatternString(openSymbolStacks[-1]):
                if not searchedSymbol == "${":
                    continue      
            #If Parents' Symbol is Aannotation Symbol ex) // | /*
            if isPatternAannotation(searchedSymbol):
                continue                 
        if isPatternOpen(searchedSymbol):
            _string = string[endIndex:]
            _openSymbolStacks = openSymbolStacks + [searchedSymbol]
            _startIndex, _endIndex = parseString(_string, _openSymbolStacks)
            endIndex += _endIndex
            continue