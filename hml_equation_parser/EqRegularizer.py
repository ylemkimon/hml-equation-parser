from typing import Dict, Tuple, List
import json, codecs
import os
import re

def insertList (index: int, origin: List[str], lst: List[str]) -> List[str]:
    beforePart = origin[0:index]
    afterPart = origin[index:]
    return beforePart + lst + afterPart

def matchCurlyBraces (strList: List[str]) -> List[str]:
    '''
    Match curly braces if they don't.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Curly bracket matched string list.
    '''
    isMatched = 0
    for idx, elem in enumerate(strList):
        if elem == "{":
            isMatched = isMatched + 1
        elif elem == "}":
            isMatched = isMatched - 1
        
    if isMatched > 0:
        while isMatched > 0:
            strList.insert(idx+1, "}")
            isMatched = isMatched - 1
    
    
    isMatched = 0
    for idx, elem in reversed(list(enumerate(strList))):
        if elem == "}":
            isMatched = isMatched + 1
        elif elem == "{":
            isMatched = isMatched - 1
        
    if isMatched > 0:
        while isMatched > 0:
            strList.insert(idx, "{")
            isMatched = isMatched - 1
    
    return strList

def sqrtRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize sqrts.
    
    This involves replacing "root" to "sqrt", adding braces to "sqrt"s without braces.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Square root regualrized string list.
    '''
    for idx, elem in enumerate(strList):
        if re.match("^.*sqrt.+", elem) != None:
            sqrtLocation = elem.find("sqrt")
            beforePart = elem[0:sqrtLocation]
            sqrtPart = elem[sqrtLocation:sqrtLocation+4]
            remainderPart = elem[sqrtLocation+4:]
            del strList[idx]
            strList.insert(idx, beforePart)
            strList.insert(idx+1, "}")
            strList.insert(idx+1, remainderPart)
            strList.insert(idx+1, "{")
            strList.insert(idx+1, sqrtPart)
        elif re.match("^.*root.+", elem) != None:
            sqrtLocation = elem.find("root")
            beforePart = elem[0:sqrtLocation]
            sqrtPart = "sqrt"
            remainderPart = elem[sqrtLocation+4:]
            del strList[idx]
            strList.insert(idx, beforePart)
            strList.insert(idx+1, "}")
            strList.insert(idx+1, remainderPart)
            strList.insert(idx+1, "{")
            strList.insert(idx+1, sqrtPart)
    return strList

def barRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize bar-like elements.
    
    This involves placing left, right braces out of bar-like elements, if do not exist,
    placing left, right braces inside of bar-like elements, if do not exist.
    Latter one will assume only string element right next to 'bar-like' element as its content.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Bar-like element regualrized string list.
    '''
    idx = 0
    while idx < len(strList):
        elem = strList[idx]
        #print("In barRegularizer, idx: " + str(idx) + ", elem: " + elem)
        if re.match("^(vec|dyad|acute|grave|dot|ddot|bar|hat|check|arch|tilde|BOX)$", elem) != None:
            if strList[idx+1] != '{':
                innerContent = strList[idx+1]
                strList.insert(idx+1, '{')
                strList.insert(idx+3, '}')
            if strList[idx-1] != '{':
                #leftBraceLocation = idx+1
                rightBraceLocation = idx+2
                while True:
                    if strList[rightBraceLocation] != '}':
                        rightBraceLocation = rightBraceLocation + 1
                    else:
                        break
                strList.insert(rightBraceLocation + 1, '}')
                strList.insert(idx-1, '{')
                idx = idx + 1
        idx = idx + 1
    return strList

def fracRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize fractions.
    
    This involves replacing "over" to "frac", adding braces to "frac" if there isn't.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Fractions regualrized string list.
    '''
    for idx, elem in enumerate(strList):
        if re.match("^.+over.+$", elem) != None:
            '''
            Case when divider and numerator are all sticked together to keyword.
            '''
            fracLocation = elem.find("over")
            beforePart = elem[0:fracLocation]
            fracPart = elem[fracLocation:fracLocation+4]
            remainderPart = elem[fracLocation+4:]
            del strList[idx]
            strList.insert(idx, "\\frac")
            strList.insert(idx+1, "}")
            strList.insert(idx+1, remainderPart)
            strList.insert(idx+1, "{")
            strList.insert(idx+1, "}")
            strList.insert(idx+1, beforePart)
            strList.insert(idx+1, "{")
        elif re.match("^over.+$", elem) != None:
            '''
            Case when numerator is seperated from keyword.
            '''
            fracLocation = elem.find("over")
            fracPart = elem[fracLocation:fracLocation+4]
            remainderPart = elem[fracLocation+4:]
            if strList[idx-1] == "}":
                del strList[idx]
                strList.insert(idx, "}")
                strList.insert(idx, remainderPart)
                strList.insert(idx, "{")
                strList.insert(idx-3, "\\frac")
            else:
                beforePart = strList[idx-1]
                del strList[idx]
                del strList[idx-1]
                strList.insert(idx-1, "\\frac")
                strList.insert(idx, "}")
                strList.insert(idx, remainderPart)
                strList.insert(idx, "{")
                strList.insert(idx, "}")
                strList.insert(idx, beforePart)
                strList.insert(idx, "{")
        elif re.match("^over$", elem) != None:
            '''
            Case when numerator and divider are both seperated from keyword.
            '''
            if strList[idx-1] != "}":
                strList.insert(idx-1, "{")
                strList.insert(idx+1, "}")
                del strList[idx+2]
                strList.insert(idx-1, "\\frac")
                if strList[idx+3] != "{":
                    strList.insert(idx+5, "{")
                    strList.insert(idx+5, "}")
            else:
                del strList[idx]
                strList.insert(idx-3, "\\frac")
                if strList[idx+1] != "{":
                    strList.insert(idx+1, "{")
                    strList.insert(idx+3, "}")
    return strList

def limRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize limits.
    
    This involves adding curly braces if needed, and seperating necessary parts.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Limits regualrized string list.
    '''
    for idx, elem in enumerate(strList):
        if re.match("^lim$", elem) != None:
            target = strList[idx+1]
            if re.match("^_.+$", elem) != None:
                underbar = target[0]
                arrowLocation = elem.find("->")
                beforeArrow = elem[1:arrowLocation]
                afterArrow = elem[arrowLocation+2:]
                del strList[idx+1]
                strList.insert(idx+1, underbar)
                strList.insert(idx+2, "}")
                strList.insert(idx+2, afterArrow)
                strList.insert(idx+2, beforeArrow)
                strList.insert(idx+2, "{")
        elif re.match("^lim_.+->.+$", elem) != None:
            limPart = elem[0:3]
            arrowLocation = elem.find("->")
            beforeArrow = elem[4:arrowLocation]
            arrowPart = elem[arrowLocation:arrowLocation+2]
            afterArrow = elem[arrowLocation+2:]
            del strList[idx]
            strList.insert(idx, "\\"+limPart)
            strList.insert(idx+1, "}")
            strList.insert(idx+1, afterArrow)
            strList.insert(idx+1, arrowPart)
            strList.insert(idx+1, beforeArrow)
            strList.insert(idx+1, "_{")
    return strList

def sumRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize limits.
    
    This involves adding curly braces if needed, and seperating parts.
    Sum is just for representation, this regularizer regularizes Sum, Integral and if needed, more equations that has same format.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Limits regularized string list.
    '''
    regularizationTarget = ["sum", "int"]
    for rt in regularizationTarget:
        #print(rt)
        idx = 0
        #for idx, elem in enumerate(strList):
        while idx < len(strList):
            elem = strList[idx]
            #print(elem)
            if re.match("^" + rt + "_.+\^.+$", elem) != None:
                print("All sticked together")
                print(strList)
                print(idx)
                '''
                Case when 'sum', lower and upper part are all sticked together.
                ex) sum_k=1^n
                '''
                underbarLocation = elem.find("_")
                caretLocation = elem.find("^")
                sumPart = elem[0:3]
                lowerPart = elem[underbarLocation:caretLocation]
                upperPart = elem[caretLocation:]
                print("sumPart: " + sumPart + ", lowerPart: " + lowerPart + ", upperPart: " + upperPart)
                if lowerPart[1] != "{":
                    #lowerPart = "_{" + lowerPart[1:] + "}"
                    lowerPartLst = ["_", "{", lowerPart[1:], "}"]
                if upperPart[1] != "{":
                    #upperPart = "^{" + upperPart[1:] + "}"
                    upperPartLst = ["^", "{", upperPart[1:], "}"]
                del strList[idx]
                strList.insert(idx, "\\"+rt)
                if rt == "int":
                    strList.insert(idx+1, "\\,")
                #strList.insert(idx+1, upperPart)
                strList = insertList(idx+1, strList, upperPartLst)
                #strList.insert(idx+1, lowerPart)
                strList = insertList(idx+1, strList, lowerPartLst)
                idx = idx + 1
            elif re.match("^.+" + rt + "_.+\^.+$", elem) != None:
                print("All sticked together + Additional text.")
                print(strList)
                print(idx)
                '''
                Case when all sticked together, and there are additional text before 'sum'.
                ex) M=sum_k=1^n
                '''
                underbarLocation = elem.find("_")
                caretLocation = elem.find("^")
                sumLocation = elem.find(rt)
                beforePart = elem[0:sumLocation]
                sumPart = elem[sumLocation:sumLocation+3]
                lowerPart = elem[underbarLocation:caretLocation]
                upperPart = elem[caretLocation:]
                print("sumPart: " + sumPart + ", lowerPart: " + lowerPart + ", upperPart: " + upperPart)
                if lowerPart[1] != "{":
                    #lowerPart = "_{" + lowerPart[1:] + "}"
                    lowerPartLst = ["_", "{", lowerPart[1:], "}"]
                if upperPart[1] != "{":
                    #upperPart = "^{" + upperPart[1:] + "}"
                    upperPartLst = ["^", "{", upperPart[1:], "}"]
                del strList[idx]
                strList.insert(idx, beforePart)
                if rt == "int":
                    strList.insert(idx+1, "\\,")
                #strList.insert(idx+1, upperPart)
                strList = insertList(idx+1, strList, upperPartLst)
                #strList.insert(idx+1, lowerPart)
                strList = insertList(idx+1, strList, lowerPartLst)
                strList.insert(idx+1, sumPart)
                print(strList)
            elif re.match("^.*" + rt + "$", elem) != None:
                '''
                Case when keyword 'sum' is seperated.
                '''
                target = strList[idx+1]
                sumLocation = elem.find(rt)
                beforePart = elem[0:sumLocation]
                sumPart = elem[sumLocation:]
                if re.match("^_.+\^.+$", target) != None:
                    print("Lower and upper sticked together.")
                    print(strList)
                    print(idx)
                    '''
                    Case when lower and upper part is sticked together.
                    '''
                    underbarLocation = target.find("_")
                    caretLocation = target.find("^")
                    lowerPart = target[0:caretLocation]
                    lowerPartLst = []
                    upperPart = target[caretLocation:]
                    upperPartLst = []
                    if lowerPart[1] != "{":
                        #lowerPart = "_{" + lowerPart[1:] + "}"
                        lowerPartLst = ["_", "{", lowerPart[1:], "}"]
                    if upperPart[1] != "{":
                        #upperPart = "^{" + upperPart[1:] + "}"
                        upperPartLst = ["^", "{", upperPart[1:], "}"]
                    print("sumPart: " + sumPart + ", lowerPart: " + lowerPart + ", upperPart: " + upperPart)
                    del strList[idx]
                    #strList.insert(idx, beforePart)
                    #strList.insert(idx+1, sumPart)
                    strList.insert(idx, sumPart)
                    #del strList[idx+2]
                    del strList[idx+1]
                    if rt == "int":
                        #strList.insert(idx+2, "\\,")
                        strList.insert(idx+1, "\\,")
                    #strList.insert(idx+2, upperPart)
                    #strList = insertList(idx+2, strList, upperPartLst)
                    strList = insertList(idx+1, strList, upperPartLst)
                    #strList.insert(idx+2, lowerPart)
                    #strList = insertList(idx+2, strList, lowerPart)
                    strList = insertList(idx+1, strList, lowerPartLst)
                    #if rt == "int":
                        #idx = idx + 5
                    #else:
                        #idx = idx + 4
                    idx = idx + 1
                elif re.match("^_.+$", target) != None:
                    print("Lower and upper seperated.")
                    print(strList)
                    print(idx)
                    '''
                    Case when lower and upper parts are seperated.
                    '''
                    upperTarget = strList[idx+2]
                    upperPart = "^{}"
                    lowerPart = ""
                    upperPartLst = ["^", "{", "}"]
                    lowerPartLst = []
                    if re.match("^\^.+$", upperTarget) != None:
                        '''
                        Case when upper part exists.
                        '''
                        if upperTarget[1] != "{":
                            #upperPart = "^{" + upperTarget[1:] + "}"
                            upperPartLst = ["^", "{", upperTarget[1:], "}"]
                        #else:
                            #upperPart = upperTarget
                    if target[1] != "{":
                        #lowerPart = "_{" + target[1:] + "}"
                        lowerPartLst = ["_", "{", target[1:], "}"]
                    print("sumPart: " + sumPart + ", lowerPart: " + lowerPart + ", upperPart: " + upperPart)
                    del strList[idx]
                    #strList.insert(idx, beforePart)
                    #strList.insert(idx+1, sumPart)
                    strList.insert(idx, sumPart)
                    #del strList[idx+2]
                    del strList[idx+1]
                    #strList.insert(idx+2, lowerPart)
                    #del strList[idx+3]
                    #if rt == "int":
                        #strList.insert(idx+3, "\\,")
                    #strList.insert(idx+3, upperPart)
                    if rt == "int":
                        #strList.insert(idx+2, "\\,")
                        strList.insert(idx+1, "\\,")
                    #strList = insertList(idx+2, upperPartLst)
                    strList = insertList(idx+1, upperPartLst)
                    #strList = insertList(idx+2, lowerPartLst)
                    strList = insertList(idx+1, lowerPartLst)
                    #if rt == "int":
                        #idx = idx + 5
                    #else:
                        #idx = idx + 4
                    idx = idx + 1
                elif target == "_":
                    print(strList)
                    print(idx)
                    '''
                    Case when lower part is seperated from keyword.
                    '''
                    rightCurlyBrace = idx+3
                    isMatched = 1
                    #while strList[rightCurlyBrace] != "}":
                    while isMatched > 0:
                        if strList[rightCurlyBrace] == "{":
                            isMatched = isMatched + 1
                        elif strList[rightCurlyBrace] == "}":
                            isMatched = isMatched - 1
                        rightCurlyBrace = rightCurlyBrace + 1
                    rightCurlyBrace = rightCurlyBrace - 1
                    print("rightCurlyBrace: " + str(rightCurlyBrace))
                    if strList[rightCurlyBrace+1] == "^":
                        '''
                        Case when upper part has curly braces.
                        '''
                        del strList[idx]
                        #strList.insert(idx, beforePart)
                        #strList.insert(idx+1, sumPart)
                        strList.insert(idx, sumPart)
                        #idx = idx + 2
                        idx = idx + 1
                    else:
                        '''
                        Case when upper part does not have curly braces.
                        '''
                        upperPart = strList[rightCurlyBrace+1]
                        upperPart = "^{" + upperPart[1:] + "}"
                        upperPartLst = ["^", "{", upperPart[1:], "}"]
                        del strList[idx]
                        #strList.insert(idx, beforePart)
                        #strList.insert(idx+1, sumPart)
                        strList.insert(idx, sumPart)
                        #del strList[rightCurlyBrace+2]
                        del strList[rightCurlyBrace+1]
                        #strList.insert(rightCurlyBrace+2, upperPart)
                        if rt == "int":
                            #strList.insert(rightCurlyBrace+2, "\\,")
                            strList.insert(rightCurlyBrace+1, "\\,")
                        #strList = insertList(rightCurlyBrace+2, strList, upperPartLst)
                        strList = insertList(rightCurlyBrace+1, strList, upperPartLst)
                        #if rt == "int":
                            #strList.insert(rightCurlyBrace+3, "\\,")
                        #if rt == "int":
                            #idx = rightCurlyBrace + 2
                        #else:
                            #idx = rightCurlyBrace + 1
                        idx = idx + 1
                else:
                    idx = idx + 1
            else:
                idx = idx + 1
    print("strList: " + str(strList))
    return strList
