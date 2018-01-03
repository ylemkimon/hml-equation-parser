from typing import Tuple, Union
import os
from xml.etree.ElementTree import fromstring, Element, ElementTree
from .hulkEqParser import hmlEquation2latex
import json
import codecs

with codecs.open(os.path.join(os.path.dirname(__file__), "config.json"),
                 "r", "utf8") as f:
    config = json.load(f)


def parseHml(fileName: str) -> Tuple[ElementTree, ElementTree]:
    '''
    Parse .hml document and make ElementTrees for question and solution.

    Parameters
    ----------------------
    fileName : str
        fileName to be parsed.
    Returns
    ----------------------
    out : (ElementTree, ElementTree)
        Tuple of parsed ElementTree objects for question and solution,
        respectively.
    '''
    with codecs.open(fileName, 'r', 'utf8') as f:
        xmlText = f.read()

    hwpml = fromstring(xmlText)
    body = hwpml.find("BODY")
    section = body.find("SECTION")

    docRoot = Element(config["NodeNames"]["root"])
    solRoot = Element(config["NodeNames"]["root"])

    def parseParagraphNode(root: Element, paragraph: Element) -> None:
        '''
        Parse and make ElementTree of paragraph(P) node.
        '''
        paragraphNode = Element(config["NodeNames"]["paragraph"])

        text = paragraph.find("TEXT")
        if text is not None:
            for child in text:
                if child.tag == "CHAR":
                    value = child.text or ''
                    for charChild in child:
                        if charChild.tag == 'LINEBREAK':
                            value += '<br>\n'
                        else:
                            print("unsupported char tag: {}"
                                  .format(charChild.tag))
                        value += charChild.tail or ''

                    if value is not None:
                        leafNode = Element(config["NodeNames"]["char"])
                        leafNode.text = value
                        paragraphNode.append(leafNode)

                elif child.tag == "EQUATION":
                    script = child.find("SCRIPT")
                    value = script.text

                    leafNode = Element(config["NodeNames"]["equation"])
                    leafNode.text = value
                    paragraphNode.append(leafNode)

                elif child.tag == "ENDNOTE":  # 해설 미주
                    paralist = child.find("PARALIST")
                    paragraphs = paralist.findall("P")

                    for paragraph in paragraphs:
                        parseParagraphNode(solRoot, paragraph)

                else:
                    print("unsupported tag: {}".format(child.tag))

            root.append(paragraphNode)

    for paragraph in section.findall("P"):
        parseParagraphNode(docRoot, paragraph)

    return ElementTree(docRoot), ElementTree(solRoot)


def convertEquation(doc: ElementTree) -> str:
    '''
    Convert equation with sample ElementTree.
    '''
    for paragraph in doc.findall(config["NodeNames"]["paragraph"]):
        for child in paragraph:
            if child.tag == config["NodeNames"]["equation"]:
                child.text = hmlEquation2latex(child.text)
    return doc


def extract2HtmlStr(doc: ElementTree) -> str:
    '''
    Convert sample ElementTree to html
    '''
    def convertSpace2nbsp(string: str) -> str:
        return string.replace(' ', r'&nbsp;')
    htmlStringList = []

    for paragraph in doc.findall(config["NodeNames"]["paragraph"]):
        paragraphStringList = []

        for child in paragraph:
            if child.tag == config["NodeNames"]["char"]:
                paragraphStringList.append(convertSpace2nbsp(child.text))
            elif child.tag == config["NodeNames"]["equation"]:
                paragraphStringList.append("$" + child.text + "$")
        paragraphString = ''.join(paragraphStringList)
        htmlStringList.append(paragraphString)
    return config["htmlHeader"] + '<br>\n'.join(htmlStringList) +\
        config["htmlFooter"]


if __name__ == '__main__':
    import sys
    script, hmlDoc, dst = sys.argv

    doc = parseHml(hmlDoc)
    doc = convertEquation(doc)
    doc.write(dst + '.xml')

    with codecs.open(dst + ".html", "w", "utf8") as f:
        f.write(extract2HtmlStr(doc))
