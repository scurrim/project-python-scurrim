from src.main.python.edu.arizona.cs.document import Document

class QueryEngine:

    def __init__(self,input_file):
        # add your code here
        pass

    def read_txt_file(self,input_file):
        #add your code here
        docs=None
        return docs

    def q1_1(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        #doc = document.Document()
        ans=[]
        # first argument must be of type document.Document()
        ans1 = Document("Doc1",1.10)
        ans2 = Document("Doc1",1.14)
        ans.append(ans1)
        ans.append(ans2)
        return ans

    def q1_2_a(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        #doc = document.Document()
        ans=[]
        # first argument must be of type document.Document()
        ans1 = Document("Doc2",1.30)
        ans2 = Document("Doc2",1.24)
        ans.append(ans1)
        ans.append(ans2)
        return ans


    def q1_2_b(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        #doc = document.Document()
        ans = []
        # first argument must be of type document.Document()
        ans1 = Document("Doc2", 1.30)
        ans.append(ans1)
        return ans

    def q1_2_c(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        # doc = document.Document()
        ans = []
        # first argument must be of type document.Document()
        ans1 = Document("Doc2", 1.30)
        ans.append(ans1)
        return ans

    def q1_3(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        # doc = document.Document()
        ans = []
        # first argument must be of type document.Document()
        ans1 = Document("Doc3", 1.30)
        ans2 = Document("Doc2", 1.24)
        ans.append(ans1)
        ans.append(ans2)
        return ans

