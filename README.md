## Web scraping 
This program receives a category and subcategory from the user, and scrapes relevant information 
from the website: www.allrecipes.com regarding all possible recipes associated with the requested arguments.
The program returns a detailed database and csv file containing the data in a well-ordered manner.  

## Features
TO DO

## Requirements
All requirements are specified in the file "requirements.txt"


## Usage
1. In order to run the program, it is necessary to add the local mySQL password in the
config.py file.
2. Changing the FILENAME (csv output file) and the DB_NAME  
(database output name) are optional by changing the values of these constants in the 
config file.

## To Run the program
1. To get list of categories:
    $python main.py -l
2. To get list of sub categories for specific category:
    $python main.py -lc category_name
3. Save all recipes of sub-categories from specific category:
    $python main.py -g category_name sub_category_name1 "sub category name2" sub_category_name3

## History
checkpoint1: TODO

checkpoint2: TODO

## Authors
Olga K, hazin.olga@gmail.com

Ravit M, ravit2244@gmail.com 
