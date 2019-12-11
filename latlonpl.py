from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import re
import pandas as pd

base='https://www.terbine.io/'
print("hello from the lat lon miner")
countlim=275

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
	s1 = Select(driver.find_element_by_xpath('//*[@id="content-container"]/div/div/div/div[1]/form/div[3]/div[2]/div[2]/div/div[2]/div/section/div[3]/li/select'))
	s1.select_by_visible_text('100')

def parselatlon(stri):
	return re.sub(r'[ a-zA-Z]*[:] *[ a-zA-Z]*','',stri)[:-1]

def parsebboxpoly(stri):
	return "Points:"+re.sub(r'[ a-zA-Z]|[a-zA-Z]*[:] ','',stri)


def scrapeloc(driver,elements,file):
	for element in elements:
		res=[]
		n=element.find_element_by_class_name('result-name')#.send_keys('\n')#click the name to get into tile
		na='"'+n.get_attribute('innerText')+'"'
		n.send_keys('\n')
		WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'//*/md-content/div[1]/div[2]/div[2]')))
		WebDriverWait(driver, 10).until(wait_for_text_to_match((By.XPATH,'//*/md-content/div[1]/div[2]/div[2]'),r"^.+$"))
		time='"'+driver.find_element_by_xpath('//*/md-content/div[1]/div[2]/div[2]').get_attribute('innerText')+'"'
		#res.append('"'+driver.find_element_by_xpath('//*/md-content/div[1]/div[2]/div[2]').get_attribute('innerText')+'"')
		#res.append('"'+na+'"')
		WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[3]/md-dialog/div/div/md-nav-bar/div/nav/ul/li[2]/button/span')))
		driver.find_element_by_xpath('/html/body/div[3]/md-dialog/div/div/md-nav-bar/div/nav/ul/li[2]/button/span').click()#click to get access to context
		inf=driver.find_element_by_xpath('//*/md-content/div[2]/div[2]/div[2]')#get location typ
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
			print('clicked')
			file.write(','.join(res)+'\n')
		driver.find_element_by_xpath('/html/body/div[3]/md-dialog/div/md-dialog-actions/button').click()


def getlatlon():
	options = Options()
	options.add_argument("no-sandbox")
	options.add_argument("headless")
	options.add_argument('--no-proxy-server')
	options.add_argument("start-maximized")
	options.add_argument("window-size=1900,1080"); 
	driver = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
	count=0
	driver.get(base)
	WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.CLASS_NAME,'resultset-inner')))
	setpagecrawlnum(driver)
	WebDriverWait(driver,60).until(EC.visibility_of_element_located((By.CLASS_NAME,'transcluded')))

	with open('latlondat.txt',"a") as f:
		f.write('date,name,lat,lon,optrad\n')#lat may also contain list of points
		while True:
			elements = driver.find_elements_by_class_name('resultset-inner')
			print(len(elements))
			scrapeloc(driver,elements,f)
			driver.find_element_by_xpath('//*[@id="content-container"]/div/div/div/div[1]/form/div[3]/div[2]/div[2]/div/div[2]/div/section/div[3]/ul/li[15]/a').send_keys('\n')#advance page
			try:
				if count==countlim:
					print("early break")
					return driver#early break for testing sample for R
				WebDriverWait(driver,60).until(EC.visibility_of_element_located((By.CLASS_NAME,'transcluded')))
				print('new page')
				count+=1
			except TimeoutException:
				break;

	return driver

driver=getlatlon()
driver.quit()
