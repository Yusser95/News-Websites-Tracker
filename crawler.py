from bs4 import BeautifulSoup
import requests


url = "http://xb.81.cn"
response = requests.get(url)

html = response.content
soup = BeautifulSoup(html,'lxml')

urls = soup.findAll("a")

path_info = requests.META.get('PATH_INFO')
print("path_info : " , path_info)

if urls:
	for url in urls:
		try:
			print(url['href'])
		except Exception as e:
			pass


# print(soup.find("p").getText(strip=True))