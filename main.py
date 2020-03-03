import logging
import logging.config
import sys

from api import API
from cli import Cli, Cmd
from scrapping import Scrapping
from db import DataBase

from constants import URL, RECIPE_DETAILS, ING_DETAILS
from config import LOG_CONF, DB_NAME, DB_HOST, DB_USER, DB_PASSWD, REC_FILENAME, ING_FILENAME


def main():
    """ The main function executes the program """
    logging.config.fileConfig(LOG_CONF)
    cli = Cli()
    cli.parse_arguments_advanced()
    try:
        ret = cli.args_handel()
        if ret[0] == Cmd.invalid_input:
            sys.exit("invalid input")
        logging.debug(f'Arguments received: {ret}')
    except Exception as ex:
        logging.error(f'Failed to handel args, error: {ex}')
        sys.exit("invalid input")

    sc = Scrapping()
    cat = ret[1]
    sub_cats = ret[2]

    exist_cat = sc.get_category_list(URL)
    logging.debug(f'List of categories: {exist_cat}')

    if ret[0] == Cmd.cat_list:
        print(exist_cat)
    elif ret[0] == Cmd.sub_cat_list:
        if cat not in exist_cat:
            logging.error(f'Invalid input: category {cat} not exists')
            sys.exit("invalid input")
        cat_link = sc.get_category_links(URL, cat)
        sub_category_list = sc.get_category_list(cat_link[cat])
        print(sub_category_list)
    elif ret[0] == Cmd.write_to_db:
        if cat not in exist_cat:
            logging.error(f'Invalid input: category {cat} not exists')
            sys.exit("invalid input")

        cat_link = sc.get_category_links(URL, cat)
        exist_subcat = sc.get_category_list(cat_link[cat])
        if set(sub_cats) - set(exist_subcat) != set():
            logging.error(f'Invalid input: at least on of subcategories {sub_cats} not exists')
            sys.exit("invalid input")

        cat_link = sc.get_category_links(URL, cat)
        sub_cat_links = sc.get_category_links(cat_link[cat], sub_cats)
        recipes = {}
        for sub_cat, link in sub_cat_links.items():
            recipes[sub_cat] = sc.get_recipe_links(link)

        logging.debug(f'Scrap for categories: {cat}, and sub-categories: {sub_cat}')
        data_sc = sc.scrap_data(cat, recipes)
        api = API()
        data_api = api.get_info_ingred()
        sc.write_data_to_csv(data_sc, REC_FILENAME, RECIPE_DETAILS)
        sc.write_data_to_csv(data_api, ING_FILENAME, ING_DETAILS)
        db = DataBase(DB_HOST, DB_USER, DB_PASSWD, DB_NAME)
        db.write_data_to_db(data_sc, data_api)


if __name__ == '__main__':
    main()
