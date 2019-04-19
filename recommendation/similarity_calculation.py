import sys
import scipy.sparse

sys.path.append("..")
from utils.justeson_extractor import get_all_terms_in_doc
from job_crawler.MySQLWrapper import MySQLWrapper
import re
from typing import Tuple, List, Generator
from MySQLdb import OperationalError, IntegrityError
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors

reg_exp = '((A|N)+|((A|N)*(NP)?)(A|N)*)N'
p = re.compile(reg_exp)

bag_of_words_doc_file = "job_bag_of_words.npz"

stop_words = ["the", "this", "a", "at", "as", "all", "are", "above", "and", "only", "more", "between", "by", "to",
              "be", "is", "are", "been", "can", "can't", "did", "my"]
vectorizer = CountVectorizer(stop_words, max_df=0.95, min_df=0.05)

all_doc_list = []
all_id_list = []
with MySQLWrapper() as db:
    sql = """select j.job_id, j.job_title, j.job_description from job j
               order by j.job_id ASC"""
    jobs_query_result: Tuple[int, str, str] = db.query_all(sql)
for index, one_job in enumerate(jobs_query_result):
    job_id, job_title, description = one_job
    all_doc_list.append(description)
    all_id_list.append(job_id)

all_doc_list_lower = [item.lower() for item in all_doc_list]
vectorizer.fit(all_doc_list_lower)


def save_doc_matrix():
    bag_of_words = vectorizer.transform(all_doc_list_lower)
    scipy.sparse.save_npz(bag_of_words_doc_file, bag_of_words)
    print(bag_of_words)


def load_dense_bag_of_words_matrix(bag_of_words_matrix_file: str):
    return scipy.sparse.load_npz(bag_of_words_matrix_file).todense()


def cosine_similarity():
    upperlimit = 200

    # construct KDtree, time consuming
    dense_matrix = load_dense_bag_of_words_matrix(bag_of_words_doc_file)
    neigh = NearestNeighbors(n_neighbors=upperlimit, metric='cosine')
    neigh.fit(dense_matrix)



    query = ['data analyst']
    top_choices_job_id = top_choice_n(neigh, upperlimit, query)
    print(top_choices_job_id)


def top_choice_n(neigh: NearestNeighbors, n: int, query_list: List[str]) -> List[int]:
    query_bag_of_words_representation = vectorizer.transform(query_list).todense()
    distance, indices_list = neigh.kneighbors(query_bag_of_words_representation)

    indices_list = indices_list.reshape(n)

    top_choices = []
    for item in indices_list:
        top_choices.append(all_id_list[item])
    return top_choices


if __name__ == '__main__':
    # save_doc_matrix()
    cosine_similarity()
