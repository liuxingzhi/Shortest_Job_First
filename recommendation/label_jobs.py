from utils.justeson_extractor import get_all_terms_in_doc
from job_crawler.MySQLWrapper import MySQLWrapper
import re
from typing import Tuple, List, Generator
from MySQLdb import OperationalError, IntegrityError

# file_name = sys.argv[1]
# min_freq = int(sys.argv[2])
# out = sys.argv[3]
#
# with open(file_name, 'rb') as file:
#     doc = file.read()
#     doc = str(doc, "utf_8").encode('ascii', 'ignore').decode("ascii")
#     terms = get_all_terms_in_doc(reg_exp, doc, min_freq)
#     out_file = open(out, 'w')
#     out_file.write("\n".join(list(terms)))
#     out_file.close()
#     file.close()

reg_exp = '((A|N)+|((A|N)*(NP)?)(A|N)*)N'
p = re.compile(reg_exp)


def init_job_bag_of_words_table():
    with MySQLWrapper() as db:
        sql = """create table if not exists job_bag_of_words_repr
            (
                job_id       BIGINT(11) NOT NULL,
                job_title    text,
                bag_of_words text,
                FOREIGN KEY (job_id)
                    REFERENCES job (job_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            )"""
        db.execute(sql)
        db.commit()


def insert_one_bag_of_word_repr(job_id: int, job_title: str, terms_generator: Generator[str, None, None]):
    term_list_str = "\n".join(terms_generator)
    with MySQLWrapper() as db:
        sql = f"""insert into job_bag_of_words_repr(job_id, job_title, bag_of_words) 
        values(%s, %s ,%s) """
        vals = (job_id, job_title, term_list_str)
        try:
            db.insert_one(sql, vals)
        except IntegrityError as e:
            pass


if __name__ == '__main__':
    min_freq = 1
    result: Tuple[int, str, str] = None
    with MySQLWrapper() as db:
        sql = "select j.job_id, j.job_title, j.job_description from job j"
        result = db.query_all(sql)

    for one_job in result:
        job_id, job_title, description = one_job
        terms = get_all_terms_in_doc(reg_exp, description, min_freq)
        insert_one_bag_of_word_repr(job_id, job_title, terms)
