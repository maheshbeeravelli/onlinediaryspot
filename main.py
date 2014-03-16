#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import time
import jinja2
import os
import json
# import urllib

from google.appengine.api import users
from google.appengine.ext import db
from webapp2_extras import sessions

JINJA_ENVIRONMENT =jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'])
main_html="""
<html>
<head>
<title>Online Diary Spot</title>


<link rel="stylesheet" href="css/homestyle.css" />
<link rel="stylesheet" href="script/jquery-ui-1.10.3.custom.min.css" />
<meta name="google-site-verification" content="5iR9q41Qiwx3IutT38MTBUfyO5IScTQyxakuBkHc3-0" />
</head>
<body>
    <div id="pagewrap">
    <div id="maincontent">
    <p>%s</p>
	<div id="menu" style="width:auto;height:25px;">
    <a href="/">Home</a>
    <a href="/showall?PageNumber=1">Show All</a>
    </div>
    <div style="width:380px">
	<form method="post"><br/>
	<div class = "data_type" style="border:1px solid; border-radius:5px; box-shadow: 10px 10px 5px #888888;">
		<input name="data_type" type="radio" checked="true" value="Important Notes"/>Important Notes<br/>
		<input name="data_type" type="radio" value="Important Date"/>Important Date<br/>
		<input name="data_type" type="radio" value="Link"/>Favourite Link<br/>
	</div><br/>
    <div class="input_fields" style="padding: 5px 0px 5px 5px; border:1px solid; border-radius:5px; box-shadow: 10px 10px 5px #888888;">
	<div>Title:<br/><input name="data_title" type="text" width="50px" value="%s"/><br/></div>
	Text:<div><textarea type="textarea" rows="4" cols="41" name="data_description">%s</textarea><br/></div>
	Date (DD/MM/YYYY):<div float="left"><input type="text" id="datepicker" name="data_date"  width="50px" value="%s"/><br/></div>
    <script type="text/javascript">
  document.getElementById('datepicker').value = Date()toString('dd-MM-yyyy');
</script>
<input type="hidden" name="delete_key" value="%s"></input>
    
	<div style="padding-top:5px"><input type="submit" value="Save"/></div>
    </div><!-- end of input fields --> 
	</form>
    </div>
    </div><!-- End of maincontent -->
    </div><!-- End of pagewrap -->
</body>
</html>
"""
showall_html="""
<html>
<header>
<title>Online Diary Spot</title>
<style>
 input{
 border-spacing:15px;
 }
</style>
<script>
function confirmDelete() {
if (confirm("Really delete this article?")) {
return true;
} else {
return false;
} 
</script>
</header>
<body>
    <div id="menu" style="width:auto;height:25px;">
    <a href="/">Home</a>
    <a href="/showall">Show All</a>
    </div>
    <table border="1">
    <tr>
    <th>Title</th>
    <th>Description</th>
    <th>Data Type</th>
    <th>Date</th>
    <th>Added On</th>
    <th>Update</th>
    <th>Delete</th>
    </tr>
    <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
<script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
<script>
$(function() {
$( "#datepicker" ).datepicker({ dateFormat: "dd/mm/yy" });
});
</script>
</body>
<html>
"""
DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return db.Key('Guestbook', guestbook_name)

class MyDataStore(db.Model):
	author=db.UserProperty()
	title=db.StringProperty()
	text=db.TextProperty()
	date = db.StringProperty()
	data_type= db.StringProperty()
	added_on = db.DateTimeProperty(auto_now_add=True)
	
class ContactUs(db.Model):
  email=db.EmailProperty()
  author = db.EmailProperty()
  name=db.StringProperty()
  date=db.DateTimeProperty(auto_now_add=True)
  description=db.TextProperty()
  
class MyDataStoreDeleted(db.Model):
    author=db.UserProperty()
    title=db.StringProperty()
    text=db.TextProperty()
    date = db.StringProperty()
    data_type= db.StringProperty()
    deleted_added_on = db.DateTimeProperty(auto_now_add=True)
    added_on = db.DateTimeProperty()
        
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class Main(webapp2.RequestHandler):
    def get(self):
        user=users.get_current_user()
        if user:
            guestbook_name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
            # self.response.write("Hello WOrld")
            if(self.request.get('PageNumber')):
                fetch_page_number=self.request.get('PageNumber')
            else:
                fetch_page_number="1"
            all_rows = db.GqlQuery("SELECT * FROM MyDataStore WHERE author=:1",user)
            total_pages=all_rows.count()/10+1
            ftnumber=int(fetch_page_number)-1
            if(ftnumber!=0):
                limit_query = ("SELECT * FROM MyDataStore WHERE author=:1 ORDER BY added_on DESC LIMIT %s,%s"%(10*ftnumber,10))
            else:
                limit_query= ("SELECT * FROM MyDataStore WHERE author=:1 ORDER BY added_on DESC LIMIT %s"%10)
            
            user = users.get_current_user()
            data_query= db.GqlQuery(limit_query,user)
            logout_url=users.create_logout_url('/')
            template_values={'all_rows':data_query,'user':user,'web_action':'Signout','logout':logout_url,'page_no':int(fetch_page_number),'count_pages':total_pages,'link':'/?'}
            template = JINJA_ENVIRONMENT.get_template('offcanvas.html')
            self.response.write(template.render(template_values))
        else:
            web_action='Signin'
            action_url=users.create_login_url(self.request.uri)
            # self.redirect(users.create_login_url(self.request.uri))
            template_values={'web_action':'Signin','logout':action_url,'page_no':0,'count_pages':0,'link':'/?'}
            template = JINJA_ENVIRONMENT.get_template('offcanvas.html')
            self.response.write(template.render(template_values))
    def post(self):
             # self.response.out.headers["Content-Type"]="text/json"
             # t=self.request.get('data_type')
             # output={'data_type':t+" duck"}
             # output=json.dumps(output)
             # self.response.out.write(output)
             # guestbook_name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
        # greeting = MyDataStore(parent=guestbook_key(guestbook_name))
        if users.get_current_user():
            author=users.get_current_user()
        else:
            self.redirect(users.create_login_url(self.request.uri))
        # d_title = self.request.get('data_title')
        # d_text = self.request.get('data_description')
        # d_data_type=self.request.get('data_type')
        # d_date=self.request.get('data_date')
        data_title = self.request.get('data_title')
        data_description = self.request.get('data_description')
        data_type=self.request.get('data_type')
        data_date=self.request.get('data_date')
        #greeting.title = self.request.get('title')
        new_data=MyDataStore(author=author,title=data_title,text=data_description,data_type=data_type,date=data_date)
        new_data.put()
        reply='''<tr>
                    <td align="center" width="5px"><span class="a_modal"><span class="glyphicon glyphicon-eye-open"></span></span></td>
                    <td> 
                      {% if "Link" in row.data_type: %}
                      {% if (row.text[:7]=="http://") or (row.text[:8]=="https://"): %}
                      <a href="{{row.text}}" target="_blank">{{ row.title }}</a>
                      {% else: %}
                      <a href="{{"http://" + row.text}}" target="_blank">{{ row.title }}</a>
                      {% endif %}
                      {% else: %}
                      {{ row.title }}
                      {% endif %}
                    </td>
                    <td><div class="wrapword">{{row.text}}</div></td>
                    <td>{{row.data_type}}</td>
                    <td>{{row.date}}</td>
                    <td>{{row.added_on}}</td>
                    <td style="display:none">{{row.key()}}</td>

                  </tr>'''
        self.response.write('<html><header><meta http-equiv="refresh" content="1; url=/showall"></header><body>Your data is successfully submited. <br/>You will be redirected to the Showall page in 2sec.</body></html>')
    
class MainHandler(webapp2.RequestHandler):
    def get(self):
    	user = users.get_current_user()

        if user:
            #self.redirect("/main")
            #self.response.headers['Content-Type'] = 'text/plain'
            hello_user = 'Hello, ' + user.nickname() + '<a href="' + users.create_logout_url('/') +'" style="padding-left:5px;">Logout</a>'
            self.response.write(main_html%(hello_user,"","","",""))
        else:
            self.redirect(users.create_login_url(self.request.uri))
        
    def post(self):
    	
    	# guestbook_name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
    	# greeting = MyDataStore(parent=guestbook_key(guestbook_name))
    	if users.get_current_user():
    		author=users.get_current_user()
        else:
            self.redirect(users.create_login_url(self.request.uri))
    	# d_title = self.request.get('data_title')
    	# d_text = self.request.get('data_description')
    	# d_data_type=self.request.get('data_type')
    	# d_date=self.request.get('data_date')
        data_title = self.request.get('data_title')
        data_description = self.request.get('data_description')
        data_type=self.request.get('data_type')
        data_date=self.request.get('data_date')
    	#greeting.title = self.request.get('title')
        new_data=MyDataStore(author=author,title=data_title,text=data_description,data_type=data_type,date=data_date)
    	new_data.put()
    	self.response.write('<html><header><meta http-equiv="refresh" content="1; url=/showall"></header><body>Your data is successfully submited. <br/>You will be redirected to the Showall page in 2sec.</body></html>')
        # MainHandler.get()
class ShowAll(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # self.response.write("Hi mahesh how are you ?")
        #fetch_page_number=1
        #self.redirect("/main")
        if(self.request.get('PageNumber')):
            fetch_page_number=self.request.get('PageNumber')
        else:
            fetch_page_number="1"

        total_count = db.GqlQuery("SELECT * FROM MyDataStore WHERE author=:1",user)
        total_pages=total_count.count()/10+1
        ftnumber=int(fetch_page_number)-1
        
        if(ftnumber!=0):
            limit_query= ("SELECT * FROM MyDataStore WHERE author=:1 ORDER BY added_on DESC LIMIT %s,%s"%(10*ftnumber,10))
        else:
            limit_query= ("SELECT * FROM MyDataStore WHERE author=:1 ORDER BY added_on DESC LIMIT %s"%10)
        
        if user:
            #self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Hello, ' + user.nickname()+ '<a href="' + users.create_logout_url('/') +'" style="padding-left:5px;">Logout</a>'+"<br/>")
            self.response.write(showall_html)
            my_data = db.GqlQuery(limit_query,user)
            # my_data.fetch(0)
            for d in my_data:
                if(d.data_type=='Link'):
                    if(d.text[:7]=="http://"):
                      self.redirect("/")
        
                      table_rowfactoty=  ('<tr><td><a href="%s" target="_blank">%s</td>' % (d.text,d.title))    
                    else:
                        table_rowfactoty=  ('<tr><td><a href="http://%s" target="_blank">%s</td>' % (d.text,d.title))

                else:
                    table_rowfactoty=('<tr><td>%s</td>' % (d.title))
                self.response.write(table_rowfactoty)
                self.response.write("<td width=170px height=50px>"+d.text+"</td>")    
                self.response.write('<td>%s</td><td>%s</td><td>%s</td>' % (d.data_type,d.date,d.added_on))
                self.response.write('<td><a href="/update?Key=%s">Update</a></td>' % (d.key()))
                self.response.write('<td><a onClick="return confirmDelete();" href="/delete?Key=%s">Delete</a></td></tr>' % (d.key()))
                
        else:
            self.redirect(users.create_login_url(self.request.uri))
        
        if(total_pages==1):
            ftnumber_next=1

        if((ftnumber+2)>total_pages):
            ftnumber_next=total_pages
        else:
            ftnumber_next=ftnumber+2
        
            
        if(ftnumber!=0):
            self.response.write("<a href='/showall?PageNumber=%s'>Previous</a><a href='/showall?PageNumber=%s'>Next</a>"%(ftnumber,ftnumber_next))
        if(ftnumber==0):
            self.response.write("<a href='/showall?PageNumber=%s'>Previous</a><a href='/showall?PageNumber=%s'>Next</a>"%(1,ftnumber_next))



class Update(webapp2.RequestHandler):
    def get(self):
        user=users.get_current_user()
        hello_user = 'Hello, ' + user.nickname()+ '<a href="' + users.create_logout_url('/') +'" style="padding-left:5px;">Logout</a>'+"<br/>"
        key = self.request.get('Key')
        user = users.get_current_user()
        current_row= MyDataStore.get(key) #db.GqlQuery("SELECT * FROM MyDataStore WHERE ID=:1",key)
        self.response.write(main_html%(hello_user,current_row.title,current_row.text,current_row.date,key))
    def post(self):
        key = self.request.get('Key')
        current_row=MyDataStore.get(key)
        if users.get_current_user()==current_row.author:
            author=users.get_current_user()
            d_title = self.request.get('data_title')
            d_text = self.request.get('data_description')
            d_data_type=self.request.get('data_type')
            d_date=self.request.get('data_date')
            #greeting.title = self.request.get('title')
            #new_data=MyDataStore(author=author,title=d_title,text=d_text,data_type=d_data_type,date=d_date)
            current_row.title=d_title
            current_row.text=d_text
            current_row.data_type=d_data_type
            current_row.date=d_date
            current_row.put()
            self.response.write('<html><header><meta http-equiv="refresh" content="1; url=/showall"></header><body>Your data is successfully updated. <br/>You will be redirected to the Showall page in 2sec.</body></html>')
class Delete_Row(webapp2.RequestHandler):
    def get(self):
        current_row=""
        try:
            if(self.request.get('Key')):
                key = self.request.get('Key')
                current_row= MyDataStore.get(key)
            #self.response.write(current_row.author+users.get_current_user)
            if(users.get_current_user()==current_row.author):
                #self.response.write(current_row.author+users.get_current_user)
                #self.response.write("Do you really want to delete ?")
                new_data=MyDataStoreDeleted(author=current_row.author,title=current_row.title,text=current_row.text,data_type=current_row.data_type,date=current_row.date,added_on=current_row.added_on)
                new_data.put()
                current_row.delete()
                # self.redirect("/")
                self.response.write('<html><header><meta http-equiv="refresh" content="1; url=/"></header><body></body></html>')#Your data is successfully deleted. <br/>You will be redirected to the main page in 2sec.</body></html>')
        except Exception, e:
            self.redirect("/")
        # self.redirect('/showall')

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        #self.response.write('<html><header><meta http-equiv="refresh" content="1; url=/showall"></header><body>Your data is successfully updated. <br/>You will be redirected to the Showall page in 2sec.</body></html>')
        user=users.get_current_user()
        if user:
            if(self.request.get('keyword')):
                search_key=self.request.get('keyword')
            else:
                search_key=""
            guestbook_name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
            # self.response.write("Hello WOrld")
            if(self.request.get('PageNumber')):
                fetch_page_number=self.request.get('PageNumber')
            else:
                fetch_page_number="1"
            all_rows = db.GqlQuery("SELECT * FROM MyDataStore WHERE author=:1",user)
            # total_pages=all_rows.count()/10+1
            ftnumber=int(fetch_page_number)-1
            if(ftnumber!=0):
                limit_query = ("SELECT * FROM MyDataStore WHERE author=:1 ORDER BY added_on DESC")# LIMIT %s,%s"%(10*ftnumber,10))
            else:
                limit_query= ("SELECT * FROM MyDataStore WHERE author=:1 ORDER BY added_on DESC")# LIMIT")
            
            data_query1= db.GqlQuery(limit_query,user)
            # data_query =list(data_quer)
            data_query =[]
            for row in data_query1:
                if search_key.lower() in row.title.lower():
                    # self.response.write(row.text)
                    data_query.append(row)
                # else:
                #     data_query.remove(row)
            # for row in data_query:
            #     self.response.write(row.author)
            
            total_pages= len(data_query)/10+1
            from_list=10*(int(fetch_page_number)-1)
            logout_url=users.create_logout_url('/')
            template_values={'all_rows':data_query[from_list:from_list+10],'user':user,'web_action':'Signout','logout':logout_url,'page_no':int(fetch_page_number),'count_pages':total_pages,'link':'/search?keyword='+search_key+'&'}
            template = JINJA_ENVIRONMENT.get_template('offcanvas.html')
            self.response.write(template.render(template_values))
        else:
            # self.redirect(users.create_login_url(self.request.uri))

            web_action='Signin'
            action_url=users.create_login_url(self.request.uri)
            # self.redirect(users.create_login_url(self.request.uri))
            template_values={'web_action':'Signin','logout':action_url,'page_no':0,'count_pages':0,'link':'/?'}
            template = JINJA_ENVIRONMENT.get_template('offcanvas.html')
            self.response.write(template.render(template_values))

class Contactus(webapp2.RequestHandler):
    def post(self):
        
        try:
            #self.response.write(current_row.author+users.get_current_user)
            name=self.request.get("contactus_name")
            description = self.request.get("contactus_desc")
            user=users.get_current_user()
            if user:
                user_email=user.email()
                # self.response.write("1st your Query is successfully submitted"+name+":"+email+":"+description)
            else:
                email=self.request.get("contactus_email")
            new_data=ContactUs(email=email,author=user_email,name=name,description=description)
            new_data.put()
            # self.response.write("Your Query is successfully submitted"+name+":"+email+":"+description)
        except Exception, e:
            self.redirect("/")



app = webapp2.WSGIApplication([('/', Main),('/search', SearchHandler),
    ('/main', MainHandler),('/showall',ShowAll),('/update',Update),('/delete',Delete_Row),('/contactus',Contactus)
], debug=True)

