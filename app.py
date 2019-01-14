
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
from sqlalchemy import desc
from operator import itemgetter
from flask import make_response
import time


app = Flask(__name__)

cwd = os.getcwd()
print(cwd)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+cwd+'/resources/data.db'
db = SQLAlchemy(app)


from models import *
 
 
@app.route("/" , methods =["POST" , "GET"])
def main():

	data = {}
	if request.method == "POST":

		resp = {"success":False}
		selected_domains = request.form.get('domains')
		selected_keywords = request.form.get('keywors')
		try:
			data = get_data(selected_domains,selected_keywords)
			resp["data"] = data
			resp["success"] = True
		except Exception as e:
			print(e)

		
		resp = json.dumps(resp, ensure_ascii=False).encode('utf8')
		resp = make_response(resp);
        resp.headers["Content-Type"]='application/json; charset=utf-8';

		return resp
	else: # get request
		domains = get_domains()
		keywords = getkeywords()
		data = get_data()
		return render_template('index.html',keywords = keywords ,domains = domains, data=data)
 



def get_domains():
	domains = Domain.query.all()
	return domains

def getkeywords():
	keywords = Keyword.query.all()
	return keywords

def get_data(selected_domains=None , selected_keywords=None):
	# ss= Sentiment.query.filter_by(topic_id=selected_topic[2:]).order_by(Sentiment.date).all()
	# ss= Sentiment.query.filter(Sentiment.tweet_id.in_(selected_tweets)).order_by(Sentiment.date).all()
	pargraphs = []
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
		pargraphs = Pargraph.query.all()


	data = [{"html":p.html , "domain":Domain.query.filter_by(id=p.domain_id).one().url ,"order":len(Keyword_Pargraph.query.filter_by(pargraph_id=p.id).all())} for p in pargraphs]
	data = sorted(data, key=itemgetter('order')) 
	return data






###########      data



@app.route("/admin" , methods =["GET"])
def admin():
	return render_template('admin.html')




###########      topic routes





@app.route("/admin/topic/show" , methods =["GET"])
def showtopic():
	# topics = [{'id':1,'name':'sport' , 'words':'("a","b")'}]
	tt= Topic.query.all()
	topics = [{'id':t.id , 'name':t.name , 'words':t.words} for t in tt]
	return render_template('admin/topic/show.html',topics=topics)

@app.route("/admin/topic/delete/<id>" , methods =["GET"])
def deletetopic(id):
	print("deleted " , id)
	return redirect('/admin/topic/show')

@app.route("/admin/topic/edit/<id>" , methods =["GET" , "POST"])
def edittopic(id):
	print(id)
	# edit
	if request.method == "POST":
		name = request.form.get('name')
		words = request.form.get('words')
		print(name,words)
		return redirect('/admin/topic/show')
	# show  one row
	elif request.method == "GET":
		# topic = {'id':1,'name':'sport' , 'words':'("a","b")'}

		t= Topic.query.filter_by(id=id).first()
		topic = {'id':t.id , 'name':t.name , 'words':t.words}
		return render_template('/admin/topic/edit.html',item = topic)
	return "404"


@app.route("/admin/topic/create" , methods =["GET" , "POST"])
def createtopic():
	# edit
	if request.method == "POST":
		name = request.form.get('name')
		words = request.form.get('words')
		print(name,words)
		return redirect('/admin/topic/show')
	# show  one row
	elif request.method == "GET":
		return render_template('/admin/topic/create.html')
	return "404"







###########      user routes





@app.route("/admin/user/show" , methods =["GET"])
def showuser():
	users = [{'id':1,'name':'sport' , 'words':'("a","b")'}]
	return render_template('admin/user/show.html',users=users)

@app.route("/admin/user/delete/<id>" , methods =["GET"])
def deleteuser(id):
	print("deleted " , id)
	return redirect('/admin/user/show')

@app.route("/admin/user/edit/<id>" , methods =["GET" , "POST"])
def edituser(id):
	print(id)
	# edit
	if request.method == "POST":
		name = request.form.get('name')
		words = request.form.get('words')
		print(name,words)
		return redirect('/admin/user/show')
	# show  one row
	elif request.method == "GET":
		user = {'id':1,'name':'sport' , 'words':'("a","b")'}
		return render_template('/admin/user/edit.html',item = user)
	return "404"


@app.route("/admin/user/create" , methods =["GET" , "POST"])
def createuser():
	# edit
	if request.method == "POST":
		name = request.form.get('name')
		words = request.form.get('words')
		print(name,words)
		return redirect('/admin/user/show')
	# show  one row
	elif request.method == "GET":
		return render_template('/admin/user/create.html')
	return "404"







if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5001)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True, threaded=True)

