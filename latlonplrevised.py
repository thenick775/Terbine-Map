#!/usr/bin/env python
# coding: utf-8
#This script is designed to format the location strings
#to a vector format suitable for plotly

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
from time import sleep
import os.path
import pandas as pd

base='https://www.terbine.io/'
print("hello from the lat lon miner")

class wait_for_text_to_match(object):
    def __init__(self, locator, pattern):
        self.locator = locator
        self.pattern = re.compile(pattern)

    def __call__(self, driver):
        try:
            element_text = EC._find_element(driver, self.locator).get_attribute('innerText')
            return self.pattern.search(element_text)
        except StaleElementReferenceException:
            return False

def setpagecrawlnum(driver):
	driver.find_element_by_xpath('//*[@id="select_9"]').send_keys('\n')
	WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="select_option_6"]'))) # find next arrow
	driver.find_element_by_xpath('//*[@id="select_option_6"]').send_keys("\n")

def parselatlon(stri):
	return re.sub(r'[ a-zA-Z]*[:] *[ a-zA-Z]*','',stri)[:-1]

def parsebboxpoly(stri):
	return "Points:"+re.sub(r'[ a-zA-Z]|[a-zA-Z]*[:] ','',stri)

def scrapeloc(driver,elements,file,prevdat,lastline):
	clicked=0
	first=False
	for element in elements:
		res=[]
		n=element.find_element_by_class_name('result-name')#.send_keys('\n')#click the name to get into tile
		na='"'+n.get_attribute('innerText')+'"'
		
		if prevdat["val"] and na[1:-1]!=lastline:
			print("last data present, skipping to last line")
			continue
		elif prevdat["val"] and na[1:-1]==lastline:
			prevdat["val"]=False
			first=True
			continue

		n.send_keys('\n')
		try:
			WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'//*/md-content/div[1]/div[2]/div[2]')))
			WebDriverWait(driver, 20).until(wait_for_text_to_match((By.XPATH,'//*/md-content/div[1]/div[2]/div[2]'),r"^.+$"))
		except TimeoutException:
			pass
		time='"'+driver.find_element_by_xpath('//*/md-content/div[1]/div[2]/div[2]').get_attribute('innerText')+'"'
		WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[5]/md-dialog/div/div/md-nav-bar/div/nav/ul/li[2]/button')))
		driver.find_element_by_xpath('/html/body/div[5]/md-dialog/div/div/md-nav-bar/div/nav/ul/li[2]/button').click()#click to get access to context
		inf=driver.find_element_by_xpath('//*/md-content/div[2]/div[2]/div[2]')#get location type
		if(inf.get_attribute('innerText')=='Fixed'):#if not fixed I cant track anything here with this info easily
			#print('getting latlon or bbox')
			res.append(time)
			res.append(na)
			s=driver.find_element_by_xpath('//*/md-content/div[2]/div[3]/div[2]').get_attribute('innerText')
			if 'Latitude: ' in s:
				res.append(parselatlon(driver.find_element_by_xpath('//*/md-content/div[2]/div[3]/div[2]').get_attribute('innerText')))#if fixed get location info
			elif "Bounded " in s or "Polygon" in s:
				res.append('"'+parsebboxpoly(driver.find_element_by_xpath('//*/md-content/div[2]/div[3]/div[2]').get_attribute('innerText'))+'"')
				res.append('nil')
				res.append('nil')
			clicked+=1
			print('clicked: '+str(clicked))

			if first:
				file.write("\n")
				first=False
			file.write(','.join(res)+'\n')
		driver.find_element_by_xpath('/html/body/div[5]/md-dialog/div/md-dialog-actions/button').click()
		sleep(1)


def getlatlon():
	options = Options()
	options.add_argument("no-sandbox")
	options.add_argument("headless")
	options.add_argument('--no-proxy-server')
	options.add_argument("start-maximized")
	options.add_argument("window-size=1900,1080"); 
	driver = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
	count=1
	origfname='./latlondat.txt'
	prevdat={"val":False}
	last_line=""
	driver.get(base)
	WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.CLASS_NAME,'resultset-inner')))
	setpagecrawlnum(driver)
	WebDriverWait(driver,60).until(EC.visibility_of_element_located((By.CLASS_NAME,'transcluded')))

	if os.path.exists(origfname):
		print("found existing data in file")
		prevdat={"val":True}
		last_line = pd.read_csv(origfname).iloc[[-1]]["name"].values[0]
		print(last_line)
	else:
		print("no existing data")

	with open(origfname,"a") as f:
		if prevdat["val"]==False:
			f.write('date,name,lat,lon,optrad\n')#lat may also contain list of points
		while True:
			elements = driver.find_elements_by_class_name('resultset-inner')
			print(len(elements))
			scrapeloc(driver,elements,f,prevdat,last_line)
			driver.find_element_by_xpath('//*[@id="content-container"]/div/div/div/div/form/div[3]/div[3]/div[2]/div[1]/div[2]/div[4]/ul/li[15]/a').send_keys('\n')#advance page
			try:
				WebDriverWait(driver,60).until(EC.visibility_of_element_located((By.CLASS_NAME,'transcluded')))
				print('new page '+str(count))
				count+=1
			except TimeoutException:
				break;

	driver.quit()

if __name__== "__main__":
    getlatlon()