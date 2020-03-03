"""
This module contains the main function, and parse_arguments_advanced.
It executes the program from the main function, according to the specified arguments given by the user.
the input arguments are parsed by the parse_arguments_advanced function
"""

import argparse
import logging
import enum


# Enumerations for Cli Class
class Cmd(enum.Enum):
    invalid_input = 0
    cat_list = 1
    sub_cat_list = 2
    write_to_db = 3


class Cli:
    def __init__(self):
        self.args = None
        self.logger = logging.getLogger(__name__)

    def parse_arguments_advanced(self):
        """ Processing and storing the arguments of the program
            returns an argparse. Namespace object, depicting and store the input arguments
            according to the defined flags
        """
        parser = argparse.ArgumentParser(
            description="Script Description"
        )

        parser.add_argument("-l", "--list", help="""
                            Returns the list of categories.
                            example: '$python main.py -l'
                            """, action="store_true")

        parser.add_argument("-c", "--category", help="""
                            Receives one argument (category) after the -l flag and returns the list of 
                            sub categories associated with the specified category. 
                            example: '$python main.py -lc Cookies' 
                            """,    # TODO add a condition that this flag can not be independent
                            action="store")

        parser.add_argument("-g", "--get", help="""
                            Scraping data of the requested category and subcategory and save it in a 
                            csv and sql data base. Receives two arguments: category and sub-category 
                            Note: don't forget to add "" around category/subcategory of >=2 words.
                        
                            example: '$python main.py -g Cookies "Butter Cookies" "Biscotti"' 
                            """, nargs='+')

        self.args = parser.parse_args()

    def args_handel(self):
        """ The function handles the arguments
            Returns:
            list: list of 3 parameters: [action, category, list of sub categories]
        """
        self.logger.debug(f'Starting to  handel arguments')

        if self.args.list:
            # in case l is given alone
            if self.args.category is None:
                return [Cmd.cat_list, None, None]
            elif self.args.category is not None:
                return [Cmd.sub_cat_list, self.args.category, None]
            else:
                self.logger.error(f'Invalid input')
                return [Cmd.invalid_input, None, None]

        # in case -g is given correctly(with category and sub-category)
        elif self.args.get is not None:
            if len(self.args.get) > 1:
                return [Cmd.write_to_db, self.args.get[0], self.args.get[1:]]
            else:
                self.logger.error(f'Invalid input, args: -g  requested '
                                  f'category {self.args.get[0]} requested subcategory {self.args.get[1:]}')
                return [Cmd.invalid_input, None, None]
        else:
            self.logger.error(f'Unknown error')
            return [Cmd.invalid_input, None, None]
