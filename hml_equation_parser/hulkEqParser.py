from typing import List
import json
import codecs
import os
from .hulkReplaceMethod import (replaceAllMatrix, replaceAllBar, replaceRootOf,
                                replaceFrac, replaceAllBrace)
from .EqRegularizer import (sqrtRegularizer, barRegularizer, fracRegularizer,
                            limRegularizer,  sumRegularizer, matchCurlyBraces,
                            inEqualityRegularizer, bracketRegularizer,
                            expRegularizer, fontRegularizer, backslashRemover,
                            textRegularizer, matchBraces)

with codecs.open(os.path.join(os.path.dirname(__file__), "convertMap.json"),
                 "r", "utf8") as f:
    convertMap = json.load(f)


def hmlEquation2latex(hmlEqStr: str) -> str:
    '''
    Convert hmlEquation string to latex string.

    Parameters
    ----------------------
    hmlEqStr : str
        A hml equation string to be converted.

    Returns
    ----------------------
    out : str
        A converted latex string.
    '''
    def replaceBracket(strList: List[str]) -> List[str]:
        '''
        "\left {"  -> "\left \{"
        "\right }" -> "\right \}"
        '''
        for i, string in enumerate(strList):
            if string == r'{':
                if i > 0 and strList[i-1] == r'\left':
                    strList[i] = r'\{'
            if string == r'}':
                if i > 0 and strList[i-1] == r'\right':
                    strList[i] = r'\}'
        return strList

    strConverted = hmlEqStr.replace('`', ' ').replace('~', ' ')
    strConverted = strConverted.replace('{', ' { ')
    strConverted = strConverted.replace('}', ' } ')
    strConverted = strConverted.replace('(', ' ( ')
    strConverted = strConverted.replace(')', ' ) ')
    strConverted = strConverted.replace('&', ' & ')

    strList = strConverted.split(' ')

    strList = list(filter(lambda x: x != "", strList))

    strList = bracketRegularizer(strList)
    #strList = fontRegularizer(strList)

    strList = matchCurlyBraces(strList)
    strList = inEqualityRegularizer(strList)
    strList = textRegularizer(strList)

    strList = sqrtRegularizer(strList)
    strList = expRegularizer(strList, True)
    strList = barRegularizer(strList)
    strList = fracRegularizer(strList)
    strList = limRegularizer(strList)
    strList = sumRegularizer(strList)
    strList = expRegularizer(strList, False)
    strList = fontRegularizer(strList)
    strList = matchBraces(strList)

    for key, candidate in enumerate(strList):
        if candidate in convertMap["convertMap"]:
            strList[key] = convertMap["convertMap"][candidate]
        elif candidate in convertMap["middleConvertMap"]:
            strList[key] = convertMap["middleConvertMap"][candidate]

    strList = [string for string in strList if len(string) != 0]
    strList = replaceBracket(strList)
    strList = backslashRemover(strList)

    strConverted = ' '.join(strList)


    #strConverted = replaceFrac(strConverted)
    strConverted = replaceRootOf(strConverted)
    strConverted = replaceAllMatrix(strConverted)
    strConverted = replaceAllBar(strConverted)
    strConverted = replaceAllBrace(strConverted)

    return strConverted
