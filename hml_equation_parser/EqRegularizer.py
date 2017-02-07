from typing import Dict, Tuple, List
import json, codecs
import os
import re

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