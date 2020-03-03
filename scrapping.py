"""
This module stands for scraping data from the www.allrecipes.com website:
The actions of the module:
    - returns lists/links of categories/subcategories
    - save the scraped data to csv/db
"""

from bs4 import BeautifulSoup
import requests
import logging
from recipe_details import RecipeDetails


class Scrapping:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_category_links(self, url, category):
        """ returns a link to a category/sub category
            Parameters:
            url (string): link for scraping
            category (list of strings) : requested categories
            Returns:
            dict : links to recipes, where key is category
        """
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        base = soup.find('div', id="insideScroll")
        links = {}
        for link in BeautifulSoup(str(base), 'lxml').findAll('a'):
            try:
                if link.span.text in category:
                    links[link.span.text] = link['href']
            except ValueError:
                self.logger.error(f"Unrecognized category")
        return links

    def get_category_list(self, url):
        """ returns a list of all the valid options in category/subcategory
            Parameters:
            url (string): link for scraping
            Returns:
            list of strings : categories names
        """
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        base = soup.find('div', id="insideScroll")
        category_list = []
        for link in BeautifulSoup(str(base), 'lxml').findAll('a'):
            try:
                category_list.append(link.span.text)
            except ValueError:
                self.logger.error(f"Unrecognized category")
        return category_list

    def get_recipe_links(self, url):
        """ returns links to all recipes on webpage
            Parameters:
            url (string): link for scraping
            Returns:
            list: list of links to recipes
        """
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        # find all recipes and extract their links
        links = soup.select('article.fixed-recipe-card div.grid-card-image-container a')
        links = [link['href'] for link in links if 'video' not in link['href']]
        if links == list():
            self.logger.warning(f"Failed to get recipe's links")
        return links

    def scrap_data(self, category, subcategories_links):
        """ scraps recipe details for category and subcategories
            Parameters:
            category (string): category for scraping
            subcategories_links (dict): links for scraping, where subcategories is a key
            Returns:
            list of dict: where each dictionary contains data of one link
        """
        rep_data = []
        rd = RecipeDetails()
        for sub_cat, links in subcategories_links.items():
            self.logger.info(f'Extracting data from category {category} , subcategory {sub_cat}')
            data = rd.get_recipes_details(category, sub_cat, links)
            rep_data.extend(data)
        return rep_data

    def write_data_to_csv(self, data, filename, headers):
        """ get recipe details and write it to csv
            Parameters:
            data (list of dict): data to write to csv file
            Returns:
            list of dict: where each dictionary contains data of one link
        """
        self.logger.info(f'Appending data to csv file')
        rd = RecipeDetails()
        rd.write_data_to_csv(data, filename, headers)
