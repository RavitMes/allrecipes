import requests
import logging
from constants import INGREDIENTS, API_URL_EXTRA, API_URL_NUTRIENTS


class API:
    def __init__(self):
        self.args = None
        self.logger = logging.getLogger(__name__)

    def extract_extra(self, ing):
        """
        :param ing: name of ingredient(ing) as specified by the user
        :return list of recipes associated with this ingredient, for each recipe the following data
        is provided: title, url, img
        """
        lst = []
        try:
            querystring = {"i": ing}
            headers = {
                'x-rapidapi-host': "recipe-puppy.p.rapidapi.com",
                'x-rapidapi-key': "56ae2ccbf4mshf55a5b55145a40ep1472b9jsn6a8637a31483"
            }
            response = requests.request("GET", API_URL_EXTRA, headers=headers, params=querystring)
            data = response.json()
            for recipe in data['results']:
                lst.append({'title': recipe['title'], 'url': recipe['href'], 'img': recipe['thumbnail']})
            return lst
        except:
            self.logger.warning(f"Failed to extract extra details for the ingredient {ing}")
            return

    def extract_nutrients(self, ing):
        """
        :param ing: name of ingredient(ing) as specified by the user
        :return tuple of the following dietary values of associated with the specified ingredient:
        label(ingredient name), enerc_kcal(ingredient calories), fat, procnt (proteins), carb (carbohydrate)
        """
        try:
            querystring = {"ingr": ing}
            headers = {
                'x-rapidapi-host': "edamam-food-and-grocery-database.p.rapidapi.com",
                'x-rapidapi-key': "56ae2ccbf4mshf55a5b55145a40ep1472b9jsn6a8637a31483"
                }
            response = requests.request("GET", API_URL_NUTRIENTS, headers=headers, params=querystring)
            data = response.json()
            label = data['hints'][0]['food']['label'].strip()

            if label.lower().strip() == ing.lower().strip():
                enerc_kcal = data['hints'][0]['food']['nutrients']['ENERC_KCAL']
                fat = data['hints'][0]['food']['nutrients']['FAT']
                procnt = data['hints'][0]['food']['nutrients']['PROCNT']
                carb = data['hints'][0]['food']['nutrients']['CHOCDF']
                return label, enerc_kcal, fat, procnt, carb
        except:
            self.logger.warning(f"Failed to extract nutrients details for {ing}")
            return

    def get_info_ingred(self):
        """
        unify all data extracted from the APIs regarding the ingredients into one list of dictionaries
        :return: list of dictionaries where each dictionary indicate a row, containing the following
        fields: label(ingredient name), enerc_kcal(ingredient calories), fat, procnt (proteins),
        carb (carbohydrate), related_recipes(dictionary with the following data regarding each ingredient:
        title, url, img)
        """
        self.logger.info(f"Starting api scrapping")
        ing_data = []
        for ing in INGREDIENTS:
            ingred_data = {}
            if self.extract_nutrients(ing) is None:
                label, enerc_kcal, fat, procnt, carb = None, None, None, None, None
            else:
                label, enerc_kcal, fat, procnt, carb = self.extract_nutrients(ing)
            ingred_data['label'] = ing.strip()
            ingred_data['enerc_kcal'] = enerc_kcal
            ingred_data['fat'] = fat
            ingred_data['procnt'] = procnt
            ingred_data['carb'] = carb

            if self.extract_extra(ing) is None:
                extra = []
            else:
                extra = self.extract_extra(ing)
            ingred_data['related_recipes'] = extra
            ing_data.append(ingred_data)

        return ing_data
