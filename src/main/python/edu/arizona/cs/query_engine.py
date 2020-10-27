from src.main.python.edu.arizona.cs.document import Document
import lucene
from lupyne import engine
from lupyne.engine import Query
from org.apache.lucene import index, search
from org.apache.lucene import analysis, document, index, queryparser, search, store, util
from org.apache.lucene.search.similarities import ClassicSimilarity
from org.apache.lucene.document import FieldType, Field
from org.apache.lucene.index import IndexOptions
lucene.initVM()


class QueryEngine:

    def __init__(self, input_file): # Temporarily removing from arguments: ,input_file
        # add your code here
        import os
        from pathlib import Path
        # print("doc",doc)
        filepath = os.path.join(Path(__file__).parent.parent.parent.parent.parent.parent.parent, input_file)
        print("File path",filepath, "Doc", input_file)
        self.doc = filepath
        self.indexer = None
        self.dir = None
        print("done with init")
        pass

    def read_txt_file(self,input_file):
        print("In read file")
        #add your code here
        with open(input_file) as f1:
            # Assumes Docs.txt satisfies One document per line in the input file,
            # b) The first token in each line be the document id
            # read file and store lines into list
            docs = f1.readlines()
            # sort the documents in lexicographical order
            docs.sort()
            # print(docs)
        return docs

    def list_to_string(self, s):
        # intialize empty string
        str1 = " "
        # return string
        return (str1.join(s))

    def q1_1(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        #doc = document.Document()
        print("In q1-1")
        indexer= self.get_index(self.doc)
        # Convert to searching for information retrieval by converting comma to space
        query_str = " ".join(query)
        print('Passing to query: contents:', query_str)
        ans=[]
        # search for query terms in contents of documents
        hits = indexer.search(query_str, field='contents')
        for hit in hits:
            print("hit is ", hit)
            print("hit docid, score",hit['docid'], hit.score)
            # add Documents to answer
            d = Document(hit['docid'], hit.score)
            ans.append(d)
        # Sort answer by descending order of score (redundant since searcher does it, but added it so that it was explicit)
        ans.sort(key=lambda x: x.score, reverse=True)
        print("After search of terms")
        return ans

    def q1_2_a(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        #doc = document.Document()
        print("In q1-2a")
        indexer= self.get_index(self.doc)
        # Convert to searching for information retrieval by converting comma to AND between terms
        query_str = " AND ".join(query)
        print('Passing to query: contents:', query_str)
        ans=[]
        # search for query terms in contents of documents
        hits = indexer.search(query_str, field='contents')
        for hit in hits:
            print("hit is ", hit)
            print("hit docid, score",hit['docid'], hit.score)
            # add Documents to answer
            d = Document(hit['docid'], hit.score)
            ans.append(d)
        # Sort answer by descending order of score
        ans.sort(key=lambda x: x.score, reverse=True)
        print("After search of terms")
        return ans


    def q1_2_b(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        #doc = document.Document()
        print("In q1-2b")
        indexer= self.get_index(self.doc)
        # Convert to searching for information retrieval by converting comma to AND between terms
        query_str = " AND NOT ".join(query)
        print('Passing to query: contents:', query_str)
        ans=[]
        # search for query terms in contents of documents
        hits = indexer.search(query_str, field='contents')
        for hit in hits:
            print("hit is 1-2b", hit)
            print("hit docid, score",hit['docid'], hit.score)
            # add Documents to answer
            d = Document(hit['docid'], hit.score)
            ans.append(d)
        # Sort answer by descending order of score
        ans.sort(key=lambda x: x.score, reverse=True)
        print("After search of terms")
        return ans

    def q1_2_c(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        # doc = document.Document()
        print("In q1-2c")
        indexer= self.get_index(self.doc)
        # Convert to searching for information retrieval by converting comma to AND between terms
        query_str = " ".join(query)
        print('Passing to query: contents:', '"'+query_str+'"'+'~1')
        ans=[]
        # search for query terms in contents of documents
        hits = indexer.search('"'+query_str+'"'+'~1', field='contents')
        for hit in hits:
            print("hit is 1-2c", hit)
            print("hit docid, score",hit['docid'], hit.score)
            # add Documents to answer
            d = Document(hit['docid'], hit.score)
            ans.append(d)
        # Sort answer by descending order of score
        ans.sort(key=lambda x: x.score, reverse=True)
        print("After search of terms")
        return ans

    def q1_3(self, query):
        # This is just sample code. add your actual code here.
        # The Document class we provided is just a dummy wrapper over Lucene document.
        # the document you use must be the Lucene document i.e
        # doc = document.Document()

        # Search index
        directory = self.get_directory(self.doc)
        ireader = index.DirectoryReader.open(directory)
        isearcher = search.IndexSearcher(ireader)
        analyzer = analysis.standard.StandardAnalyzer()
        # change the similarity function
        isearcher.setSimilarity(ClassicSimilarity())

        # Parse a simple query that searches for "text":
        parser = queryparser.classic.QueryParser('contents', analyzer)
        query_str = " ".join(query)
        query = parser.parse(query_str)
        hits = isearcher.search(query, 10).scoreDocs

        ans=[]
        # search for query terms in contents of documents
        for hit in hits:
            print("hit is 1-3", hit)
            print("hit docid, score",hit.doc, hit.score)
            hitDoc = isearcher.doc(hit.doc)
            print("hitdoc id",hitDoc['docid'])
            # add Documents to answer
            d = Document(hitDoc['docid'], hit.score)
            ans.append(d)
        # Sort answer by descending order of score (redundant since searcher does it, but added it just in case)
        ans.sort(key=lambda x: x.score, reverse=True)
        print("After search of terms")
        ireader.close()
        directory.close()
        return ans

    # Returns the index
    def get_index(self,doc):
        # If index not yet defined, read input_file. Else, return index
        print("Self writer before if",bool(self.indexer), self.indexer)
        if not bool(self.indexer) :
            self.indexer = self.set_index(self.doc, self.indexer )
        print("Self writer",bool(self.indexer), self.indexer)
        return self.indexer

    # creates inverted index, consisting of dictionary and postings (index the documents that each term occurs in)
    def set_index(self, input_file, my_indexer):
        # create index
        my_indexer = engine.Indexer()
        # create a stored docid field: Not-tokenized
        my_indexer.set('docid', engine.Field.String, stored=True)
        # create a stored contents field that is tokenized
        my_indexer.set('contents',engine.Field.Text)
        my_doc = None
        #my_dictionary = {}
        #postings = []
        docs = self.read_txt_file(input_file)
        # Assumes input file satisfies a) One document per line in the input file, b) The first token in each line be the document id,
        #    c) The rest of tokens in a line be all terms appearing in the document. d) The text is already tokenized and the tokens are normalized.
        for line in docs:
            # Split each line into 2: one for docid and the rest of the line
            tokens = line.split(" ", 1 )
            # Extract Document Name, i.e., Doc#.
            docNo = tokens[0]
#            my_doc = Document(docNo, 0)
            # Add the doc# and document contents
            if len(tokens[1])>0:
                my_indexer.add(docid=docNo, contents= tokens[1])
            print("Added: docId:", docNo, " contents ", tokens[1])
        # close the writer after documents read
        my_indexer.commit()
        return my_indexer

    # Returns the dictionary (part 3)
    def get_directory(self,doc):
        # If index not yet defined, read input_file. Else, return index
        print("Self dir before if",bool(self.dir), self.dir)
        if not bool(self.dir) :
            self.dir = self.set_directory(self.doc, self.dir)
        print("Self dir",bool(self.dir), self.dir)
        return self.dir

    # creates inverted index, consisting of dictionary and postings (index the documents that each term occurs in)
    def set_directory(self, input_file, my_directory):
        ## PyLucene code
        # Initialize Standard analyzer & Index writer
        my_analyzer = analysis.standard.StandardAnalyzer()
        # Store the index in memory:
        my_directory = store.RAMDirectory()
        my_config = index.IndexWriterConfig(my_analyzer)
        my_config.setSimilarity(ClassicSimilarity())
        my_writer = index.IndexWriter(my_directory, my_config)
        # # Setting up String field for content we don't want tokenized
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.DOCS)   # only want documents returned

        # # Setting up Text field for content we want tokenized
        t2 = FieldType()
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS) #  using IndexOptions.DOCS_AND_FREQS_AND_POSITIONS since care about frequencies and positions to generate ranking
        # # create in-memory index
        # my_indexer2 = engine.Indexer()
        # # create a stored docid field: Not-tokenized
        # my_indexer2.set('docid', engine.Field.String, stored=True)
        # # create a stored contents field that is tokenized
        # my_indexer2.set('contents',engine.Field.Text)
        #my_dictionary = {}
        #postings = []
        docs = self.read_txt_file(input_file)
        # Assumes input file satisfies a) One document per line in the input file, b) The first token in each line be the document id,
        #    c) The rest of tokens in a line be all terms appearing in the document. d) The text is already tokenized and the tokens are normalized.
        for line in docs:
            # Split each line into 2: one for docid and the rest of the line
            tokens = line.split(" ", 1 )
            # Extract Document Name, i.e., Doc#.
            docNo = tokens[0]
            my_doc = document.Document()
            # Add the doc# and document contents
            if len(tokens[1])>0:
                my_doc.add(Field('docid', docNo , t1))
                my_doc.add(Field('contents', tokens[1], t2))
                my_writer.addDocument(my_doc)
                print("Added: docId:", docNo, " contents ", tokens[1])
        # close the writer after documents read
        my_writer.commit()
        my_writer.close()
        return my_directory



# def main():
#     # can comment this out later
#     input_path = "src/main/resources/input.txt"
#     print("In 7-1-1")
#     query = ["information", "retrieval"]
#     ans_q1_1 = QueryEngine(input_path).q1_1(query)
#     assert type(ans_q1_1) is not None
#     assert type(ans_q1_1) is list
#     assert len(ans_q1_1) > 0
#     print("Answer in main is",ans_q1_1)
#     print("len of ansq11", len(ans_q1_1))
#     assert len(ans_q1_1) == 2
#     doc_names_q1 = ["Doc1", "Doc2"]
#     counter = 0
#     for docs in ans_q1_1:
#         assert doc_names_q1[counter] == docs.doc_id
#         counter = counter + 1
#     print("done with Q1")
#
#     print("In 7-1-2a")
#     query = ["information", "retrieval"]
#     ans = QueryEngine(input_path).q1_2_a(query) ## changed from QueryEngine(input_path).
#     assert type(ans) is not None
#     assert type(ans) is list
#     assert len(ans) > 0
#     assert len(ans) == 2
#     expected_doc_names = ["Doc1", "Doc2"]
#     counter1 = 0
#     for docs in ans:
#         assert expected_doc_names[counter1] == docs.doc_id
#         counter1 = counter1 + 1
#     print("In 7-1-2b")
#     query = ["information", "retrieval"]
#     ans=QueryEngine(input_path).q1_2_b(query)
#     assert type(ans) is not None
#     assert type(ans) is list
#     assert len(ans) == 0
#
#     print("In 7-1-2c")
#     query = ["information", "retrieval"]
#     ans = QueryEngine(input_path).q1_2_c(query)
#     assert type(ans) is not None
#     assert type(ans) is list
#     assert len(ans) > 0
#     assert len(ans) == 1
#
#     expected_doc_names = ["Doc1"]
#     counter1 = 0
#
#     for docs in ans:
#         assert expected_doc_names[counter1] == docs.doc_id
#         counter1 = counter1 + 1
#
#     print("In 7-1-3")
#     query = ["information", "retrieval"]
#     ans=QueryEngine(input_path).q1_3(query)
#     assert type(ans) is not None
#     assert type(ans) is list
#     assert len(ans) > 0
#     assert len(ans) == 2
#
#     expected_doc_names = ["Doc1", "Doc2"]
#     counter1 = 0
#
#     for docs in ans  :
#         assert expected_doc_names[counter1]== docs.doc_id
#         counter1 = counter1 + 1
#
# if __name__ == "__main__":
#     main()
