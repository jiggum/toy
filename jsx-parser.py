import re
import sys

#pattern must be inside of r"()"
patternWithOutBackSlash = r"(?!\\(?:\\\\)*)"
patternString = r"((?:\"\"\")|[`'\"])"
patternAnnotationOpen = r"((?://)|(?:/\*))"
patternAnnotationClose = r"((?:\\n)|(?:\*/))"
patternAnnotationTotal = re.compile("(%s)"%("|".join([patternAnnotationOpen[1:-1], patternAnnotationOpen[1:-1]]))).pattern
patternTagOpen = r"((?:<((?:((?!\W).)|\.)+)))"
patternTagOpenPerfect = r"((?:<((?:((?!\W).)|\.)+)>))"
patternTagClose = r"(/?>)"
patternTagClosePerfect = "((?:</((?:((?!\W).)|\.)+)>))"
patternTagTotal = re.compile("(%s)"%("|".join([patternTagOpenPerfect[1:-1], patternTagOpen[1:-1], patternTagClosePerfect[1:-1], patternTagClose[1:-1]]))).pattern
patternBracketOpen = r"(\${|[\(\[\{])"
patternBracketClose = r"([\)\]\}])"
patternOpen = re.compile("(%s%s)"%(r"(?!\\(?:\\\\)*)", "|".join([pattern[1:-1] for pattern in [patternString, patternAnnotationOpen, patternTagOpenPerfect, patternTagOpen, patternBracketOpen]]))).pattern
patternClose = re.compile("(%s%s)"%(r"(?!\\(?:\\\\)*)", "|".join([pattern[1:-1] for pattern in [patternString, patternAnnotationClose, patternTagClosePerfect, patternTagClose, patternBracketClose]]))).pattern
patternTotal = re.compile("((?:%s)|(?:%s))"%(patternOpen[1:-1], patternClose[1:-1])).pattern

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
def isPatternBracketClose(symbol):
    return matchExactly(patternBracketOpen, symbol)
def isPatternBracketClosePerfect(symbol):
    return matchExactly(patternBracketClose, symbol)
def matchExactly(reg, symbol):
    return re.match(r"^" + reg + r"$", symbol)

def getPatternPairClose(srcSymbol):
    symbolPairs=[
        #string
        ("\"\"\"","\"\"\""),
        ("`","`"),
        ("'","'"),
        ("\"","\""),
        #bracket
        ("(",")"),
        ("[","]"),
        ("{","}"),
        ("${","}"),
        #annotation
        ("//","\\n"),
        ("/*","*/"),
    ]
    #openTag ex) <span
    openTagMatch = matchExactly(patternTagOpen, srcSymbol)
    if openTagMatch:
        openTag = openTagMatch.groups()[0]
        openTagName = openTagMatch.groups()[1]
        symbolPairs.append((openTag,">"))
        symbolPairs.append((">", openTag))
        symbolPairs.append((openTag,"/>"))
        symbolPairs.append(("/>", openTag))
    #openTagPerfect ex) <span>
    openTagPerfectMatch = matchExactly(patternTagOpenPerfect, srcSymbol)
    if openTagPerfectMatch:
        openTagPerfect = openTagPerfectMatch.groups()[0]
        openTagPerfectName = openTagPerfectMatch.groups()[1]
        symbolPairs.append((openTagPerfect,"</%s>"%(openTagPerfectName)))
        symbolPairs.append(("</%s>"%(openTagPerfectName),openTagPerfect))
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
            _closeSymbol = getPatternPairClose(searchedSymbol)[0]
            _string = string[index + 1:]
            print 1, _string
            _openSymbolStacks =openSymbolStacks + [searchedSymbol]
            _index, openSymbolStacks = findPatternClose(_closeSymbol, _string, _openSymbolStacks)
            index += _index + 1
        index+=1



def parseString(string, openSymbolStacks=[], debug=False):
    contents = []
    if debug:
        print "%sStart Parsing, opensymbolStacks : %s"%("¦¢ " * len(openSymbolStacks), openSymbolStacks)
    startIndex = 0
    endIndex = 0
    while endIndex < len(string):
        startIndex = endIndex
        currentString = string[startIndex:]
        if debug:
            print ("%sParsing Loop string : %s"%("¦¢ " * len(openSymbolStacks), len(string) - startIndex > 30 and currentString[:startIndex+30] + "  ..." or currentString)).replace("\n", "\\n")
        searchedSymbolMatch = re.search(patternTotal, currentString)
        if not searchedSymbolMatch:
            if debug:
                print "%sThere Is No Searched Symbol"%("¦¢ " * len(openSymbolStacks))
            return -1, -1, contents
        searchedSymbol = searchedSymbolMatch.groups()[0]        
        startIndex += searchedSymbolMatch.start()
        endIndex = startIndex + len(searchedSymbol)
        if openSymbolStacks:
            #Detacted CloseSC
            if searchedSymbol in getPatternPairClose(openSymbolStacks[-1]): 
                if debug:
                    print "%sFinded Close Symbol : %s"%("¦¢ " * len(openSymbolStacks), searchedSymbol)
                #If Parents' Symbol is Tag but Not Perfect
                if isPatternTagOpen(openSymbolStacks[-1]) and searchedSymbol == ">":
                    openSymbolStacks[-1] = openSymbolStacks[-1] + ">"
                    continue
                #If Parents' Symbol is Perfect Tag
                if isPatternTagOpenPerfect(openSymbolStacks[-1]):
                    content = currentString[:searchedSymbolMatch.start()]
                    contents.append(content)
                return startIndex, endIndex, contents
            #If Parents' Symbol is String Symbol ex) ` | ' | "
            if isPatternString(openSymbolStacks[-1]) and not searchedSymbol == "${":
                continue      
            #If Parents' Symbol is Aannotation Symbol ex) // | /*
            if isPatternAannotation(searchedSymbol):
                continue
        if isPatternOpen(searchedSymbol):
            #If Parents' Symbol is Perfect Tag
            if openSymbolStacks and isPatternTagOpenPerfect(openSymbolStacks[-1]):
                content = currentString[:searchedSymbolMatch.start()]
                contents.append(content)                
            _string = string[endIndex:]
            _openSymbolStacks = openSymbolStacks + [searchedSymbol]
            _startIndex, _endIndex, _contents = parseString(_string, _openSymbolStacks)
            contents = contents + _contents
            endIndex += _endIndex
            continue
    return startIndex, endIndex, contents

def contentsFilter(_contents):
    return [\
        content.strip() for content in _contents \
        if content.strip() and \
        re.search(r"[°¡-ÆR]", content)]