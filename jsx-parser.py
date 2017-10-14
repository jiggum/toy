import re
import sys

openSCs = r"((?!\\(?:\\\\)*)(?:\"\"\")|(?:\\\\)|(?:/\*)|[`'\"\(\[\{]|\${)"
closeSCs = r"((?!\\(?:\\\\)*)(?:\"\"\")|(?:\\n)|(?:\*/)|[`'\"\)\]\}])"
totalSCs = r"((?!\\(?:\\\\)*)(?:\"\"\")|(?:\\\\)|(?:/\*)|(?:\\n)|(?:\*/)|[`'\"\(\[\{\)\]\}]|\${)"
stringSCs = r"([`'\"])"
annotationSCs = r"((?:\\\\)|(?:/\*)|(?:\\n)|(?:\*/))"
openTagReg = r"(<((?:(?!\W).)*))"
closeTagReg= r"(/>|</((?:(?!\W).)*)>)"

# index
def isSc(symbol):
    return isMatchExactly(totalSCs, symbol)
def isOpenSC(symbol):
    return isMatchExactly(openSCs, symbol)
def isCloseSC(symbol):
    return isMatchExactly(closeSCs, symbol)
def isStringSC(symbol):
    return isMatchExactly(stringSCs, symbol)
def isAannotationSC(symbol):
    return isMatchExactly(annotationSCs, symbol)
def isOpenTagStart(symbol):
    return isMatchExactly(openTagReg, symbol)
def isCloseTag(symbol):
    return isMatchExactly(closeTagReg, symbol)
def isMatchExactly(reg, symbol):
    return bool(re.match(r"^" + reg + r"$", symbol))

def getSymbolPair(srcSymbol):
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
    openTagMatch = re.match(openTagReg, srcSymbol)
    if openTagMatch:
        openTag = openTagMatch.groups()[0]
        openTagName = openTagMatch.groups()[1]
        symbolPairs.append((openTag,">"))
        symbolPairs.append((openTag,"</%s>"%(openTagName)))
        symbolPairs.append((">", openTag))
        symbolPairs.append(("</%s>"%(openTagName),openTag))
    #closeTag ex) /> or </span>
    closeTagMatch = re.match(closeTagReg, srcSymbol) 
    if closeTagMatch:
        closeTag = closeTagMatch.groups()[0]
        closeTagName = closeTagMatch.groups()[1]   
        symbolPairs.append((closeTag,">"))
        symbolPairs.append((closeTag,"</%s>"%(closeTagName)))
        symbolPairs.append((">", closeTag))
        symbolPairs.append(("</%s>"%(closeTagName),closeTag))
    return [symbol[1] for symbol in symbolPairs if symbol[0] == srcSymbol]

def findCloseSymbol(targetSymbol, string, openSymbolStacks=[]):
    index = 0
    while True:
        searchedSymbolMatch = re.search(totalSCs, string[index:])
        if not searchedSymbolMatch:
            return
        index += searchedSymbolMatch.start()
        searchedSymbol = searchedSymbolMatch.groups()[0]
        if searchedSymbol == targetSymbol:
            print 1, openSymbolStacks
            return index, openSymbolStacks[:-1]
        #print searchedSymbol, targetSymbol
        if isOpenSC(searchedSymbol):
            _closeSymbol = getSymbolPair(searchedSymbol)[0]
            _string = string[index + 1:]
            _openSymbolStacks =openSymbolStacks + [searchedSymbol]
            _index, openSymbolStacks = findCloseSymbol(_closeSymbol, _string, _openSymbolStacks)
            index += _index + 1
        index+=1



def parseString(string, openSymbolStacks=[]):
    print "%sStart Parsing, opensymbolStacks : %s"%("¦¢ " * len(openSymbolStacks), openSymbolStacks)
    startIndex = 0
    endIndex = 0
    while True:
        startIndex = endIndex
        print ("%sParsing Loop string : %s"%("¦¢ " * len(openSymbolStacks), len(string) - startIndex > 30 and string[startIndex:startIndex+30] + "  ..." or string[startIndex:])).replace("\n", "\\n")
        searchedSymbolMatch = re.search(totalSCs, string[startIndex:])
        if not searchedSymbolMatch:
            print "%sThere Is No Searched Symbol"%("¦¢ " * len(openSymbolStacks))
            return
        searchedSymbol = searchedSymbolMatch.groups()[0]        
        #print "%sSearched Symbol : %s"%("¦¢ " * len(openSymbolStacks), searchedSymbol)
        startIndex += searchedSymbolMatch.start()
        endIndex = startIndex + len(searchedSymbol)
        if openSymbolStacks:
            #Detacted CloseSC
            if openSymbolStacks[-1] in getSymbolPair(searchedSymbol): 
                print "%sFinded Close Tag : %s"%("¦¢ " * len(openSymbolStacks), searchedSymbol)
                return startIndex, endIndex
            #If Parents' Symbol is String Symbol ex) ` | ' | "
            if isStringSC(openSymbolStacks[-1]):
                if not searchedSymbol == "${":
                    continue      
            #If Parents' Symbol is Aannotation Symbol ex) // | /*
            if isAannotationSC(searchedSymbol):
                continue                 
        if isOpenSC(searchedSymbol):
            _string = string[endIndex:]
            _openSymbolStacks = openSymbolStacks + [searchedSymbol]
            _startIndex, _endIndex = parseString(_string, _openSymbolStacks)
            endIndex += _endIndex
            continue