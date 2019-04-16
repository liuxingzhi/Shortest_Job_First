from job_crawler.MySQLWrapper import MySQLWrapper

def init_tag_table():
    with MySQLWrapper() as db:
        sql = """CREATE TABLE IF NOT EXISTS job_tags
                (
                  job_id VARCHAR(100) NOT NULL,
                  tag    varchar(100) NOT NULL,
                  FOREIGN KEY (job_id)
                    REFERENCES job (job_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                );"""
        db.execute(sql)

