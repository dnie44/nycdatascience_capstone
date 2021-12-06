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

def make_soup(url) :
	options = Options()
	options.headless = True

	DRIVER_PATH = '/Users/tonypennoyer/desktop/capstone/chromedriver'
	driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)


	try :

		driver.get(url);

		gotit = driver.find_element_by_id('download-and-save');

		gotit.click()

		time.sleep(1)

		driver.close()


	except :

		print('invalid')



zip_list = [12581,22400,91945]

make_soup('https://www.redfin.com/zipcode/12550')