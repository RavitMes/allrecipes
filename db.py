"""
This module handles the creation and management of the database:
     - creates new database if not exits
     - inserts data to database
     - delete database
 """

import logging
# import contextlib
import mysql.connector as mysql
from constants import INGREDIENTS


class DataBase:
    def __init__(self, host, username, pwd, db_name, port=3306):
        self.host = host
        self.user = username
        self.pwd = pwd
        self.db_name = db_name
        self.port = port
        self.logger = logging.getLogger(__name__)

    # @contextlib.contextmanager
    # TODO: replace connect_db function with db_connection
    # """
    #     connects to db, and disconnects automatically
    #  """
    # def db_connection(self):
    #     conn = mysql.connect(user=self.user, host=self.host, passwd=self.pwd, port=self.port, db=self.db_name)
    #     try:
    #         yield conn
    #     except Exception:
    #         conn.rollback()
    #         raise
    #     else:
    #         conn.commit()
    #     finally:
    #         conn.close()

    def connect_db(self):
        """ connects to db, returns connection and cursor
            Returns:
            db: connection to db
            cursor: database cursor
        """
        db = mysql.connect(host=self.host, user=self.user, passwd=self.pwd)
        cursor = db.cursor()
        return db, cursor

    def create_db(self):
        """ Creates database and tables if not exists """
        self.logger.debug("Create db and tables if not exists")
        db, cursor = self.connect_db()
        try:
            # Crete database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
        except mysql.Error as err:
            cursor.close()
            db.close()
            self.logger.error(f'Failed creating database: {err}"')
            raise Exception('DB error')

        try:
            # Select database
            cursor.execute(f"USE {self.db_name}")
        except mysql.Error as err:
            cursor.close()
            db.close()
            self.logger.error(f'Failed to select database: {err}"')
            raise Exception('DB error')

        try:
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS recipes (
                              id int PRIMARY KEY AUTO_INCREMENT,
                              name varchar(255),
                              category varchar(255),
                              sub_category varchar(255),
                              prep_time varchar(255),
                              calories int,
                              author varchar(255),
                              review int,
                              rating float,
                              url varchar(255),
                              image varchar(255),
                              summary BLOB,
                              directions BLOB
                            )""")
        except mysql.Error as err:
            cursor.close()
            db.close()
            self.logger.error(f'Failed creating table: recipes')
            raise Exception('DB error')

        try:
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS ingredients (
                                id int PRIMARY KEY AUTO_INCREMENT,
                                name varchar(255)
                            )""")
        except mysql.Error as err:
            cursor.close()
            db.close()
            self.logger.error(f'Failed creating table: ingredients')
            raise Exception('DB error')

        try:
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS nutrients (
                                id int PRIMARY KEY AUTO_INCREMENT,
                                ingd_id int,
                                enerc_kcal float,
                                procnt float,
                                fat float,
                                carb float,
                                FOREIGN KEY (ingd_id) REFERENCES ingredients (id)
                            )""")
        except mysql.Error as err:
            cursor.close()
            db.close()
            self.logger.error(f'Failed creating table: nutrients')
            raise Exception('DB error')

        try:
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS recipe_ingredients (
                                id int PRIMARY KEY AUTO_INCREMENT,
                                recipe_id int,
                                ingd_id int,
                                quantity varchar(255),
                                measurement_tool varchar(255),
                                FOREIGN KEY (recipe_id) REFERENCES recipes (id),
                                FOREIGN KEY (ingd_id) REFERENCES ingredients (id)
                            )""")
        except mysql.Error as err:
            cursor.close()
            db.close()
            self.logger.error(f'Failed creating table: recipe_ingredients')
            raise Exception('DB error')

        try:
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS api_data (
                                id int PRIMARY KEY AUTO_INCREMENT,
                                ingd_id int,
                                recipe_name varchar(255),
                                url varchar(255),
                                image varchar(255),
                                FOREIGN KEY (ingd_id) REFERENCES ingredients (id)
                            )""")

        except mysql.Error as err:
            self.logger.error(f'Failed creating table: api_data"')
            raise Exception('DB error')
        finally:
            cursor.close()
            db.close()

    def delete_db(self):
        """ Deletes a database """
        db, cursor = self.connect_db()
        cursor.execute(f"DROP DATABASE {self.db_name}")
        cursor.close()
        db.close()

    def select_ingredients(self):
        """ selects ingredients from db and return them as dict
            return:
            dict: key is a ingredients, value it's id
        """
        db, cursor = self.connect_db()
        cursor.execute(f"USE {self.db_name}")
        cursor.execute("SELECT * FROM ingredients")
        result = cursor.fetchall()
        cursor.close()
        db.close()
        dct = {k: v for v, k in result}
        return dct

    def insert_constant_data_to_db(self):
        """ Insert constant data from file "constants.py" to 'in'gredients' table """
        db, cursor = self.connect_db()
        self.logger.debug("Starting to insert data into db")
        try:
            for record in INGREDIENTS:
                cursor.execute(f"USE {self.db_name}")
                insert_query = """INSERT INTO ingredients (name) VALUES (%s)"""
                cursor.execute(insert_query, (record,))

            db.commit()
        except mysql.Error as err:
            self.logger.error(f'Failed creating table: {err}"')
            raise Exception('DB error')
        finally:
            cursor.close()
            db.close()

    def insert_scrapped_data_to_db(self, data):
        """ Insert data to database tables
            Parameters:
            data (list of dict): data to upload to database
        """
        db, cursor = self.connect_db()
        self.logger.debug("Starting to insert data into db")
        try:
            ing = self.select_ingredients()
            cursor.execute(f"USE {self.db_name}")
            for i, record in enumerate(data):
                insert_query_recipes = """INSERT INTO recipes (name, category, sub_category, prep_time, calories, 
                                author, review, rating, url, image, summary, directions) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                row_recipes = (record['name'], record['category'], record['sub_category'], record['prep_time'],
                               record['calories'], record['author'], record['review'], record['rating'],
                               record['url'], record['image'], record['summary'], record['directions'])
                cursor.execute(insert_query_recipes, row_recipes)

                insert_rec_ingd = """INSERT INTO recipe_ingredients (recipe_id, ingd_id, quantity, measurement_tool) 
                                    VALUES (%s, %s, %s, %s)"""
                for item in record['ingredients']:
                    quantity, measur, ingd = item
                    ingd_id = ing[ingd]
                    row_rec_ingd = (i + 1, ingd_id, quantity, measur)
                    cursor.execute(insert_rec_ingd, row_rec_ingd)

                if i % 10000 == 0:
                    db.commit()
            db.commit()
        except mysql.Error as err:
            self.logger.error(f'Failed creating table: {err}"')
            raise Exception('DB error')
        finally:
            cursor.close()
            db.close()

    def insert_api_data_to_db(self, data):
        """ Insert data to database tables
            Parameters:
            data (list of dict): data to upload to database
        """
        db, cursor = self.connect_db()
        self.logger.debug("Starting to insert data into db")
        try:
            ing = self.select_ingredients()
            cursor.execute(f"USE {self.db_name}")
            for i, record in enumerate(data):
                ingd_id = ing[record['label']]
                insert_query_nutrients = """INSERT INTO nutrients (ingd_id, enerc_kcal, procnt, fat, carb) 
                                            VALUES (%s, %s, %s, %s, %s)"""
                row_nutr = (ingd_id, record['enerc_kcal'], record['procnt'], record['fat'], record['carb'])
                cursor.execute(insert_query_nutrients, row_nutr)
                insert_query_api_data = """INSERT INTO api_data (ingd_id, recipe_name, url, image) 
                                            VALUES (%s, %s, %s, %s)"""
                for subrec in record['related_recipes']:
                    row_api_data = (ingd_id, subrec['title'], subrec['url'], subrec['img'])
                    cursor.execute(insert_query_api_data, row_api_data)

                if i % 10000 == 0:
                    db.commit()
            db.commit()
        except mysql.Error as err:
            self.logger.error(f'Failed creating table: {err}"')
            raise Exception('DB error')
        finally:
            cursor.close()
            db.close()

    def write_data_to_db(self, data_sc, data_api):
        """ Creates db and tales if not exists, and inserts data into it
            Parameters:
            data_sc (list of dict): data from scrapping to upload to database
            data_api (list of dict): data from api to upload to databases
        """
        self.create_db()
        self.insert_constant_data_to_db()
        self.insert_scrapped_data_to_db(data_sc)
        self.insert_api_data_to_db(data_api)
