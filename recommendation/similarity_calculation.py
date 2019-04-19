import sys
# sys.path.append("..")
import scipy.sparse
from joblib import Memory
from django.db import connection

from utils.justeson_extractor import get_all_terms_in_doc
from job_crawler.MySQLWrapper import MySQLWrapper
import re
from typing import Tuple, List, Generator, Union
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
    distance, indices_list = neigh.kneighbors(query_bag_of_words_representation, n_neighbors=n)
    print(distance)
    indices_list = indices_list.reshape(n)

    top_choices = []
    for item in indices_list:
        top_choices.append(all_id_list[item])
    return top_choices


def manyjobs2job_n_closest_neighbors(job_list: Union[List[int], Tuple[int]], n: int) -> List[int]:
    if len(job_list) == 0:
        return []
    job_list = [str(x) for x in job_list]
    job_id_range_repr = "(" + ",".join(job_list) + ")"
    with MySQLWrapper() as db:
        sql = f"""select j.job_id, j.bag_of_words
                       from job_bag_of_words_repr j
                       where j.job_id in {job_id_range_repr}"""
        print(sql)
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


def job2job_n_closest_neighbors(job_id: int, n: int) -> List[int]:
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


def jobseeker2job_n_closest_neighbors(user_id: int, n: int) -> List[int]:
    with MySQLWrapper() as db:
        sql = f"""select j.user_id, u.bag_of_words
                       from jobseeker j
                       inner join user_bag_of_words_repr u 
                       on u.user_id = j.user_id
                       WHERE j.user_id = '{user_id}'"""
        result: Tuple[int, str] = db.query_one(sql)
    if result is None:
        return []
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


# store recommend job based on user interests
def store_interest_job():
    with MySQLWrapper() as cursor:
        query = "DELETE FROM interest_job"
        cursor.execute(query)
        cursor.commit()
        query1 = f"""SELECT user_id FROM jobseeker WHERE personal_summary IS NOT NULL"""
        cursor.execute(query1)
        result1 = cursor.fetchall()
        for row in result1:
            uid = row[0]
            job_id_list = jobseeker2job_n_closest_neighbors(uid, 9)
            for job_id in job_id_list:
                query2 = f"""INSERT INTO interest_job (user_id, job_id) VALUES ('{uid}', '{job_id}')"""
                cursor.execute(query2)
                cursor.commit()


# store recommend job based on user search history and browse time
def store_behavior_job():
    with MySQLWrapper() as cursor:
        query = "DELETE FROM behavior_job"
        cursor.execute(query)
        cursor.commit()
        query1 = f"""SELECT user_id FROM jobseeker WHERE personal_summary IS NOT NULL"""
        cursor.execute(query1)
        result1 = cursor.fetchall()
        for row in result1:
            uid = row[0]
            behavior_job_list = get_list_by_history(uid)
            job_id_list = top_n_neighbors(6, behavior_job_list)
            similar_list = manyjobs2job_n_closest_neighbors(get_by_browse_time(20000, uid), 3)
            job_id_list.extend(similar_list)
            for job_id in job_id_list:
                query2 = f"""INSERT INTO behavior_job (user_id, job_id) VALUES ({uid}, {job_id})"""
                cursor.execute(query2)
                cursor.commit()


# get a list of job (ids) where user stays for a long time
def get_by_browse_time(threshold: int, uid: str) -> List[int]:
    with MySQLWrapper() as cursor:
        query1 = f"""SELECT job_id FROM 
        (((SELECT job_id, sum(time_elapsed) as total_time FROM browse_time WHERE user_id = '{uid}' 
        GROUP BY job_id HAVING total_time >= {threshold}) as atable natural join job) natural join company)"""
        cursor.execute(query1)
        result = cursor.fetchall()
        to_return = []
        for row in result:
            to_return.append(row[0])
        return to_return


# get a list from search history, pass to similarity function
def get_list_by_history(uid: str) -> List[str]:
    list1 = shc_helper("job_title", uid)
    list2 = shc_helper("company_name", uid)
    list3 = shc_helper("industry", uid)
    list4 = shc_helper("location", uid)
    list1.extend(list2)
    list1.extend(list3)
    list1.extend(list4)
    return list1


# a helper function
def shc_helper(col: str, uid: str) -> List[str]:
    with MySQLWrapper() as cursor:
        to_return = []
        query1 = f"""SELECT {col}, COUNT({col}) as count FROM search_history WHERE user_id = '{uid}' AND {col} <> '' GROUP BY {col} ORDER BY count DESC;"""
        cursor.execute(query1)
        result = cursor.fetchall()
        for row in result:
            for i in range(0, row[1]):
                to_return.append(row[0])
        return to_return


if __name__ == '__main__':
    # init_doc_matrix()
    # save_doc_matrix()
    # save_doc_matrix()
    # job2job_n_closest_neighbors(972027802, 5)
    # manyjobs2job_n_closest_neighbors([972027802, 1342456246, 1011707680, 3108494370, 3157500847], 5)
    store_behavior_job()
    store_interest_job()
