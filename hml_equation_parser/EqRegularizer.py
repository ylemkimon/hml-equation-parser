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

def fontRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize fonts.
    Target font is roman, bold, italic.
    This regularizer also deals with special keywords, such as 'sin', 'cos', 'ln' and so on.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Font regularized string list.
    '''
    targetFonts = ["rm", "bold", "it"]
    for tf in targetFonts:
        for idx, elem in enumerate(strList):
            if re.match("^" + tf + ".+$", elem) != None:
                afterPart = elem[len(tf):]
                del strList[idx]
                strList.insert(idx, "}")
                strList.insert(idx, afterPart)
                strList.insert(idx, "{")
                if tf == "rm":
                    strList.insert(idx, "\\mathrm")
                elif tf == "bold":
                    strList.insert(idx, "\\mathbf")
                elif tf == "it":
                    strList.insert(idx, "\\mathit")
            elif re.match("^" + tf + "$", elem) != None:
                target = strList[idx+1]
                if (target != "{"):
                    del strList[idx]
                    if tf == "rm":
                        strList.insert(idx, "\\mathrm")
                    elif tf == "bold":
                        strList.insert(idx, "\\mathbf")
                    elif tf == "it":
                        strList.insert(idx, "\\mathit")
                    strList.insert(idx+2, "}")
                    strList.insert(idx+1, "{")
    specialKeywords = ["sin", "cos", "tan", "ln", "log", "alpha", "beta", "gamma", "theta", "pi", "sigma"]
    for sk in specialKeywords:
        for idx, elem in enumerate(strList):
            if re.match("^.+"+sk+".+$", elem) != None:
                keywordLocation = elem.find(sk)
                beforePart = elem[0:keywordLocation]
                keywordPart = elem[keywordLocation:keywordLocation+len(sk)]
                afterPart = elem[keywordLocation+len(sk):]
                del strList[idx]
                strList.insert(idx, afterPart)
                strList.insert(idx, "\\"+keywordPart)
                strList.insert(idx, beforePart)
            elif re.match("^"+sk+".+$", elem) != None:
                afterPart = elem[len(sk):]
                del strList[idx]
                strList.insert(idx, afterPart)
                strList.insert(idx, "\\"+sk)
            elif re.match("^"+sk+"$", elem) != None:
                del strList[idx]
                strList.insert(idx, "\\"+sk)
    matrixKeywords = ["matrix", "cases"]
    for mk in matrixKeywords:
        for idx, elem in enumerate(strList):
            if re.match("^.+"+mk+"$", elem) != None:
                keywordLocation = elem.find(mk)
                beforePart = elem[0:keywordLocation]
                del strList[idx]
                strList.insert(idx, mk)
                strList.insert(idx, beforePart)
                rightBracketLocation = idx + 2
                bracketMatch = 0
                while True:
                    if strList[rightBracketLocation] == '}':
                        bracketMatch = bracketMatch - 1
                        if bracketMatch == 0:
                            break
                        else:
                            rightBracketLocation = rightBracketLocation + 1
                    elif strList[rightBracketLocation] == '{':
                        bracketMatch = bracketMatch + 1
                        rightBracketLocation = rightBracketLocation + 1
                    else:
                        rightBracketLocation = rightBracketLocation + 1
                strList.insert(rightBracketLocation+1, "}")
                strList.insert(idx, "{")
            elif re.match("^" + mk + "$", elem) != None:
                if strList[idx-1] != "{":
                    rightBracketLocation = idx + 1
                    bracketMatch = 0
                    while True:
                        if strList[rightBracketLocation] == '}':
                            bracketMatch = bracketMatch - 1
                            if bracketMatch == 0:
                                break
                            else:
                                rightBracketLocation = rightBracketLocation + 1
                        elif strList[rightBracketLocation] == '{':
                            bracketMatch = bracketMatch + 1
                            rightBracketLocation = rightBracketLocation + 1
                        else:
                            rightBracketLocation = rightBracketLocation + 1
                    strList.insert(rightBracketLocation+1, "}")
                    strList.insert(idx, "{")
    return strList

def bracketRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize bracket format.
    'LEFT', 'RIGHT' signs and their equivalents are converted to regularized form.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Bracket regularized list of strings.
    '''
    for idx, elem in enumerate(strList):
        if re.match('^(left|LEFT)(\(|\{|\[)$', elem) != None:
            directionKeyword = "\\left"
            bracketKeyword = elem[4:]
            del strList[idx]
            strList.insert(idx, bracketKeyword)
            strList.insert(idx, directionKeyword)
        elif re.match('^(left|LEFT)(\(|\{|\[).+$', elem) != None:
            directionKeyword = "\\left"
            bracketKeyword = elem[4]
            afterPart = elem[5:]
            del strList[idx]
            strList.insert(idx, afterPart)
            strList.insert(idx, bracketKeyword)
            strList.insert(idx, directionKeyword)
        elif re.match('^(right|RIGHT)(\)|\}|\])$', elem) != None:
            directionKeyword = "\\right"
            bracketKeyword = elem[5:]
            del strList[idx]
            strList.insert(idx, bracketKeyword)
            strList.insert(idx, directionKeyword)
        elif re.match('^(right|RIGHT)(\)|\}|\]).+$', elem) != None:
            directionKeyword = "\\right"
            bracketKeyword = elem[5]
            afterPart = elem[6:]
            del strList[idx]
            strList.insert(idx, afterPart)
            strList.insert(idx, bracketKeyword)
            strList.insert(idx, directionKeyword)
    return strList

def inEqualityRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize inequalities.
    
    This converts non ASCII characters to Latex inequality keywords.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Inequality regularized string list.
    '''

    for idx, elem in enumerate(strList):
        print(idx, elem)
        if elem == "＞":
            del strList[idx]
            strList.insert(idx, ">")
        elif elem == "＜":
            del strList[idx]
            strList.insert(idx, "<")
        elif re.match("^.+le.+$", elem) != None and elem != "\\leq" and elem != "\\left":
            inequalityLocation = elem.find("le")
            beforePart = elem[0:inequalityLocation]
            afterPart = elem[inequalityLocation+2:]
            del strList[idx]
            strList.insert(idx, afterPart)
            strList.insert(idx, "\\leq")
            strList.insert(idx, beforePart)
        elif re.match("^le.+$", elem) != None:
            afterPart = elem[2:]
            del strList[idx]
            strList.insert(idx, afterPart)
            strList.insert(idx, "\\leq")
        elif re.match("^.+le$", elem) != None:
            inequalityLocation = elem.find("le")
            beforePart = elem[0:inequalityLocation]
            del strList[idx]
            strList.insert(idx, "\\leq")
            strList.insert(idx, beforePart)
        elif elem == "le":
            del strList[idx]
            strList.insert(idx, "\\leq")
        elif re.match("^.+ge.+$", elem) != None and elem != "\\geq":
            inequalityLocation = elem.find("ge")
            beforePart = elem[0:inequalityLocation]
            afterPart = elem[inequalityLocation+2:]
            del strList[idx]
            strList.insert(idx, afterPart)
            strList.insert(idx, "\\geq")
            strList.insert(idx, beforePart)
        elif re.match("^ge.+$", elem) != None:
            afterPart = elem[2:]
            del strList[idx]
            strList.insert(idx, afterPart)
            strList.insert(idx, "\\geq")
        elif re.match("^.+ge$", elem) != None:
            print("Before part exist. GEQ")
            inequalityLocation = elem.find("ge")
            beforePart = elem[0:inequalityLocation]
            del strList[idx]
            strList.insert(idx, "\\geq")
            strList.insert(idx, beforePart)
            print(strList)
        elif elem == "ge":
            del strList[idx]
            strList.insert(idx, "\\geq")
    return strList

def expRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize exponents and subscripts.
    
    This involves breaking exponents and "^" keyword, subscripts and "_" keyword and adding curly braces if dose not exist.

    Parameters
    ----------------------
    strList : List[str]
        List of strings, splitted by whitespace from hml equation string.
    
    Returns
    ----------------------
    out : List[str]
        Exponent and subscript regularized string list.
    '''
    regularizationTarget = ["^", "_"]
    for rt in regularizationTarget:
        for idx, elem in enumerate(strList):
            if re.match("^.+" + "\\" + rt + ".+$", elem) != None and "{" not in elem and "}" not in elem:
                exponentLocation = elem.find(rt)
                beforePart = elem[0:exponentLocation]
                afterPart = elem[exponentLocation+1:]
                del strList[idx]
                strList.insert(idx, "}")
                strList.insert(idx, afterPart)
                strList.insert(idx, "{")
                strList.insert(idx, rt)
                strList.insert(idx, beforePart)
            elif re.match("^" + "\\" + rt + ".+$", elem) != None and "{" not in elem and "}" not in elem:
                afterPart = elem[1:]
                del strList[idx]
                strList.insert(idx, "}")
                strList.insert(idx, afterPart)
                strList.insert(idx, "{")
                strList.insert(idx, rt)
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
    targetKeywords = ["vec", "dyad", "acute", "grave", "dot", "ddot", "bar", "hat", "check", "arch", "tilde", "BOX"]
    for targetKeyword in targetKeywords:
        idx = 0
        while idx < len(strList):
            elem = strList[idx]
            #print("In barRegularizer, idx: " + str(idx) + ", elem: " + elem)
            if re.match("^" + targetKeyword + "$", elem) != None:
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
            elif re.match("^" + targetKeyword + ".+$", elem) != None:
                afterPart = elem[len(targetKeyword):]
                del strList[idx]
                strList.insert(idx, "}")
                strList.insert(idx, afterPart)
                strList.insert(idx, "{")
                strList.insert(idx, targetKeyword)
                if strList[idx-1] != "{":
                    strList.insert(idx+4, "}")
                    strList.insert(idx, "{")
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
                leftCurlyBrace = idx-2
                isMatched = 1
                while isMatched > 0:
                    if strList[leftCurlyBrace] == "}":
                        isMatched = isMatched + 1
                    elif strList[leftCurlyBrace] == "{":
                        isMatched = isMatched - 1
                    leftCurlyBrace = leftCurlyBrace - 1
                leftCurlyBrace = leftCurlyBrace + 1
                del strList[idx]
                strList.insert(leftCurlyBrace, "\\frac")
                if strList[idx+1] != "{":
                    strList.insert(idx+1, "{")
                    strList.insert(idx+3, "}")
    return strList

def limRegularizer (strList: List[str]) -> List[str]:
    '''
    Regularize limits.
    
    This involves adding curly braces if needed, and seperating necessary parts.
    Rightarrows written as "->" are also regularized.

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
            del strList[idx]
            strList.insert(idx, "\\lim")
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
                strList.insert(idx+2, "\\rightarrow")
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
            strList.insert(idx+1, "\\rightarrow")
            strList.insert(idx+1, beforeArrow)
            strList.insert(idx+1, "_{")
        elif re.match("^lim_$", elem) != None:
            del strList[idx]
            strList.insert(idx, "_")
            strList.insert(idx, "\\lim")
        if re.match("^.+->.+$", elem) != None:
            arrowLocation = elem.find("->")
            beforePart = elem[0:arrowLocation]
            afterPart = elem[arrowLocation+2:]
            del strList[idx]
            strList.insert(idx, afterPart)
            strList.insert(idx, "\\rightarrow")
            strList.insert(idx, beforePart)
        elif re.match("^.+->$", elem) != None:
            arrowLocation = elem.find("->")
            beforePart = elem[0:arrowLocation]
            del strList[idx]
            strList.insert(idx, "\\rightarrow")
            strList.insert(idx, beforePart)
        elif re.match("^->.+$", elem) != None:
            afterPart = elem[2:]
            del strList[idx]
            strList.insert(idx, afterPart)
            strList.insert("\\rightarrow")
        elif re.match("^->$", elem) != None:
            del strList[idx]
            strList.insert(idx, "\\rightarrow")
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
