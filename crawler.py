import time
import requests
 
import re
from sys import exit
from bs4 import BeautifulSoup
import os
import unicodedata
from urllib.parse import urlparse


class Crawler():
    
    def __init__ (self):
        pass
        

    def strip_punctuation(self,text):
        if text is None:
            return None
        punctutation_cats = set(['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'])
        return  ''.join(x for x in text if unicodedata.category(x)
                       not in punctutation_cats)

    def scrape_data(self ,url  , path ,depth=4,flag=0 ,urls=[]):
        path = "./data/"+str(path)
        if not os.path.exists(path):
            os.makedirs(path)
        
        base_url = urlparse(url).scheme+"://"+urlparse(url).netloc+"/"
        
        for t in urls:
            if t['url'] == url:
                if t['depth'] <= depth:
                    return True
        
        urls.append({'url':url,'depth':depth})
        
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            response = None
            for i in range (3):
                try:
                    response = requests.get(url,headers=headers)
                    break
                except ConnectionError as e:
                    print(e)
                    if i == 2:
                        return e
            html = response.content
            

            if response.status_code == 200:
                file_name = urlparse(url).netloc+"/"+urlparse(url).path.replace("../","").replace("/","")
                file_name = file_name.replace("/","")

                if path[-1] != "/":
                    path+="/"

                if url[-5] != ".html":
                    file_name += ".html"

                

                with open(path+file_name , 'wb') as f:
                    f.write(html)
                
                

                print("flag : ",flag)
                print("url : ",url)
                print("file name : ",path+file_name)
                print('-'*30)

                if flag < depth:
                    soup = BeautifulSoup(html,'lxml')
                    all_as = soup.findAll("a")
                    if all_as:
                        for a in all_as:
                            try:
                                href = a['href']
        #                         print(href)
                                if href:
                                    if href.find("://") == -1:
                                        if href[0] != "#":
            #                                 print(base_url+href)
                                            time.sleep(1)
                                            self.scrape_data(base_url+href , path ,depth ,flag+1,urls)
                                    elif urlparse(href).netloc == urlparse(url).netloc:
        #                                 print(href)
                                        time.sleep(1)
                                        self.scrape_data(href , path ,depth ,flag+1,urls)
                            except KeyError as e:
                                print(e)
                                pass
                    else:
                        print("no links")
        #                 print(all_as)
            else:
                print("status_code : " , response.status_code)
        except Exception as e:
            print(e)