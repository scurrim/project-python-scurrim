#you should change this document class to use: from org.apache.lucene import  document
import lucene
from org.apache.lucene import document

class Document:
    def __init__(self, doc_id, score):
        #first argument must be of type document.Document() and you should get docid using doc.get("docid")
        self.doc_id = doc_id
        self.score=score

    def get(self, s):
        str =""
        if s == "docid":
            str = self.doc_id
        if s == "score":
            str = self.score
        return str







