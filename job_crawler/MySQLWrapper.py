# coding=utf8
from typing import Dict, List
import MySQLdb
from DBUtils.PooledDB import PooledDB
import logging

logging.basicConfig(level=logging.INFO)


class MySQLWrapper:
    __pool = None

    def __init__(self, db_name="411project"):
        self._connection = MySQLWrapper.get_conn(db_name)
        self.cursor = self._connection.cursor()

        # # 立即将本次数据库连接设成utf-8编码
        # self._connection.set_character_set('utf8')
        # self.cursor.execute('SET NAMES utf8;')
        # self.cursor.execute('SET CHARACTER SET utf8;')
        # self.cursor.execute('SET character_set_connection=utf8;')

    @staticmethod
    def get_conn(db_name="411project", user="309manager", password="cs4112019", host="localhost", port=3306):
        """
        静态方法，从连接池中取出连接
        return sqlite.connection
        """
        if MySQLWrapper.__pool is None:
            MySQLWrapper.__pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=5, host=host, port=port, user=user,
                                           password=password, database=db_name, charset='utf8')
        return MySQLWrapper.__pool.connection()

    def query_table_columns(self, table_name):
        """same as quert title"""
        sql = f"select * from {table_name} limit 0"
        return self.query_title(sql)

    def query_title(self, sql, params=None):
        """return table headers"""
        if "limit" not in sql:
            sql += " limit 0"
        if len(params) > 0:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        col_names = []
        # print(self.cursor.description)
        for info in self.cursor.description:
            col_names.append(info[0])
        return col_names

    def query_all(self, sql):
        """select all matched query result"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def query_one(self, sql):
        """select one matched query result"""
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def query_by(self, sql, params=None):
        """select all matched with condition query result"""
        if len(params) > 0:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self.cursor.fetchall()

    def insert_one_row_by_dict(self, table_name: str, data_dict: Dict):
        """insert a json format dictionary"""
        sql_pre = "insert into {table} (%s) values (%s)".format(table=table_name)
        # clean the dict
        fields = data_dict.keys()
        bindvars = ["%(" + x + ")s" for x in data_dict.keys()]
        bindvars = ",".join(bindvars)
        sql = sql_pre % (",".join(fields), bindvars)
        print(sql)
        print(data_dict)
        # try:
        self.insert_one(sql, data_dict)
        # except MySQLdb.IntegrityError as e:  # 如果有重复，就跳过它
        #     logging.log(e)
            # print("data duplicate:", data_dict)

    def insert_one(self, sql: str, params=None):
        if params is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)
        self.commit()

    def upper_all(self, table_name):
        """uppercase whole table"""
        columns = self.query_title(f"select * from {table_name}")
        for column in columns:
            print(column)
            sql = f"update {table_name} set {column} = upper({column})"
            # print(sql)
            self.cursor.execute(sql)
            self.commit()

    def lower_all(self, table_name):
        """lowercase whole table"""
        columns = self.query_title(f"select * from {table_name}")
        for column in columns:
            print(column)
            sql = f"update {table_name} set {column} = lower({column})"
            print(sql)
            self.cursor.execute(sql)
            self.commit()

    def insert_batch_from_dataframe(self, result_df, table_name):
        """batch insert from pandas dataframe"""
        values = []
        for index, row in result_df.iterrows():
            values.append(tuple(row))

        cols_str = ",".join((tuple(result_df.columns)))
        num_list_str = ""
        for i in range(1, len(result_df.columns) + 1):
            num_list_str += f":{i},"
        num_list_str = num_list_str[:-1]

        sql = f"INSERT INTO {table_name}({cols_str}) VALUES({num_list_str})"
        print(sql)
        self.insert_batch(sql, values)

    def insert_batch(self, sql, value_list):
        self.cursor.executemany(sql, value_list)
        self.commit()

    def delete_from(self, table_name, conditions):
        sql = f"delete from {table_name} where {conditions}"
        self.cursor.execute(sql)
        self.commit()
        print(f"executed sql: {sql}")

    def erase_table(self, table_name):
        """clear a whole table"""
        sql = "delete from " + table_name
        print(f"started to erase {table_name}")
        self.cursor.execute(sql)
        self.commit()
        print(f"data in {table_name} has been cleared")

    def backup(self, table):
        """backup a table"""
        sql = f"create table {table.upper() + '_BACK_UP'} as select * from {table}"
        """直接建表不用commit"""
        print(sql)
        try:
            self.cursor.execute(sql)
        except MySQLdb.OperationalError:
            self.cursor.execute(f"drop table {table.upper() + '_BACK_UP'}")
            self.cursor.execute(sql)

    def recover_from(self, table_recovered, backup):
        """recover a table"""
        self.copy_table(backup, table_recovered)

    def recover_from_backup(self, table):
        """recover a table from back_up table"""
        self.recover_from(table, f"{table.upper() + '_BACK_UP'}")

    def copy_table(self, table_origin, table_dest):
        """copy a table into a new table"""
        self.erase_table(table_dest)
        sql = f"insert into {table_dest} select * from {table_origin}"
        print(sql)
        self.cursor.execute(sql)
        self.commit()

    def commit(self):
        self._connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        # print(exc_type,exc_val,exc_tb)

    def release(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, '_conn'):
            self._connection.close()
        print("db resources has released.")

    # def __del__(self):
    #     self.release()


def test_query_title():
    db = MySQLWrapper()
    sql = "select id from kafkatest1 where id =: id"
    result = db.query_title(sql, {'id': 1000})
    for r in result:
        print(r)


if __name__ == '__main__':
    # test_query_title()
    db = MySQLWrapper()
    db2 = MySQLWrapper()
    r = db.query_all("select * from Company")
    print(r)
    # # db.backup(table)
    # db.copy_table(table2, table)
    # db.backup(table)
    # sql = "select * from ? where sender = ?"
    # temp = db.query_by(sql,['msgapp_msgboard', 'kafka'])
    # print(temp)
