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



df = pd.read_csv('zip_df.csv')
df['ZipCode'] = df['ZipCode'].apply(str)
zip_list = df.ZipCode
count = 0

for zip_code in zip_list:
	if count < 70001 :
		print(zip_code)
		make_soup(zip_code)
		count = count + 1
	else : print('done')












