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
        # Initialize document input path, indexer and directory (for 1_3)
        import os
        from pathlib import Path
        filepath = os.path.join(Path(__file__).parent.parent.parent.parent.parent.parent.parent, input_file)
        print("File path",filepath, "Doc", input_file)
        self.doc = filepath
        self.indexer = None
        self.dir = None
        pass

    def read_txt_file(self,input_file):
        # open file and read lines
        with open(input_file) as f1:
            # Assumes Docs.txt satisfies One document per line in the input file,
            # b) The first token in each line be the document id
            # read file and store lines into list
            docs = f1.readlines()
        return docs

    def q1_1(self, query):
        # get index using lupyne
        indexer = self.get_index(self.doc)
        # Convert from list to space separated to search for words separated by space.
        query_str = " ".join(query)
        ans = []
        # search for query terms in contents of documents
        hits = indexer.search(query_str, field='contents')
        for hit in hits:
            # add Documents to answer
            # Document includes Docid and score
            d = Document(hit['docid'], hit.score)
            ans.append(d)
            # print("1-1", hit['docid'], hit.score)
        # Sort answer by descending order of score (redundant since searcher does it)
        ans.sort(key=lambda x: x.score, reverse=True)
        return ans

    def q1_2_a(self, query):
        indexer= self.get_index(self.doc)
        # Parse query string to include AND between terms.
        query_str = " AND ".join(query)
        ans = []
        # search for BOOLEAN query term1 AND term2 in contents of documents
        hits = indexer.search(query_str, field='contents')
        for hit in hits:
            # add Documents to answer
            d = Document(hit['docid'], hit.score)
            ans.append(d)
        # Sort answer by descending order of score
        ans.sort(key=lambda x: x.score, reverse=True)
        return ans

    def q1_2_b(self, query):
        indexer = self.get_index(self.doc)
        # Parse list to 'AND NOT' between terms
        query_str = " AND NOT ".join(query)
        ans = []
        hits = indexer.search(query_str, field='contents')
        for hit in hits:
            # add Documents to answer
            d = Document(hit['docid'], hit.score)
            ans.append(d)
        # Sort answer by descending order of score
        ans.sort(key=lambda x: x.score, reverse=True)
        return ans

    def q1_2_c(self, query):
        indexer = self.get_index(self.doc)
        # Search for instances within 1 word of each other using ~
        query_str = " ".join(query)
        ans = []
        # search for query terms in contents of documents
        hits = indexer.search('"'+query_str+'"'+'~1', field='contents')
        for hit in hits:
            # add Documents to answer
            d = Document(hit['docid'], hit.score)
            ans.append(d)
        # Sort answer by descending order of score
        ans.sort(key=lambda x: x.score, reverse=True)
        return ans

    def q1_3(self, query):
        # Search index in lucene syntax
        directory = self.get_directory(self.doc)
        ireader = index.DirectoryReader.open(directory)
        isearcher = search.IndexSearcher(ireader)
        analyzer = analysis.standard.StandardAnalyzer()
        # change the similarity function to ClassicSimilarity which implements tfidf
        isearcher.setSimilarity(ClassicSimilarity())
        # Parse a simple query that searches in the field "contents":
        parser = queryparser.classic.QueryParser('contents', analyzer)
        query_str = " ".join(query)
        query = parser.parse(query_str)
        # return top 10 documents
        hits = isearcher.search(query, 10).scoreDocs

        ans=[]
        # search for query terms in contents of documents
        for hit in hits:
            hit_doc = isearcher.doc(hit.doc)
            # add Documents to answer
            d = Document(hit_doc['docid'], hit.score)
            ans.append(d)
        # Sort answer by descending order of score (redundant since searcher does it, but added it just in case)
        ans.sort(key=lambda x: x.score, reverse=True)
        #print("After search of terms")
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
        docs = self.read_txt_file(input_file)
        # Assumes input file satisfies a) One document per line in the input file, b) The first token in each line be the document id,
        #    c) The rest of tokens in a line be all terms appearing in the document. d) The text is already tokenized and the tokens are normalized.
        for line in docs:
            # Split each line into 2: one for docid and the rest of the line (document contents)
            tokens = line.split(" ", 1 )
            # Extract Document Name, i.e., Doc#.
            docNo = tokens[0]
            # Add the doc# and document contents
            if len(tokens[1])>0:
                my_indexer.add(docid=docNo, contents= tokens[1])
        # close the indexer after documents read
        my_indexer.commit()
        return my_indexer

    # Returns the dictionary (part 3)
    # To set similarity function, created a new get/set method for index.
    # [not required since tf automatically computed].
    # But, best practice to make index & query use same similarity function
    def get_directory(self,doc):
        # If index not yet defined, read input_file. Else, return index
        print("Self dir before if",bool(self.dir), self.dir)
        if not bool(self.dir) :
            self.dir = self.set_directory(self.doc, self.dir)
        print("Self dir",bool(self.dir), self.dir)
        return self.dir

    # returns directory corresponding to writer.
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
