from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import re 
import csv
import requests
import pandas as pd
import numpy as np
import pickle
import os, glob
from time import sleep
from random import randint
from itertools import chain
from csv import writer
from bs4 import BeautifulSoup

def make_soup(zips) :
	options = Options()
	options.headless = True

	DRIVER_PATH = '/Users/tonypennoyer/desktop/capstone/chromedriver'
	driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
	base = 'https://www.redfin.com/zipcode/'

	url = base + zips

	try :

		driver.get(url);

		gotit = driver.find_element_by_id('download-and-save');

		gotit.click()

		sleep(1)

		driver.close()


	except :

		print('invalid')



df = pd.read_csv('zip_list_2.csv')
df['ZipCode'] = df['ZipCode'].apply(str)
zip_list = df.ZipCode
count = 0

# for zip_code in zip_list:
# 	if count < 7001 :
# 		print(zip_code)
# 		make_soup(zip_code)
# 		count = count + 1
# 	else : print('done')

os.chdir("/Users/tonypennoyer/desktop/capstone/final_scrape")
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
#combine all files in the list
combined_2 = pd.concat([pd.read_csv(f) for f in all_filenames ])
#export to csv
combined_2.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')










