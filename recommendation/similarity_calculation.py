import sys
import scipy.sparse
from joblib import Memory

sys.path.append("..")
from utils.justeson_extractor import get_all_terms_in_doc
from job_crawler.MySQLWrapper import MySQLWrapper
import re
from typing import Tuple, List, Generator, Union, Optional
from MySQLdb import OperationalError, IntegrityError
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
import os

cache_location = './cachedir'
if not os.path.exists(cache_location):
    os.makedirs(cache_location)
memory = Memory(cache_location, verbose=0)

reg_exp = '((A|N)+|((A|N)*(NP)?)(A|N)*)N'
p = re.compile(reg_exp)

bag_of_words_doc_file = "job_bag_of_words.npz"

stop_words = ["the", "this", "a", "at", "as", "all", "are", "above", "and", "only", "more", "between", "by", "to",
              "be", "is", "are", "been", "can", "can't", "did", "my"]
vectorizer = CountVectorizer(stop_words, max_df=0.95, min_df=0.05)

all_doc_list = []
all_id_list = []
all_doc_list_lower = []


def init_doc_matrix():
    with MySQLWrapper() as db:
        sql = """select j.job_id, j.job_title, j.job_description from job j
                   order by j.job_id ASC"""
        jobs_query_result: Tuple[int, str, str] = db.query_all(sql)

    for index, one_job in enumerate(jobs_query_result):
        job_id, job_title, description = one_job
        all_doc_list.append(description)
        all_id_list.append(job_id)

    global all_doc_list_lower
    all_doc_list_lower = [item.lower() for item in all_doc_list]
    vectorizer.fit(all_doc_list_lower)


get_doc_terms_KDtree = memory.cache(init_doc_matrix)
init_doc_matrix()


def save_doc_matrix():
    bag_of_words = vectorizer.transform(all_doc_list_lower)
    scipy.sparse.save_npz(bag_of_words_doc_file, bag_of_words)
    print(bag_of_words)


def load_dense_bag_of_words_matrix(bag_of_words_matrix_file: str):
    return scipy.sparse.load_npz(bag_of_words_matrix_file).todense()


def get_doc_terms_KDtree(n_neighbors=5):
    dense_matrix = load_dense_bag_of_words_matrix(bag_of_words_doc_file)
    neigh = NearestNeighbors(n_neighbors=5, metric='cosine')
    neigh.fit(dense_matrix)
    return neigh


get_doc_terms_KDtree = memory.cache(get_doc_terms_KDtree)


def top_n_neighbors(n: int, query_list: List[str]) -> List[int]:
    # construct KDtree, time consuming
    neigh = get_doc_terms_KDtree()
    combine2str = [",".join(query_list)]
    query_bag_of_words_representation = vectorizer.transform(combine2str).todense()
    distance, indices_list = neigh.kneighbors(query_bag_of_words_representation)

    indices_list = indices_list.reshape(n)

    top_choices = []
    for item in indices_list:
        top_choices.append(all_id_list[item])
    return top_choices


def manyjobs2job_n_closest_neighbors(job_list: Union[List[int], Tuple[int]], n: int):
    job_list = [str(x) for x in job_list]
    job_id_range_repr = "(" + ",".join(job_list) + ")"
    with MySQLWrapper() as db:
        sql = f"""select j.job_id, j.bag_of_words
                       from job_bag_of_words_repr j
                       where j.job_id in {job_id_range_repr}"""
        results: Tuple[Tuple[int, str]] = db.query_all(sql)

    total_query_list = []
    for result in results:
        _, bag_of_words = result
        query_list_fre = bag_of_words.split("\n")
        for one_row in query_list_fre:
            word, fre = one_row.split("\t")
            for i in range(int(fre)):
                total_query_list.append(word)
    closest_neighbors = top_n_neighbors(n, total_query_list)
    print(closest_neighbors)
    return closest_neighbors


def job2job_n_closest_neighbors(job_id: int, n: int):
    with MySQLWrapper() as db:
        sql = f"""select j.job_id, j.bag_of_words
                    from job_bag_of_words_repr j
                    where j.job_id = {job_id}"""
        result: Tuple[int, str] = db.query_one(sql)
    _, bag_of_words = result
    query_list_fre = bag_of_words.split("\n")
    query_list = []
    for one_row in query_list_fre:
        word, fre = one_row.split("\t")
        for i in range(int(fre)):
            query_list.append(word)
    closest_neighbors = top_n_neighbors(n, query_list)
    print(closest_neighbors)
    return closest_neighbors


def jobseeker2job_n_closest_neighbors(user_id: int, n: int) -> Optional[List[int]]:
    with MySQLWrapper() as db:
        sql = f"""select j.user_id, u.bag_of_words
                       from jobseeker j
                       inner join user_bag_of_words_repr u 
                       on u.user_id = j.user_id
                       where j.user_id = {user_id}"""
        result: Tuple[int, str] = db.query_one(sql)
    print(result)
    _, bag_of_words = result
    query_list_fre = bag_of_words.split("\n")
    query_list = []
    for one_row in query_list_fre:
        word, fre = one_row.split("\t")
        for i in range(int(fre)):
            query_list.append(word)
    closest_neighbors = top_n_neighbors(n, query_list)
    print(closest_neighbors)
    return closest_neighbors


if __name__ == '__main__':
    # save_doc_matrix()
    # job2job_n_closest_neighbors(972027802, 5)
    # manyjobs2job_n_closest_neighbors([972027802, 1342456246, 1011707680, 3108494370, 3157500847], 5)
    jobseeker2job_n_closest_neighbors(3,5)