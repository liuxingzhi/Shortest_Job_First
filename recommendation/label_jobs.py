import sys
# sys.path.append("..")
from utils.justeson_extractor import get_all_terms_in_doc, get_all_terms_in_doc_with_frequency
from job_crawler.MySQLWrapper import MySQLWrapper
import re
from typing import Tuple, List, Generator
from MySQLdb import OperationalError, IntegrityError

reg_exp = '((A|N)+|((A|N)*(NP)?)(A|N)*)N'
p = re.compile(reg_exp)


def init_job_bag_of_words_table():
    with MySQLWrapper() as db:
        sql = """create table if not exists job_bag_of_words_repr
            (
                job_id       BIGINT(11) NOT NULL,
                job_title    text,
                bag_of_words text,
                CONSTRAINT job_unique UNIQUE (job_id),
                FOREIGN KEY (job_id)
                    REFERENCES job (job_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            )"""
        db.execute(sql)
        db.commit()


def insert_one_bag_of_word_repr_of_job(job_id: int, job_title: str, terms_generator: Generator[str, None, None]):
    term_frequency_repr = [f"{t}\t{c}" for t, c in terms_generator]
    term_list_str = "\n".join(term_frequency_repr)
    with MySQLWrapper() as db:
        sql = f"""insert into job_bag_of_words_repr(job_id, job_title, bag_of_words) 
        values(%s, %s ,%s) """
        vals = (job_id, job_title, term_list_str)
        try:
            db.insert_one(sql, vals)
        except IntegrityError as e:
            sql = f"""update job_bag_of_words_repr as jbwr
                                set jbwr.bag_of_words = %s
                                where jbwr.job_id = %s"""
            val = (term_list_str, job_id)
            db.execute(sql, params=val)
            db.commit()


def label_jobs(min_freq=1):
    init_job_bag_of_words_table()
    with MySQLWrapper() as db:
        sql = "select j.job_id, j.job_title, j.job_description from job j"
        result: Tuple[int, str, str] = db.query_all(sql)

    for one_job in result:
        job_id, job_title, description = one_job
        terms = get_all_terms_in_doc_with_frequency(reg_exp, description, min_freq)
        insert_one_bag_of_word_repr_of_job(job_id, job_title, terms)


if __name__ == '__main__':
    label_jobs(min_freq=1)
