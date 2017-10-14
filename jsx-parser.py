import re
import sys

openSCs = r"((?!\\(?:\\\\)*)(?:\"\"\")|(?:/\*)|[`'\"\(\[\{]|\${)"
closeSCs = r"((?!\\(?:\\\\)*)(?:\"\"\")|(?:\*/)|[`'\"\)\]\}])"
totalSCs = r"((?!\\(?:\\\\)*)(?:\"\"\")|(?:/*)|(?:\*/)|[`'\"\(\[\{\)\]\}]|\${)"
stringSCs = r"([`'\"])"
remarkSCs = r"((?:\\\\)|(?:/\*)|(?:\\n)|(?:\*/))"
openTagReg = r"(<((?:(?!\W).)*))"
closeTagReg= r"(/>|</((?:(?!\W).)*)>)"

# index
def isSc(symbol):
    return isMatchExactly(totalSCs, symbol)
def isOpenSC(symbol):
    return isMatchExactly(openSCs, symbol)
def isCloseSC(symbol):
    return isMatchExactly(closeSCs, symbol)
def isStringSc(symbol):
    return isMatchExactly(stringSCs, symbol)
def isRemarkTag(symbol):
    return isMatchExactly(remarkSCs, symbol)
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
    print "%sStart Parsing, opensymbolStacks : %s"%("│ " * len(openSymbolStacks), openSymbolStacks)
    index = 0
    while True:
        print ("%sParsing Loop string : %s"%("│ " * len(openSymbolStacks), len(string) - index > 30 and string[index:index+30] + "  ..." or string[index:])).replace("\n", "\\n")
        searchedSymbolMatch = re.search(totalSCs, string[index:])
        if not searchedSymbolMatch:
            print "%sThere Is No Searched Symbol"%("│ " * len(openSymbolStacks))
            return
        index += searchedSymbolMatch.start()
        searchedSymbol = searchedSymbolMatch.groups()[0]
        if openSymbolStacks:
            #닫는태그발견시
            #print searchedSymbol, getSymbolPair(searchedSymbol), openSymbolStacks[-1], openSymbolStacks[-1] in getSymbolPair(searchedSymbol)
            if openSymbolStacks[-1] in getSymbolPair(searchedSymbol): 
                print "%sFinded Close Tag : %s"%("│ " * len(openSymbolStacks), searchedSymbol)
                return index
            #상위 기호가 스트링 기호일경우 (`, ', ")
            if isStringSc(openSymbolStacks[-1]):
                if not searchedSymbol == "${":
                    index+=1
                    continue  
        if isOpenSC(searchedSymbol):
            _string = string[index + 1:]
            _openSymbolStacks = openSymbolStacks + [searchedSymbol]
            _index = parseString(_string, _openSymbolStacks)
            index += _index + 1
        index+=1
        
#TEST

#srcFile = open("jsx.txt", "r")

#s =  re.search(openSCs, "fasefsa'e")
#s.start(), s.end(), s.span(), s.pos, s.endpos, s.string =>
#7 8 (7, 8) 0 9 fasefsa'e
#s.groups()
#("'", None)
