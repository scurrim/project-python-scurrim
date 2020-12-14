INDEX_DIR = "QueryEngine.Index"
INDEX_DIR_ENG = "QueryEngine.Index.EnglishAnalyzer"
INDEX_DIR_EL = "QueryEngine.Index.EnglishAnalyzer_Spacy"


#from src.main.python.edu.arizona.cs.document import Document
import lucene
from lucene import *
#import os, shutil

from lupyne import engine
from lupyne.engine import Query
from org.apache.lucene import index, search
from org.apache.lucene import analysis, document, index, queryparser, search, store, util
from org.apache.lucene.search.similarities import ClassicSimilarity
from org.apache.lucene.document import FieldType, Field
from org.apache.lucene.index import IndexOptions
# from org.apache.lucene import morphology #analyzer.MorhpologyFilter
lucene.initVM()
# import os
# from pathlib import Path
import glob
import time
import os, sys
import json

import java
from java.nio.file import Paths
# from java.lang import System
# from java.text import DecimalFormat
# from java.util import Arrays
# import lucene
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.search import IndexSearcher, TermQuery, MatchAllDocsQuery
from org.apache.lucene.store import FSDirectory, SimpleFSDirectory
from org.apache.lucene.index import (IndexWriter, IndexReader,
                                     DirectoryReader, Term,
                                     IndexWriterConfig)
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.facet import DrillSideways, DrillDownQuery
from org.apache.lucene.facet import (Facets, FacetField, FacetResult,
                                     FacetsConfig, FacetsCollector)
from org.apache.lucene.facet.taxonomy import FastTaxonomyFacetCounts
from org.apache.lucene.facet.taxonomy.directory import (DirectoryTaxonomyWriter,
                                                        DirectoryTaxonomyReader)
import spacy
import re

# adapted code from FacetExample.py that is included in pylucene
class QueryEngine:

    def __init__(self, input_path): # Temporarily removing from arguments: ,input_file
        self.txt_files = glob.glob(input_path+"en*.txt")
        self.TITLE = "title"
        self.TEXT = "text"
        self.directory = input_path
        # Store the index on disk:
        self.in_directory = SimpleFSDirectory.open(Paths.get(os.path.join(self.directory, INDEX_DIR)))
        self.in_directory_English = SimpleFSDirectory.open(Paths.get(os.path.join(self.directory, INDEX_DIR_ENG)))
        self.in_directory_English_lemma = SimpleFSDirectory.open(Paths.get(os.path.join(self.directory, INDEX_DIR_EL)))
        self.queries = []
        self.sp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        self.sp_bodies_lemma = []
        self.sp_bodies_pos = []
        self.query_lemma = ""
        self.query_pos = ""
        self.prec_at_1 =0
        pass

    # Create basic index (no lemmatization / stemmer)
    def createIndex_simple(self,input_files):
        # open file and read lines
        docs = []
        cur_title = ""
        cur_body = ""
        cur_category = []
        file_counter = 0
        ip_file_counter = 1
        # Initialize Standard analyzer & Index writer
        my_analyzer = analysis.standard.StandardAnalyzer()
        my_config = index.IndexWriterConfig(my_analyzer)
        # Set ClassicSimilarity for tf-idf
        #my_config.setSimilarity(ClassicSimilarity())
        my_writer = index.IndexWriter(self.in_directory, my_config)

        # # Setting up Title field for content we want tokenized
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(True)
        t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)   # only want documents returned
        # Setting up Body field for content we want tokenized
        t2 = FieldType()
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS) #  using IndexOptions.DOCS_AND_FREQS_AND_POSITIONS since care about frequencies and positions to generate ranking
        # Setting up Categories field for content we want tokenized
        t3 = FieldType()
        t3.setStored(True)
        t3.setTokenized(True)
        t3.setIndexOptions(IndexOptions.DOCS) #  using IndexOptions.DOCS_AND_FREQS_AND_POSITIONS since care about frequencies and positions to generate ranking
        nDocsAdded = 0
        print("List of input files is",input_files)
        for input_file in input_files:
            with open(input_file, 'r', encoding='utf8') as f1:
                # Assumes all input documents contain documents that are separated by titles denoted by  [[xxx]]
                my_line = f1.readline()
                while my_line:
                    if my_line.startswith("[[") and my_line.rstrip().endswith("]]"):
                        if cur_title != "":
                            # add previous document to index when next document
                            doc = Document()
                            doc.add(Field(self.TITLE, cur_title, t1))
                            doc.add(Field(self.TEXT, cur_body, t2))
                            doc.add(Field("Categories", self.listToString(cur_category), t3))
                            my_writer.addDocument(doc)
                            # increment counters and reset document variables
                            nDocsAdded += 1
                            cur_title = ""
                            cur_body = ""
                            cur_category = []
                            file_counter += 1
                        # store current title
                        cur_title = my_line[2:-3]
                    # store categories as a string
                    elif my_line.startswith("CATEGORIES:"):
                        # categories are in a line that starts with CATEGORIES and each category is separated by ", "
                        cur_category = my_line[11:].strip().split(", ")
                    # store body of document
                    else:
                        cur_body += my_line
                    #read next line
                    my_line = f1.readline()
                file_counter += 1
                print("File counter",file_counter) # ,"cur category",listToString(cur_category)
                # on EOF save document to index
                doc = Document()
                doc.add(Field(self.TITLE, cur_title, t1))
                doc.add(Field(self.TEXT, cur_body, t2))
                doc.add(Field("Categories", self.listToString(cur_category), t3))
                my_writer.addDocument(doc)
                cur_title = ""
                cur_body = ""
            ip_file_counter += 1
        # now safely in the provided directories: indexDir and taxoDir.
        my_writer.commit()
        my_writer.close()
        print("Indexed %d documents." % nDocsAdded)
        pass

    # Create index with stemmer [EnglishAnalyzer] (no lemmatization )
    def createIndex_Stem(self,input_files):
        cur_title = ""
        cur_body = ""
        cur_category = []
        file_counter = 0
        ip_file_counter = 1
        # Initialize PorterStemmer analyzer & Index writer
        my_analyzer = analysis.en.EnglishAnalyzer()
        my_config = index.IndexWriterConfig(my_analyzer)
        my_config.setSimilarity(ClassicSimilarity())
        my_writer = index.IndexWriter(self.in_directory_English, my_config)
        # Setting up Title field for content we want tokenized
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(True)
        t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        # Setting up Body field for content we want tokenized
        t2 = FieldType()
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS) #  using IndexOptions.DOCS_AND_FREQS_AND_POSITIONS since care about frequencies and positions to generate ranking
        # Setting up Categories field for content we want tokenized
        t3 = FieldType()
        t3.setStored(True)
        t3.setTokenized(True)
        t3.setIndexOptions(IndexOptions.DOCS)
        nDocsAdded = 0
        print("List of input files is",input_files)
        for input_file in input_files:
            with open(input_file, 'r', encoding='utf8') as f1:
                # Assumes all input documents contain documents that are separated by titles denoted by  [[xxx]]
                my_line = f1.readline()
                while my_line:
                    if my_line.startswith("[[") and my_line.rstrip().endswith("]]"):
                        if cur_title != "":
                            doc = Document()
                            doc.add(Field(self.TITLE, cur_title, t1))
                            doc.add(Field(self.TEXT, cur_body, t2))
                            doc.add(Field("Categories", self.listToString(cur_category), t3))
                            my_writer.addDocument(doc)
                            nDocsAdded += 1
                            cur_body = ""
                            cur_category = []
                            file_counter += 1
                        cur_title = my_line[2:-3]
                    elif my_line.startswith("CATEGORIES:"):
                        cur_category = my_line[11:].strip().split(", ")
                    else:
                        cur_body += my_line
                    my_line = f1.readline()
                file_counter += 1
                doc = Document()
                doc.add(Field(self.TITLE, cur_title, t1))
                doc.add(Field(self.TEXT, cur_body, t2))
                doc.add(Field("Categories", self.listToString(cur_category), t3))
                my_writer.addDocument(doc)
                cur_title = ""
                cur_body = ""
            ip_file_counter += 1
        my_writer.commit()
        my_writer.close()
        print("Indexed %d documents." % nDocsAdded)
        pass

    # Create index with stemmer [EnglishAnalyzer] AND lemmatization (spacy)
    # In this version, I store documents with pre-processing (removing References and tpl tags) and after lemmatization into a file.
    # Then, store it in an index
    def createIndex_Stem_Lemma_SpacyDoc(self,input_files):
        cur_title = ""
        cur_body = ""
        cur_category = []
        file_counter = 0
        ip_file_counter = 1
        nDocsAdded = 0
        titles = []
        bodies = []
        categories = []
        ignore_line = 0
        print("List of input files is",input_files)
        for input_file in input_files:
            with open(input_file, 'r', encoding='utf8') as f1:
                # Assumes all input documents contain documents that are separated by titles denoted by  [[xxx]]
                my_line = f1.readline()
                while my_line:
                    if my_line.startswith("[[") and my_line.rstrip().endswith("]]"):
                        ignore_line = 0
                        if cur_title != "":
                            titles.append(cur_title)
                            bodies.append(cur_body)
                            categories.append(self.listToString(cur_category))
                            nDocsAdded += 1
                            file_counter += 1
                            cur_body = ""
                            cur_category = []
                        cur_title = my_line[2:-3]
                    # ignores lines after references to the end of the document
                    elif ignore_line == 1:
                        my_line = f1.readline()
                        continue
                    elif my_line.startswith("CATEGORIES:"):
                        cur_category = my_line[11:].strip().split(", ")
                    # ignore references
                    elif my_line.startswith("==References=="):
                        ignore_line = 1
                    elif my_line.startswith("=="):
                        my_line = my_line.strip("=")
                        cur_body += my_line
                    else:
                        cur_body += my_line
                    my_line = f1.readline()
                file_counter += 1
                ignore_line = 0
                #print("File counter", file_counter) # ,"cur category",listToString(cur_category)
                titles.append(cur_title)
                bodies.append(cur_body)
                categories.append(self.listToString(cur_category))
                # finally add the document to the index
                cur_title = ""
                cur_body = ""
            ip_file_counter += 1
        titles.append(cur_title)
        bodies.append(self.cleanText(cur_body))
        categories.append(self.listToString(cur_category))
        print("Just before spacy, len bodies:", len(bodies))
        self.convertTextToLemmaToString(bodies)
        print("Finished spacy; now writing to json")
        json_list_of_docs =[]
        for i in range(len(titles)):
            doc = [titles[i], self.sp_bodies_lemma[i],categories[i], self.sp_bodies_pos[i]]
            json_list_of_docs.append(doc)
        self.writeJSONToDisk(json_list_of_docs, self.directory+"wiki_spacy_lemma_pos.json")
        print("Indexed %d documents with spacy." % nDocsAdded)
        pass




    def createIndex(self):
        # index the sample documents
        self.createIndex_simple(self.txt_files)

    def createIndex_eng(self):
        # index the sample documents
        self.createIndex_Stem(self.txt_files)

    def createIndex_eng_lemma(self):
        # index the sample documents
        self.createIndex_Stem_Lemma(self.txt_files)


    def readQueries(self):
        #print("In readQueries")
        # retrieve queries
        query_file = self.directory + "questions.txt"
        query_count = 0
        with open(query_file, 'r', encoding='utf8') as f1:
            # Assumes questions.txt has CATEGORY, query and answer followed by blank line as structure
            my_line = f1.readline()
            while my_line:
                query_category = my_line.strip()
                query_cat = self.clean_query_cat(query_category)
                my_line = f1.readline()
                query_text = my_line.strip()
                query_txt = self.clean_query(query_text)
                # if "Wayside" in my_line:
                #     print(my_line)
                my_line = f1.readline()
                query_answer = my_line.strip()
                # print("Query category", query_category, "query text", query_text, "query_ans", query_answer)
                # all three need to be populated to evaluate results
                if query_cat != "" and query_txt != "" and query_answer!= "":
                    query_tuple = [query_cat, query_txt, query_answer]
                    self.queries.append(query_tuple)
                    query_count += 1
                my_line = f1.readline()
                my_line = f1.readline()
        return self.queries

    def runSimple(self, tfidf):
        print("In runSimple")
        answers = []
        if not self.queries:
            self.readQueries()
        count_correct = 0
        count_correct_queryText =0
        for query in self.queries:
            answer = self.SearchSimple(query, tfidf)
            count_correct += answer[5]
            count_correct_queryText += answer[7]
            answers.append(answer)
        print("Total questions", len(answers), "total correct", count_correct)
        pass

    def runSimple_Eng(self, tfidf):
        print("In runSimpleEng")
        answers = []
        count_correct_queryText = 0
        if not self.queries:
            self.readQueries()
        count_correct = 0
        for query in self.queries:
            answer = self.SearchSimple_Eng(query, tfidf)
            count_correct += answer[5]
            count_correct_queryText += answer[7]
            answers.append(answer)
        print("Total questions", len(answers), "total correct", count_correct)
        pass

    def runSimple_Eng_Lemma(self, tfidf):
        print("In runSimpleEngLemma")
        answers = []
        count_correct_queryText = 0
        if not self.queries:
            self.readQueries()
        count_correct = 0
        for query in self.queries:
            answer = self.SearchSimple_Eng_Lemma(query, tfidf)
            count_correct += answer[5]
            count_correct_queryText += answer[7]
            answers.append(answer)
        print("Total questions", len(answers), "total correct", count_correct)
        pass

    def runMult_Eng(self, tfidf):
        print("Starting run with Best Index and 100 questions")
        answers = []
        count_correct_queryText = 0
        self.prec_at_1 = 0
        if not self.queries:
            self.readQueries()
        count_correct = 0
        for query in self.queries:
            answer = self.SearchSimple_Eng_mult(query, tfidf)
            count_correct += answer[5]
            count_correct_queryText += answer[7]
            answers.append(answer)
        print("Total questions", len(answers), "total correct (precision at 1)",self.prec_at_1)
        pass

    def SearchSimple(self, query, tfidf):
        # # Search index in lucene syntax
        directory = self.in_directory
        ireader = index.DirectoryReader.open(directory)
        isearcher = search.IndexSearcher(ireader)
        analyzer = analysis.standard.StandardAnalyzer()
        isMatch = False
        isMatchCat = False
        # change the similarity function to ClassicSimilarity which implements tfidf
        if (tfidf):
            isearcher.setSimilarity(ClassicSimilarity())
        # # Parse a simple query that searches in the field "contents":
        parser = queryparser.classic.QueryParser(self.TEXT, analyzer)
        # extract query text from query object
        query_text = parser.parse(query[1])
        # # return top 1 documents
        # remove special characters & convert to lower case so that AND, OR, NOT etc. are not considered as keywords
        query_cat_text = parser.parse(query[1] + " " + query[0].title())
        hits = isearcher.search(query_text, 1).scoreDocs
        hits_cat = isearcher.search(query_cat_text, 1).scoreDocs
        ans=[]
        # search for query terms in contents of documents
        for hit in hits:
            hit_doc = isearcher.doc(hit.doc)
            if hit_doc[self.TITLE] in query[2] :
                isMatch = True
            # add Documents to answer
            ans = [query[0], query[1], query[2], hit_doc[self.TITLE], hit.score, isMatch, hit.score, isMatch, hit.score, isMatch]
            if hit.score < hits_cat[0].score:
                hit_cat_doc = isearcher.doc(hits_cat[0].doc)
                if hit_cat_doc[self.TITLE] in query[2] :
                    isMatchCat = True
                ans = [query[0], query[1], query[2], hit_cat_doc[self.TITLE], hits_cat[0].score, isMatchCat, hit.score, isMatch]
            # if isMatch or isMatchCat:
            #     print("SS Query-answer ",ans)
        ireader.close()
        return ans

    def SearchSimple_Eng(self, query, tfidf):
        # # Search index in lucene syntax
        directory = self.in_directory_English
        ireader = index.DirectoryReader.open(directory)
        isearcher = search.IndexSearcher(ireader)
        analyzer = analysis.en.EnglishAnalyzer()
        isMatch = False
        isMatchCat = False
        # change the similarity function to ClassicSimilarity which implements tfidf
        if (tfidf):
            isearcher.setSimilarity(ClassicSimilarity())
        # # Parse a simple query that searches in the field "contents":
        parser = queryparser.classic.QueryParser(self.TEXT, analyzer)
        # extract query text from query object
        query_text = parser.parse(query[1])
        # # return top 1 documents
        # remove special characters & convert to lower case so that AND, OR, NOT etc. are not considered as keywords
        query_cat_text = parser.parse(query[1] + " " + query[0].title())
        hits = isearcher.search(query_text, 1).scoreDocs
        hits_cat = isearcher.search(query_cat_text, 1).scoreDocs
        ans=[]
        # search for query terms in contents of documents
        for hit in hits:
            hit_doc = isearcher.doc(hit.doc)
            if hit_doc[self.TITLE] in query[2]:
                isMatch = True
            # add Documents to answer
            ans = [query[0], query[1], query[2], hit_doc[self.TITLE], hit.score, isMatch, hit.score, isMatch]
            if hit.score < hits_cat[0].score:
                hit_cat_doc = isearcher.doc(hits_cat[0].doc)
                if hit_cat_doc[self.TITLE] in query[2] :
                    isMatchCat = True
                ans = [query[0], query[1], query[2], hit_cat_doc[self.TITLE], hits_cat[0].score, isMatchCat, hit.score, isMatch]
            # if isMatch or isMatchCat:
            #     print("SSE Query-answer ", ans)
        ireader.close()
        return ans


    def SearchSimple_Eng_Lemma(self, query, tfidf):
        # # Search index in lucene syntax
        directory = self.in_directory_English_lemma
        ireader = index.DirectoryReader.open(directory)
        isearcher = search.IndexSearcher(ireader)
        analyzer = analysis.en.EnglishAnalyzer()
        isMatch = False
        isMatchNoun = False
        isMatchCat = False
        # change the similarity function to ClassicSimilarity which implements tfidf
        if (tfidf):
            isearcher.setSimilarity(ClassicSimilarity())
        parser = queryparser.classic.QueryParser(self.TEXT, analyzer)
        self.convertQueryToLemmaToString(query[1])
        query_text = re.sub(r'[0-9]+', '', self.query_lemma)
        query_txt = query_text.split(" ")
        query_pos = self.query_pos.split(" ")
        query_sub =""
        # Extract nouns
        for i in range(len(query_pos)):
            # token is PROPN / NOUN
            if query_pos[i] == "PROPN" or query_pos[i] == "NOUN" or query_pos[i] == "-PRON-":
                if query_sub=="":
                    query_sub = query_txt[i]
                else:
                    query_sub += " "+ query_txt[i]
        #stopwords = "a an and are as at be but by for if in into is it no not of on or such that the their then there these they this to was will with"
        # if two words or less or the number of POS <> length of text
        if query_sub =="" or len(query_sub)<=2 or len(query_pos)!= len(query_txt):
            query_sub = self.query_lemma
        #     print("Query noun phr was empty")
        # else:
        #     print("query sub",query_sub)
        # print("querysub",query_sub, "lemma ", self.query_lemma, query[1])
        query_text = parser.parse(self.query_lemma)
        # noun phrases only
        query_text_noun = parser.parse(query_sub)
        query_cat_text = parser.parse(self.query_lemma + " " + query[0].title())

        hits = isearcher.search(query_text, 1).scoreDocs
        hits_noun = isearcher.search(query_text_noun, 1).scoreDocs
        hits_cat = isearcher.search(query_cat_text, 1).scoreDocs
        ans=[]
        # search for query terms in contents of documents
        for hit in hits:
            hit_doc = isearcher.doc(hit.doc)
            if hit_doc[self.TITLE] in query[2] :
                isMatch = True
            # add Documents to answer
            ans = [query[0], query[1], query[2], hit_doc[self.TITLE], hit.score, isMatch, hit.score, isMatch]
            if hit.score < hits_noun[0].score:
                hit_noun_doc = isearcher.doc(hits_noun[0].doc)
                if hit_noun_doc[self.TITLE] in query[2]  :
                    isMatchNoun = True
                ans = [query[0], query[1], query[2], hit_noun_doc[self.TITLE], hits_noun[0].score, isMatchNoun, query_sub, hit.score, isMatch]
            if hit.score < hits_cat[0].score  and hits_noun[0].score < hits_cat[0].score :
                hit_cat_doc = isearcher.doc(hits_cat[0].doc)
                if hit_cat_doc[self.TITLE] in query[2] :
                    isMatchCat = True
                ans = [query[0], query[1], query[2], hit_cat_doc[self.TITLE], hits_cat[0].score, isMatchCat, hit.score, isMatch, hits_noun[0].score, isMatchNoun]
            # if isMatch or isMatchCat or isMatchNoun:
            #     print("SSEL Query-answer ", ans)
        ireader.close()
        return ans

    def SearchSimple_Eng_mult(self, query, tfidf):
        # # Search index in lucene syntax
        directory = self.in_directory_English
        ireader = index.DirectoryReader.open(directory)
        isearcher = search.IndexSearcher(ireader)
        analyzer = analysis.en.EnglishAnalyzer()
        isMatch = False
        isMatchCat = False
        # change the similarity function to ClassicSimilarity which implements tfidf
        if (tfidf):
            isearcher.setSimilarity(ClassicSimilarity())
        # # Parse a simple query that searches in the field "contents":
        parser = queryparser.classic.QueryParser(self.TEXT, analyzer)
        # extract query text from query object
        query_text = parser.parse(query[1])
        # if "Wayside" in query[1] or "wayside" in query[1]:
        #     print("q1 query_text",query[1], query_text)
        query_cat_text = parser.parse(query[1] + " " +query[0].title())
        hits = isearcher.search(query_text, 10).scoreDocs
        hits_cat = isearcher.search(query_cat_text, 10).scoreDocs
        answers=[]
        ans =[]
        j = 0
        topTenCorrect = False
        #test_ans = query[2]
        # search for query terms in contents of documents
        query_txt = query[1].split()
        pot_ans = []
        pot_ans_overlap_question = 0
        for i in range(len(hits)):
            hit_doc = isearcher.doc(hits[i].doc)
            hit_cat_doc = isearcher.doc(hits_cat[i].doc)
            ansSet = False
            # exclude category and not self.contains_category_term(hit_doc[self.TITLE], query[0])
            # to test for special characters
            # if not self.contains_unnatural_terms(hit_doc[self.TITLE]) or not self.contains_unnatural_terms(hit_cat_doc[self.TITLE]) : 25
            #if not self.answer_too_long(hit_doc[self.TITLE]) or not self.answer_too_long(hit_cat_doc[self.TITLE]) : 26
            #if hit_doc[self.TITLE] not in query[1] or hit_cat_doc[self.TITLE] not in query[1]: 26
            #if not self.contains_category_term(hit_doc[self.TITLE], query[0]) or hit_cat_doc[self.TITLE] not in query[0]:
            if  (not self.contains_unnatural_terms(hit_doc[self.TITLE]) and not self.answer_too_long(hit_doc[self.TITLE]) and hit_doc[self.TITLE] not in query[0] ) or (not self.contains_unnatural_terms(hit_cat_doc[self.TITLE])  and not self.answer_too_long(hit_cat_doc[self.TITLE]) and hit_cat_doc[self.TITLE] not in query[0]):
                # print("Query ans ", query[2], "too_long ", self.answer_too_long(hit_doc[self.TITLE]), " unnat terms ", self.contains_unnatural_terms(query[2]), " categ", self.contains_category_term(query[2], query[0]), "cat too long",  self.answer_too_long(hit_cat_doc[self.TITLE]) )
                # hit_doc = isearcher.doc(hits[i].doc)
                #if not self.contains_unnatural_terms(hit_doc[self.TITLE]) :
                # if not self.answer_too_long(hit_doc[self.TITLE]):
                #if hit_doc[self.TITLE] not in query[0]:
                if (not self.contains_unnatural_terms(hit_doc[self.TITLE]) and not self.answer_too_long(hit_doc[self.TITLE]) and hit_doc[self.TITLE] not in query[1]):
                    ansSet = True
                    # Return to this when done
                    pot_ans = hit_doc[self.TITLE].split(" ")
                    for p in pot_ans:
                        if p in query_txt:
                            pot_ans_overlap_question += 1
                    # if at least 75% of answer words in question then not right answer
                    # if hit_doc[self.TITLE] in query[2]:
                    if not pot_ans_overlap_question/len(pot_ans) >= 0.75 :
                        if hit_doc[self.TITLE] in query[2] :
                        #print("Hit_doc title",hit_doc[self.TITLE])
                            isMatch = True
                            topTenCorrect = True
                        ans = [query[0], query[1], query[2], hit_doc[self.TITLE], hits[i].score, isMatch, hits[i].score, isMatch]
                    else:
                        ansSet = False
                    # add Documents to answer
                # hit_cat_doc = isearcher.doc(hits_cat[i].doc)
                #if not self.contains_unnatural_terms(hit_cat_doc[self.TITLE]) :
                # if not self.answer_too_long(hit_cat_doc[self.TITLE]):
                # if hit_cat_doc[self.TITLE] not in query[1]:
                # if not self.answer_too_long(hit_cat_doc[self.TITLE]) :
                if (not self.contains_unnatural_terms(hit_cat_doc[self.TITLE])  and not self.answer_too_long(hit_cat_doc[self.TITLE]) and hit_cat_doc[self.TITLE] not in query[1]):
                    pot_ans_overlap_question = 0
                    pot_ans = hit_cat_doc[self.TITLE].split(" ")
                    for p in pot_ans:
                        if p in query_txt:
                            pot_ans_overlap_question += 1
                    if not pot_ans_overlap_question / len(pot_ans) >= 0.75:
                        if (hit_cat_doc[self.TITLE] in query[2] and ((hits[i].score < hits_cat[i].score) or ansSet == False)) :
                            # Return to this when done (hit_cat_doc[self.TITLE] in query[2] or pot_ans_overlap_question/len(pot_ans) >= 0.75 ) and ((hits[i].score < hits_cat[i].score) or ansSet == False):
                            isMatchCat = True
                            topTenCorrect = True
                        # elif hit_cat_doc[self.TITLE] not in query[2] and ((hits[i].score < hits_cat[i].score) or ansSet == False):
                        #     topTenCorrect = False
                            ans = [query[0], query[1], query[2], hit_cat_doc[self.TITLE], hits_cat[i].score, isMatchCat, hits[i].score, isMatch]
                #print("SSEM Query-answer ",i, ans)
                if topTenCorrect == True:
                    #print("Matched in top 10 for ",j, query[2], ans)
                    if j == 0:
                        self.prec_at_1 += 1
                    break
                if pot_ans_overlap_question < 0.75 :
                    j += 1
                pot_ans_overlap_question = 0
            # else:
                 # print("Query ans ", query[2], "too_long ", self.answer_too_long(query[2]) , " unnat terms ", self.contains_unnatural_terms(query[2]), " categ" , self.contains_category_term(query[2], query[0]))
        ireader.close()
        return ans


    def cleanText(self, doc):
        clean_doc = re.sub(r"\[tpl\](.*)\[/tpl\]", "", doc)
        return clean_doc

    def convertTextToLemmaToString(self, texts):
        noDocs = 0
        noTokens =0
        for text in self.sp.pipe(texts):
            #doc = self.sp.pipe(text)
            noDocs += 1
            body_lemma = []
            body_pos = []
            for token in text:
                if token.pos_ != 'PUNCT' and token.text != '\n':
                    body_lemma.append(token.lemma_)
                    body_pos.append(token.pos_)
                    noTokens += 1
            self.sp_bodies_lemma.append(self.listToString(body_lemma))
            self.sp_bodies_pos.append(self.listToString(body_pos))
            if noDocs % 5000 == 0:
                print("No docs & time is", noDocs, time.time())
        print("No of Docs ", noDocs, " Total No of tokens ", noTokens)
        pass

    def convertQueryToLemmaToString(self, text):
        self.query_lemma = ""
        self.query_pos = ""
        noTokens = 0
        text.replace("--"," ")
        text.replace("'", "")
        text.replace('"', ' ')
        tokens = self.sp(text)
        for token in tokens:
            if token.pos_ != 'PUNCT' and token.text != '\n' and token.text != '' : #and not token.lemma_.startswith("'") and token.lemma_ != "-PRON-"
                if (self.query_lemma==""):
                    self.query_lemma = token.lemma_
                    self.query_pos = token.pos_
                else:
                    self.query_lemma += " " + token.lemma_
                    self.query_pos += " " + token.pos_
                noTokens += 1
        self.query_lemma.replace('  ', ' ')
        self.query_pos.replace('  ', ' ')
        self.query_lemma.strip()
        self.query_pos.strip()
        pass


    def writeJSONToDisk(spacy_docs, filename):
        with open(filename, "w") as f1:
            json.dump(spacy_docs, f1)

    def readJSONFromDisk(self, filename):
        spacy_docs = []
        with open(filename, "r") as f1:
            spacy_docs = json.load(f1)
        return spacy_docs


    # Python program to convert a list to string using join() function
    def listToString(self, s):
        # initialize an empty string
        str1 = " "
        # return string
        return (str1.join(s))

    # Jeopardy answers are a max of 4 words
    def answer_too_long(self, input_string):
        too_long = False
        max_len = 4
        input_array = input_string.split()
        #print("Input array", input_array, "len", len(input_array))
        if len(input_array) > max_len:
            too_long = True
        # print('Too long', input_string)
        return too_long

    def contains_unnatural_terms(self, input_string):
        # list of things in bad answers but not in good answers
        bad_terms = ['(']
        contains_word = False
        my_input_string = input_string
        for term in bad_terms:
            if term in my_input_string:
                contains_word = True
                contains_word = True
                # print('bad term', input_string)
        return contains_word

    def contains_category_term(self, input_string, category):
        # a term in the category will never be answer
        my_input_string = input_string.lower()
        contains_category = False
        c = category.lower().split(" ")
        # print("input string", input_string, category )
        for i in range(len(c)):
            print("cat term is",c[i], "input_str", my_input_string)
            if c[i] in my_input_string :
                contains_category = True
        return contains_category


    def clean_query(self, input_string):
        checked_string = input_string
        for chk in ['!', '\\', '&', '--', "(Alex: We'll give you the ", "You give us the ", "You tell us the ",
                    'Alex:', ' and ', ' not ', ' or ', '(', ')', '"', ',', ':', '. ', '--', ' ', ' ']:
            if chk in checked_string:
                checked_string = checked_string.replace(chk, " ")
        final_string = checked_string.strip()
        return final_string

    def clean_query_cat(self, input_string):
        checked_string = input_string
        for chk in ['!', '\\', '&']:
            if chk in checked_string:
                checked_string = checked_string.replace(chk, " ")
        final_string = checked_string.strip()
        return final_string

    # Read from spacy file and write to index
    def createIndex_Stem_Lemma_SpacyIndex(self):
        print("In create index method")
        spacy_file = self.directory+"wiki_spacy_lemma_pos.json"
        my_analyzer = analysis.en.EnglishAnalyzer()
        my_config = index.IndexWriterConfig(my_analyzer)
        my_config.setSimilarity(ClassicSimilarity())
        my_writer = index.IndexWriter(self.in_directory_English_lemma, my_config)
        # # Setting up Title field for content we want tokenized
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(True)
        t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)   # only want documents returned
        # Setting up Body field for content we want tokenized
        t2 = FieldType()
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS) #  using IndexOptions.DOCS_AND_FREQS_AND_POSITIONS since care about frequencies and positions to generate ranking
        # Setting up Categories field for content we want tokenized
        t3 = FieldType()
        t3.setStored(True)
        t3.setTokenized(True)
        t3.setIndexOptions(IndexOptions.DOCS) #  using IndexOptions.DOCS_AND_FREQS_AND_POSITIONS since care about frequencies and positions to generate ranking
        # Setting up Body POS  field for content we want tokenized
        t4 = FieldType()
        t4.setStored(True)
        t4.setTokenized(True)
        t4.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS) #  using IndexOptions.DOCS_AND_FREQS_AND_POSITIONS since care about frequencies and positions to generate ranking

        nDocsAdded = 0
        docs = self.readJSONFromDisk(spacy_file)
        print("Len of file is", len(docs))
        for doc in docs:
            title = doc[0]
            lemma = doc[1]
            category = doc[2]
            pos = doc[3]
            doc = Document()

            doc.add(Field(self.TITLE, title, t1))
            doc.add(Field(self.TEXT, lemma, t2))
            doc.add(Field("Categories", category, t3))
            doc.add(Field("POS", pos, t4))
            my_writer.addDocument(doc)
            nDocsAdded +=1
        # now safely in the provided directories: indexDir and taxoDir.
        my_writer.commit()
        my_writer.close()
        print("Indexed %d documents with spacy." % nDocsAdded)
        pass

def main():
    input_path = "src/main/resources/"
    q1 = QueryEngine(input_path)
    # # print("With tfidf")
    # # No stemming; standard analyzer Tokenizes based on a sophisticated grammar that recognizes email addresses, acronyms,
    # # Chinese-Japanese-Korean characters, alphanumerics, and more. It also lowercases and removes stop words.
    # q1.runSimple(True)
    # # To add stemming
    # q1.runSimple_Eng(True)
    # # To add stemming and lemmatization
    # q1.runSimple_Eng_Lemma(True)
    # q1.runSimple_Eng(True)
    # # Additional improvements over stemming . Also allows one to look at top 10 to do error analyses
    # q1.runMult_Eng(True)
    print("With BM25")
    # #q1.runSimple_Eng_Lemma(False)
    # q1.runSimple(False)
    # q1.runSimple_Eng(False)
    # q1.runSimple_Eng_Lemma(False)
    # Additional improvements over stemming
    q1.runMult_Eng(False)




if __name__ == '__main__':
    main()

