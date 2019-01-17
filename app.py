
# coding: utf-8

# In[1]:
import os
import json
from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import desc
from operator import itemgetter
from flask import make_response
import time
from datetime import datetime, timedelta
import re


app = Flask(__name__)

cwd = os.getcwd()
print(cwd)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+cwd+'/resources/data.db'
app.config['SCHEDULER_API_ENABLED'] = True
db = SQLAlchemy(app)


scheduler = BackgroundScheduler()

# scheduler = APScheduler()
# scheduler.init_app(app)
scheduler.start()


from models import *
from crawler import Crawler
 
 
@app.route("/" , methods =["POST" , "GET"])
def main():

	data = {}
	if request.method == "POST":

		resp = {"success":False}
		selected_domains = request.form.getlist('domains[]')
		selected_keywords = request.form.getlist('keywords[]')

		print("\n selected_domains : ",selected_domains,"\n selected_keywords : ",selected_keywords)
		try:
			data = get_data(selected_domains,selected_keywords)
			resp["data"] = data
			resp["success"] = True
		except Exception as e:
			print(e)



		resp = json.dumps(resp, ensure_ascii=False).encode('utf8')
		resp = make_response(resp)
		resp.headers["Content-Type"]='application/json; charset=utf-8'

		return resp
	else: # get request
		domains = get_domains()
		keywords = getkeywords()
		data = get_data()
		colors = ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"]
		labels = [d.url for d in domains]
		domains_keywords_count = [len(Pargraph.query.filter_by(domain_id=d.id).all()) for d in domains]
		return render_template('index.html',keywords = keywords ,domains = domains, data=data ,labels=labels,colors=colors, domains_keywords_count=domains_keywords_count)
 



def get_domains():
	domains = Domain.query.all()
	return domains

def getkeywords():
	keywords = Keyword.query.all()
	return keywords

def get_data(selected_domains=None , selected_keywords=None):
	# ss= Sentiment.query.filter_by(keyword_id=selected_keyword[2:]).order_by(Sentiment.date).all()
	# ss= Sentiment.query.filter(Sentiment.tweet_id.in_(selected_tweets)).order_by(Sentiment.date).all()
	pargraphs = []

	print(selected_domains)
	print(selected_keywords)
	if selected_domains and selected_keywords:
		p_ids = Keyword_Pargraph.query.filter(Keyword_Pargraph.keyword_id.in_(selected_keywords)).all()
		p_ids = [p.pargraph_id for p in p_ids]
		pargraphs = Pargraph.query.filter(Pargraph.domain_id.in_(selected_domains),Pargraph.id.in_(p_ids)).all()
	elif selected_domains:
		pargraphs = Pargraph.query.filter(Pargraph.domain_id.in_(selected_domains)).all()
	elif selected_keywords:
		p_ids = Keyword_Pargraph.query.filter(Keyword_Pargraph.keyword_id.in_(selected_keywords)).all()
		p_ids = [p.pargraph_id for p in p_ids]
		pargraphs = Pargraph.query.filter(Pargraph.id.in_(p_ids)).all()
	else:
		p_ids = Keyword_Pargraph.query.all()
		p_ids = [p.pargraph_id for p in p_ids]
		pargraphs = Pargraph.query.filter(Pargraph.id.in_(p_ids)).all()


	data = [{"html":p.html , "domain":Domain.query.filter_by(id=p.domain_id).one().url ,"order":len(Keyword_Pargraph.query.filter_by(pargraph_id=p.id).all())} for p in pargraphs]
	data = sorted(data, key=itemgetter('order') , reverse = True) 
	return data[:20]


def reindex_data(keyword , keyword_id):
    all_ps = Pargraph.query.all()
    if all_ps:
        for p in all_ps:
            html = p.html
            flag = False
            if re.search(keyword, html):
                flag = True
                html = re.sub(keyword,'<mark>'+keyword+"</mark>", html)
                
            
            if flag:
                p.html = html
                db.session.commit()
                
                try:
                    Keyword_Pargraph.query.filter_by(pargraph_id=p.id,keyword_id=keyword_id).one()
                except Exception as e:
                    obj = Keyword_Pargraph(pargraph_id=p.id,keyword_id=keyword_id)
                    db.session.add(obj)
                    db.session.commit()

def unindex_data(keyword , keyword_id):
    all_ps = Pargraph.query.all()
    if all_ps:
        for p in all_ps:
            html = p.html
            flag = False
            if re.search(keyword, html):
                flag = True
                html = re.sub('<mark>'+keyword+"</mark>",keyword, html)
                
            
            if flag:
                p.html = html
                db.session.commit()
                
                try:
                    Keyword_Pargraph.query.filter_by(pargraph_id=p.id,keyword_id=keyword_id).delete()
                except Exception as e:
                    pass

def index_data(domain_id):
    keywords = Keyword.query.all()
    for (dirpath, dirnames, filenames) in os.walk("./data/"+str(domain_id)):#../patents data
        for file in filenames:
            html = None
            with open("./data/"+str(domain_id)+"/"+file , "rb") as f:
                html = f.read()
            soup = BeautifulSoup(html,"lxml")
            all_ps = soup.findAll("p")
            if all_ps:
                for p in all_ps:
                    
                    text = p.getText(strip=True)
                    
#                     print(p)
                    if text:
#                         print(text)

                        html = text

                        flag = False
                        keywords_in_paragraph = []
                        for w in keywords:
                            if re.search(w.ch_word, html):
                                flag = True
                                keywords_in_paragraph.append(w.id)
                                html = re.sub(w.ch_word,'<mark>'+w.ch_word+"</mark>", html)
    #                             print(html)

                        p_id = None
#                         print(text)

                        # print('-'*30)
                        # try:
                        #     obj = Pargraph.query.filter_by(file_name=file,domain_id=domain_id).one()
                        #     obj.text=text
                        #     obj.html=html
                        #     p_id = obj.id
                        #     db.session.commit()
                        # except Exception as e:
                        #     obj = Pargraph(text=text,html=html,domain_id=domain_id,file_name=file)
                        #     db.session.add(obj)
                        #     db.session.flush()
                        #     db.session.refresh(obj)
                        #     p_id = obj.id
                        #     db.session.commit()


                        obj = Pargraph(text=text,html=html,domain_id=domain_id,file_name=file)
                        db.session.add(obj)
                        db.session.flush()
                        db.session.refresh(obj)
                        p_id = obj.id
                        db.session.commit()


                        if flag:
                            for keyword_id in keywords_in_paragraph:
                                try:
                                    Keyword_Pargraph.query.filter_by(pargraph_id=p_id,keyword_id=keyword_id).one()
                                except Exception as e:
                                    obj = Keyword_Pargraph(pargraph_id=p_id,keyword_id=keyword_id)
                                    db.session.add(obj)
                                    db.session.commit()

        break


def index_all_data():
    start_time = time.time()
    domains = Domain.query.all()
    for d in domains:
        print(d.url)
        index_data(d.id)
    
    end_time = time.time() - start_time
    print("finished in ({}) s".format(end_time))


def crawl_index_data(url , domain_id):
    start_time = time.time()

    c = Crawler()
    c.scrape_data(url,domain_id)

    index_data(domain_id)

    obj = Domain.query.filter_by(id=domain_id).one()
    obj.status = "Done"
    db.session.commit()

    end_time = time.time() - start_time

    print("finished in ({}) s".format(end_time))

###########      data



# cron examples
# @scheduler.task('date', id='do_job_2')
# def job1():
#     print('Job 2 executed')
#     print("starting job")


@app.route("/admin" , methods =["GET"])
def admin():
	return render_template('admin.html')




###########      keyword routes





@app.route("/admin/keyword/show" , methods =["GET"])
def showkeyword():

	keywords = Keyword.query.all()
	return render_template('admin/keyword/show.html',keywords=keywords)

@app.route("/admin/keyword/delete/<id>" , methods =["GET"])
def deletekeyword(id):
	print("deleted " , id)
	obj = Keyword.query.filter_by(id=id).one()
	unindex_data(obj.ch_word , id)
	Keyword.query.filter_by(id=id).delete()
	db.session.commit()
	return redirect('/admin/keyword/show')

@app.route("/admin/keyword/edit/<id>" , methods =["GET" , "POST"])
def editkeyword(id):
	print(id)
	# edit
	if request.method == "POST":
		ch_word = request.form.get('ch_word')
		en_word = request.form.get('en_word')

		obj = Keyword.query.filter_by(id=id).one()
		unindex_data(obj.ch_word , id)

		obj.ch_word = ch_word
		obj.en_word = en_word
		db.session.commit()

		reindex_data(ch_word , id)


		return redirect('/admin/keyword/show')
	# show  one row
	elif request.method == "GET":
		# keyword = {'id':1,'name':'sport' , 'words':'("a","b")'}

		# t= keyword.query.filter_by(id=id).first()
		keyword = Keyword.query.filter_by(id=id).one()
		return render_template('/admin/keyword/edit.html',item = keyword)
	return "404"


@app.route("/admin/keyword/create" , methods =["GET" , "POST"])
def createkeyword():
	# edit
	if request.method == "POST":
		ch_word = request.form.get('ch_word')
		en_word = request.form.get('en_word')

		obj = Keyword(ch_word=ch_word,en_word=en_word)
		db.session.add(obj)
		db.session.flush()
		db.session.refresh(obj)
		keyword_id = obj.id
		db.session.commit()

		reindex_data(ch_word,keyword_id)

		return redirect('/admin/keyword/show')
	# show  one row
	elif request.method == "GET":
		return render_template('/admin/keyword/create.html')
	return "404"







###########      domain routes





@app.route("/admin/domain/show" , methods =["GET"])
def showdomain():
	domains = Domain.query.all()
	return render_template('admin/domain/show.html',domains=domains)

@app.route("/admin/domain/delete/<id>" , methods =["GET"])
def deletedomain(id):
	print("deleted " , id)

	Domain.query.filter_by(id=id).delete()
	db.session.commit()

	return redirect('/admin/domain/show')

@app.route("/admin/domain/edit/<id>" , methods =["GET" , "POST"])
def editdomain(id):
	print(id)
	# edit
	if request.method == "POST":
		url = request.form.get('url')

		obj = Domain.query.filter_by(id=id).one()
		obj.url = url
		obj.status = "crawling"
		db.session.commit()


		dd = datetime.now() + timedelta(seconds=3)
		scheduler.add_job(crawl_index_data, 'date',run_date=dd,id="tick_job", kwargs={'url':url,'domain_id':id})

		return redirect('/admin/domain/show')
	# show  one row
	elif request.method == "GET":
		domain = Domain.query.filter_by(id=id).one()
		return render_template('/admin/domain/edit.html',item = domain)
	return "404"


@app.route("/admin/domain/create" , methods =["GET" , "POST"])
def createdomain():
	# edit
	if request.method == "POST":
		url = request.form.get('url')

		obj = Domain(url=url,status="crawling")
		db.session.add(obj)
		db.session.flush()
		db.session.refresh(obj)
		domain_id = obj.id
		db.session.commit()


		dd = datetime.now() + timedelta(seconds=3)
		scheduler.add_job(crawl_index_data, 'date',run_date=dd,id="tick_job", kwargs={'url':url,'domain_id':domain_id})


		return redirect('/admin/domain/show')
	# show  one row
	elif request.method == "GET":
		return render_template('/admin/domain/create.html')
	return "404"







if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5001)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True, threaded=True)

