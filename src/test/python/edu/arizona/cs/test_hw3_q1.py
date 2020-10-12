from unittest import TestCase
from src.main.python.edu.arizona.cs.query_engine import QueryEngine
from src.main.python.edu.arizona.cs.document import Document

class Test_hw2_q7(TestCase):
    input_path= "src/main/resources/input.txt"

    def test_q7_1_1(self):

        query = ["information", "retrieval"]
        ans_q1_1=QueryEngine(self.input_path).q1_1(query)

        assert type(ans_q1_1) is not None
        assert type(ans_q1_1) is list
        assert len(ans_q1_1) > 0
        assert len(ans_q1_1) == 2

        doc_names_q1 = ["Doc1", "Doc2"]
        counter1 = 0

        for docs in ans_q1_1  :
            assert doc_names_q1[counter1]== docs.doc_id
            counter1 = counter1 + 1

    #
    #
    # def test_q7_1_2(self):
    #     query = "schizophrenia /4 drug"
    #     gold_q712 = [Document("Doc1", 3, 1), Document("Doc2", 1, 2), Document("Doc3", 1, 5)]
    #     ans_q712 = InvertedIndex(self.input_path).q7_1_2_a(query)
    #     assert ans_q712 is not None
    #     assert type(ans_q712) is list
    #     assert len(ans_q712) > 0
    #     assert len(ans_q712) == 3
    #
    #     for gold, ans in zip(gold_q712, ans_q712):
    #         gold.__eq__(ans)
    #
    #
    # def test_q7_2_directional(self):
    #     query = "schizophrenia /2 drug"
    #     gold_q72 = [Document("Doc2", 1, 2)]
    #     ans_q72 = InvertedIndex(self.input_path).q7_2(query)
    #
    #     assert ans_q72 is not None
    #     assert type(ans_q72) is list
    #     assert len(ans_q72) > 0
    #     assert len(ans_q72) == 1
    #
    #     for gold, ans in zip(gold_q72, ans_q72):
    #         gold.__eq__(ans)
    #
    #
