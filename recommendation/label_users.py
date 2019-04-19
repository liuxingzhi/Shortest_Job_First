import sys
sys.path.append("..")
from utils.justeson_extractor import get_all_terms_in_doc, get_all_terms_in_doc_with_frequency
from job_crawler.MySQLWrapper import MySQLWrapper
import re
from typing import Tuple, List, Generator
from MySQLdb import OperationalError, IntegrityError
import MySQLdb
reg_exp = '((A|N)+|((A|N)*(NP)?)(A|N)*)N'
p = re.compile(reg_exp)


def init_user_bag_of_words_table():
    with MySQLWrapper() as db:
        sql = """create table if not exists user_bag_of_words_repr
            (
                user_id      int NOT NULL,
                bag_of_words text,
                CONSTRAINT user_unique UNIQUE (user_id),
                FOREIGN KEY (user_id)
                    REFERENCES jobseeker (user_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            )"""
        db.execute(sql)
        db.commit()


def insert_one_bag_of_word_repr_of_user(user_id: int, terms_generator: Generator[str, None, None]):
    term_frequency_repr = [f"{t}\t{c}" for t, c in terms_generator]
    term_list_str = "\n".join(term_frequency_repr)
    print(term_list_str)
    with MySQLWrapper() as db:
        sql = f"""insert into user_bag_of_words_repr(user_id, bag_of_words)
        values(%s, %s) """
        vals = (user_id, term_list_str)
        try:
            db.insert_one(sql, vals)
        except IntegrityError as e:
            sql = f"""update user_bag_of_words_repr as ubwr
                    set ubwr.bag_of_words = %s
                    where ubwr.user_id = %s"""
            val = (term_list_str, user_id)
            db.execute(sql, params=val)
            db.commit()


def label_jobseekers(min_freq=1):
    init_user_bag_of_words_table()
    with MySQLWrapper() as db:
        sql = """select j.user_id, j.personal_summary
                    from jobseeker as j
                             inner join user u
                                        on j.user_id = u.user_id
                    where j.personal_summary is not null
                      and j.personal_summary <> 'none'"""
        result: Tuple[int, str, str] = db.query_all(sql)

    for index, one_row in enumerate(result):
        user_id, personal_summary = one_row
        terms = get_all_terms_in_doc_with_frequency(reg_exp, personal_summary, min_freq)
        insert_one_bag_of_word_repr_of_user(user_id, terms)


if __name__ == '__main__':
    label_jobseekers()
