#################
#### imports ####
#################

import traceback
import json
import logging
from time import strftime
from datetime import datetime
from logging.handlers import RotatingFileHandler

from os.path import join, isfile

from flask import Flask, render_template, make_response, jsonify, request,g,session,redirect,url_for
import hashlib 
#import sqlite3
import psycopg2
from psycopg2 import Error

from markupsafe import Markup

import base64
import jwt

import random
import string
import functools

''' begin parameter '''
SECRET_KEY = '@d1t_Cut3'
URL_DB = 'data/dataDB.db'
IS_DEVELOPMENT = True

''' end paramter '''



"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth


################
#### config ####
################

"""

app = Flask(__name__)
app.config.from_pyfile('flask.cfg')
#db = SQLAlchemy(app)

"""

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
pagedown = PageDown(app)
migrate = Migrate(app, db)
auth = HTTPBasicAuth()
auth_token = HTTPBasicAuth()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"


from project.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


####################
#### blueprints ####
####################

from project.users.views import users_blueprint
from project.recipes.views import recipes_blueprint
from project.recipes_api.views import recipes_api_blueprint

# register the blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(recipes_blueprint)
app.register_blueprint(recipes_api_blueprint)

"""

############################
#### custom error pages ####
############################

"""
from project.models import ValidationError


@app.errorhandler(ValidationError)
def bad_request(e):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': e.args[0]})
    response.status_code = 400
    return response
"""

@app.errorhandler(400)
def page_not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 400)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# @app.errorhandler(404)
# def not_found(e):
#     response = jsonify({'status': 404, 'error': 'not found', 'message': 'invalid resource URI'})
#     response.status_code = 404
#     return response


@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403


@app.errorhandler(410)
def page_not_found(e):
    return render_template('410.html'), 410
	
############################
#### decorator check session ####
############################
	
def check_session(f):
	@functools.wraps(f)
	def wrap(*args, **kwargs):
		#print(request)
		#if 'key' in request.cookies:
		request_xhr_key = request.headers.get('X-Requested-With')
		if 'X-Requested-With' not in request.headers or request_xhr_key != 'XMLHttpRequest':
		#if request.is_xhr:
			return redirect('/')
		elif  'key' not in request.cookies:
			return redirect(url_for('logout'))
		elif session['iscomplete'] == False:
			logic = (request.path == '/profil/' or request.path =='/profil')
			# print("Halisnya : ", str(logic))
			if(logic==False and session["id_level_group"] >1):
				return redirect(url_for('profil.profil_index'))
		
		return f(*args, **kwargs)

	return wrap

def check_just_session(f):
	@functools.wraps(f)
	def wrap(*args, **kwargs):
		if 'key' not in request.cookies:
			return redirect(url_for('logout'))
		
		return f(*args, **kwargs)

	return wrap
	
############################
#### global function ####
############################

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']\
	

def allowed_file_zip(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS_ZIP']
		
def basedir():
	return app.config['TOP_LEVEL_DIR']
	
def getIdUserName():
	return session['id_username'] 


def noneToStringNull(stringparam):
	
	if str(stringparam) == 'None':		
		return str('')
	return str(stringparam)

def getMD5():
	dateTimeObj = datetime.now()
	timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
	return hashlib.md5( str(timestampStr).encode('utf-8')).hexdigest()

def encodeMD5(param):
	return  hashlib.md5( str(param).encode('utf-8')).hexdigest()


def encodeBase64(message):
	message_bytes = message.encode('ascii')
	base64_bytes = base64.b64encode(message_bytes)
	return base64_bytes.decode('ascii')

def decodeBase64(message):
	message_bytes = message.encode('ascii')
	base64_bytes = base64.b64decode(message_bytes)
	return base64_bytes.decode('ascii')
	
def getFieldNameQuery(query):
	con  = connect_db()
	cur = con.cursor() 	
	cur.execute(query+' limit 1')		
	total_fields = len(cur.description)    
	fields_names = [i[0] for i in cur.description]
	cur.close()
	con.close()	
	return fields_names
	
	
def convertSQLDataTable(query):
	tempQuery = 'SELECT * FROM ( '+query+' ) TABLESAUM  '
	start = request.args.get('start')
	length = request.args.get('length')
	fields_names = getFieldNameQuery(query)
	#print(fields_names)
	idx_sort = fields_names[int(request.args.get('order[0][column]'))]
	type_sort = request.args.get('order[0][dir]')
	if '1=1' in query:
		tempQuery = tempQuery #print "Found!"
	else:
		tempQuery = tempQuery + ' WHERE 1=1 ' #print "Not found!"
	
	if request.args.get('search[value]') != '':
		tempQuery = tempQuery + ' and ('
		ind = 0
		for x in fields_names:
			if ind == 0:
				tempQuery = tempQuery + ' lower('+ x +"::text)  LIKE lower('%"+request.args.get('search[value]')+"%')"
			else:
				tempQuery = tempQuery + ' OR lower('+ x +"::text) LIKE lower('%"+request.args.get('search[value]')+"%')"
			ind = ind + 1
		tempQuery = tempQuery + ' ) '
	
	#print(idx_sort)
	#print(type_sort)
	"""
	if( total > 0 && length > 0):
		total_pages = ceil(total/length)
	else: 
		total_pages = 0
	if ($page > $total_pages) $page=$total_pages;
	$start = $limit*$page - $limit;
	if($start <0) $start = 0; 
	"""
	sumTempQuery = tempQuery + ' ORDER BY '+idx_sort+' '+ type_sort+ ' OFFSET ' + start +' LIMIT  '+ str(int(start)+int(length))
	#print(sumTempQuery)
	return sumTempQuery
	

def validateUserPass(user,password):
	con  = connect_db()
	cur = con.cursor() 
	
	#encode_pass = hashlib.md5( str(password).encode('utf-8'))	
	#encode_pass = encodeMD5(password)
	
	#cur = g.db.execute('select user from taswil.a_user where password = ?',[encode_pass.hexdigest()] )
	
	cur.execute('select a.username,a.id_user,a.password,a.id_group,b.name_group,b.id_level_group,a.id_wilayah,a.fullname,a.iscomplete from taswil.a_user a,taswil.a_group b where a.id_group=b.id_group and a.username = %s and a.password = %s',[user,encodeBase64(password)] )		
	#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	#es = [dict(id=row[0]) for row in cur.fetchall()]
	es = []
	for  row in cur.fetchall():		
		if decodeBase64(row[2]) == password:
			es = [dict(id=row[0],id_user=row[1],id_group=row[3],name_group=row[4],id_level_group=row[5],id_wilayah=row[6],fullname=row[7],iscomplete=row[8])]		

	print(es,"hehe")
	cur.close()
	con.close()
	return es

def validateUserWPass(id_user):
	con  = connect_db()
	cur = con.cursor() 
	
	#encode_pass = hashlib.md5( str(password).encode('utf-8'))	
	#encode_pass = encodeMD5(password)
	
	#cur = g.db.execute('select user from taswil.a_user where password = ?',[encode_pass.hexdigest()] )
	
	cur.execute('select a.username,a.id_user,a.password,a.id_group,b.name_group,b.id_level_group,a.id_wilayah,a.fullname,a.iscomplete from taswil.a_user a,taswil.a_group b where a.id_group=b.id_group and a.id_user = %s',[id_user] )		
	#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	#es = [dict(id=row[0]) for row in cur.fetchall()]
	es=[]
	for  row in cur.fetchall():		
		es = [dict(id=row[0],id_user=row[1],password=row[2],id_group=row[3],name_group=row[4],id_level_group=row[5],id_wilayah=row[6],fullname=row[7],iscomplete=row[8])]		

	cur.close()
	con.close()
	return es

def isMenuHaveChild(id):
	con  = connect_db()
	cur = con.cursor() 
	es = 0
	try:
		cur.execute('select id_menu from taswil.a_menu where parent_id = %s',[id] )
		#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
		es = [dict(id=row[0]) for row in cur.fetchall()]
	except Error  as e:
		print(e)
	cur.close()
	con.close()
	if len(es) > 0:
		return True
	else:
		return False;
	
def getMenuRole(id_group,parent_id):
	con  = connect_db()
	cur = con.cursor()
	eHTML = ""
	try:
		cur.execute('SELECT B.*,a.is_add,a.is_update,a.is_delete,a.is_approve FROM taswil.a_group_menu A JOIN taswil.a_menu B ON A.id_menu = B.id_menu WHERE B.active = 0 and A.id_group = %s AND COALESCE(B.PARENT_ID,0) = %s order by b.sort',[id_group,parent_id] )
		
		#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]	
		for  es in cur.fetchall():
			
			if isMenuHaveChild(es[0]) == False:
				eHTML = eHTML + '<li>'
				#eHTML = eHTML + '   <a class="nav-link" href="' + str(es[3]) + '">'
				eHTML = eHTML + '   <a href="#"  dataurl="' + str(es[3]) + '" isAdd="' + str(es[7]) + '"  isUpdate="' + str(es[8]) + '"  isDelete="' + str(es[9]) + '"  isApprove="' + str(es[10]) + '" >'
				eHTML = eHTML + '<i class="mdi mdi-'+str(es[6])+' mr-2"></i>'+ str(es[1])
				eHTML = eHTML + '	</a>'
				eHTML = eHTML + '<li class="nav-item   ">'
				
			else:
				eHTML = eHTML + '<li>'
				#<a class="has-arrow" href="#" aria-expanded="false">Menu 1.3</a>
				if str(es[2]) == '0':
					eHTML = eHTML + ' <a class="has-arrow waves-effect waves-dark" href="#" aria-expanded="false">   <i class="mdi mdi-'+str(es[6])+'"></i>'
					eHTML = eHTML + ' <span class="hide-menu">'+str(es[1])+'</span>'
				else:
					eHTML = eHTML + '<a class="has-arrow" href="#" aria-expanded="false">'+str(es[1])+'</a>'	
				eHTML = eHTML + '	</a>'				
				eHTML = eHTML + '                             <ul aria-expanded="false" class="collapse">'
				eHTML = eHTML + getMenuRole(id_group,es[0])
				eHTML = eHTML + ' </ul>'
				eHTML = eHTML + '</li>'
			
		
			#print(eHTML)
			#print(es[0])
			#print(es[1])
	except Error  as e:
		print(e)
	cur.close()
	con.close()
	return eHTML
	
def randomCharacter(length):
	chars = string.ascii_letters+'1234567890'
	return ''.join(random.choice(chars) for x in range(length))
	
def getUserRole(username,withIsComplete=True):
	# print(username)
	con  = connect_db()
	cur = con.cursor() 
	parHTML = ""
	session['username'] = username[0].get('id')
	session['id_user'] = username[0].get('id_user')
	session['id_level_group'] = username[0].get('id_level_group')
	session['id_group'] = username[0].get('id_group')
	session['name_group'] = username[0].get('name_group') 
	session['id_wilayah'] = noneToStringNull(username[0].get('id_wilayah')) 
	if (withIsComplete):
		session['iscomplete'] = username[0].get('iscomplete') 	
		session['fullname'] = username[0].get('fullname') 
	#print(username[0].get('id'))
	try:
		cur.execute('SELECT id_group FROM taswil.a_user WHERE username = %s',[username[0].get('id')] )
		#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
		es = [dict(id_group=row[0]) for row in cur.fetchall()]
		parHTML = ' <ul id="sidebarnav">'
		parHTML = parHTML + getMenuRole(es[0].get('id_group'),0)
		parHTML = parHTML + ' </ul>'
	except Error  as e:
		print(e)
	cur.close()
	con.close()
	return parHTML

def getCountTable(query):
	con  = connect_db()
	cur = con.cursor() 
	result = 0
	try:
		#print(username[0].get('id'))
		cur.execute(query)
		#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
		#es = [dict(count=row[0]) for row in cur.fetchone()]
		#if cur.fetchone() is not None:		
		result =cur.fetchone()[0]
	except Error  as e:
		print(e)
	cur.close()
	con.close()
	return int(result)

def getOneValue(table,field,condition):
	con  = connect_db()
	cur = con.cursor() 
	result = ""
	try:
		#print(username[0].get('id'))
		cur.execute("select "+field+" from "+table+" where "+condition+" limit 1")
		#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
		#es = [dict(count=row[0]) for row in cur.fetchone()]	
		#if cur.fetchone() is not None:
		#result =cur.fetchone()[0]
		data = cur.fetchall()
		if len(data)>0:			
			#result =cur.fetchone()[0] 
			result =data[0][0]
	except Error  as e:
		print(e)
	cur.close()
	con.close()
	return (result)

def getOneValueByQuery(query):
	con  = connect_db()
	cur = con.cursor() 
	result = ""
	try:
		#print(username[0].get('id'))
		cur.execute(query+" limit 1")
		#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
		#es = [dict(count=row[0]) for row in cur.fetchone()]
		#print(cur.fetchone()[0])
		#if cur.fetchone()[0] is not None:
		#if cur.fetchone() is not None and len(cur.fetchone()) > 0:
		
		result =cur.fetchone()[0]
	except Error  as e:
		print(e)
	cur.close()
	con.close()
	return (result)

def getUserName():
	return session['username']

def getWilayahById(id_wilayah):
	data = {}
	data["id_wilayah"] = ""
	data["nama"] = ""
	data["fullname_wilayah"]=""
	if (len(noneToStringNull(id_wilayah)) >0):
		con  = connect_db()
		c = con.cursor() 


		strQuery = """
		select id,nama,ref from (
			select mp.id_provinsi as id, mp.nama as nama, null as ref from taswil.m_provinsi mp 
			union
			select mk.id_kabkota as id, mk.nama as nama, mk.id_provinsi as ref from taswil.m_kabkota mk 
			union
			select mk2.id_kecamatan as id, mk2.nama as nama,mk2.id_kabkota as ref from taswil.m_kecamatan mk2 
			union
			select md.id_desa as id, md.nama as nama, md.id_kecamatan as ref from taswil.m_desa md ) wil
		where wil.id= %s
		"""
		c.execute(strQuery,[id_wilayah])
		r = c.fetchone()
		ref = r[2]
		fullname_wilayah = r[1]
		data["id_wilayah"] = id_wilayah
		data["nama"] = r[1]
		while ref != None:
			c.execute(strQuery,[ref])
			r = c.fetchone()
			fullname_wilayah += ', '+r[1]
			ref = r[2]

		data["fullname_wilayah"] = fullname_wilayah

		c.close()

	return data

def connect_db():
	#if isfile('data/dataDB.db'):
	'''
	print(app.config['POSTGRES_USER'])
	print(app.config['POSTGRES_PASSWORD'])
	print(app.config['POSTGRES_HOST'])
	print(app.config['POSTGRES_PORT'])
	print(app.config['POSTGRES_DB'])
	'''
	#return sqlite3.connect(URL_DB)
	return psycopg2.connect(user = app.config['POSTGRES_USER'], password = app.config['POSTGRES_PASSWORD'], host = app.config['POSTGRES_HOST'], port = app.config['POSTGRES_PORT'], database = app.config['POSTGRES_DB'])
	
def validJWT(encoded):
	result = "-"
	try:
		payload = jwt.decode(encoded, SECRET_KEY)		
		result = payload.get('username')
	except jwt.InvalidTokenError:
		#pass  # do something sensible here, e.g. return HTTP 403 status code
		
		result = "-"
	return result

@app.route('/logout', methods=['GET'])
def logout():

	lablecaptcha = randomCharacter(5)
	session['captcha'] = lablecaptcha
	resp = make_response(render_template('login.html',rchar=lablecaptcha))
	resp.set_cookie('key', '', expires=0)
	resp.delete_cookie('key')
	#decodejwt = request.cookies.get('key')			
	#print(decodejwt)
	return resp

@app.route('/cuser', methods=['GET'])
def cuser():
	if(IS_DEVELOPMENT):
		id_user = request.args.get('idu')
		try:
			isValidUser = validateUserWPass(id_user)		
			if  len(isValidUser) > 0:		
				#return render_template('test.html', movies=movies, name=name)
				#resp = make_response(render_template(...))
				#resp.set_cookie('username', 'the username')
				# print(isValidUser)
				payload = {
					'username': isValidUser,
					'password': decodeBase64(isValidUser[0]['password'])
				}
				encodedjwt  = jwt.encode(payload, SECRET_KEY)
				pHTML = getUserRole(isValidUser)	
				print(isValidUser)				
				#print(pHTML)
				#print(isValidUser[0].get('id'))
				#print(isValidUser[0].get('id'))
				# profille = getOneValueByQuery("SELECT COALESCE('Nama : '||a.fullname,'')|| COALESCE(', '||test.nama,'')|| COALESCE(', Role : '||b.name_group,'') || ' <script>var id_kabkota_desa = '''||test.id||'''</script>' namaa FROM TASWIL.A_USER A 	LEFT JOIN TASWIL.A_group B ON A.ID_group = B.ID_group 	LEFT JOIN 	( 		select 'Kecamatan '||bb.nama nama,aa.ID_USER ,aa.id_kabkota id from taswil.a_user_moderator AA 		join taswil.a_user cc on aa.id_user = cc.id_user   	JOIN taswil.m_kabkota bb on aa.id_kabkota = bb.id_kabkota 			where cc.username = '"+isValidUser[0].get('id')+"' 		union 		select 'Desa '||bb.nama nama,aa.ID_USER,aa.id_desa id from taswil.a_user_desa AA 	join taswil.a_user cc on aa.id_user = cc.id_user   		JOIN taswil.m_desa bb on aa.id_desa = bb.id_desa 			where cc.username = '"+isValidUser[0].get('id')+"' ) test on A.ID_USER = TEST.ID_USER 	WHERE A.username = '"+isValidUser[0].get('id')+"'")
				#print("Dfsdfsdf " + str(profille))
				profille = getNamaProfil()
				a_id_wilayah = noneToStringNull(session['id_wilayah'])
				resp = make_response(render_template('index.html',menu_html=Markup(pHTML),profille=Markup(profille),dd_change_user=Markup(getDropdownChangeUser()),home_alert=Markup(getHomeAlert()),a_id_wilayah=a_id_wilayah))
				resp.set_cookie('key',encodedjwt)
				return resp
				# redirect("/")
			else:
				return render_template('login.html',error="User and Password is not valid")			
		except Error  as e:
			return render_template('login.html',error="Error connection")
	else:
		redirect("/")
	#decodejwt = request.cookies.get('key')			
	#print(decodejwt)
	# return id_user

@app.route('/', methods=['GET', 'POST'])
def index():
	lablecaptcha = randomCharacter(5)
			
	if request.method == 'POST':
		#print(encodeBase64('password'))
		userForm = request.form.get('txtUsername')
		passwordForm = request.form.get('txtPassword')
		chaptchaForm = request.form.get('txtChatcha')
		try:
			isValidUser = validateUserPass(userForm,passwordForm)
			if session['captcha'] == chaptchaForm:
				if  len(isValidUser) > 0:		
					#return render_template('test.html', movies=movies, name=name)
					#resp = make_response(render_template(...))
					#resp.set_cookie('username', 'the username')
					payload = {
						'username': isValidUser,
						'password': passwordForm
					}
					encodedjwt  = jwt.encode(payload, SECRET_KEY)
					pHTML = getUserRole(isValidUser)	
					print(isValidUser)				
					#print(pHTML)
					#print(isValidUser[0].get('id'))
					#print(isValidUser[0].get('id'))
					# profille = getOneValueByQuery("SELECT COALESCE('Nama : '||a.fullname,'')|| COALESCE(', '||test.nama,'')|| COALESCE(', Role : '||b.name_group,'') || ' <script>var id_kabkota_desa = '''||test.id||'''</script>' namaa FROM TASWIL.A_USER A 	LEFT JOIN TASWIL.A_group B ON A.ID_group = B.ID_group 	LEFT JOIN 	( 		select 'Kecamatan '||bb.nama nama,aa.ID_USER ,aa.id_kabkota id from taswil.a_user_moderator AA 		join taswil.a_user cc on aa.id_user = cc.id_user   	JOIN taswil.m_kabkota bb on aa.id_kabkota = bb.id_kabkota 			where cc.username = '"+isValidUser[0].get('id')+"' 		union 		select 'Desa '||bb.nama nama,aa.ID_USER,aa.id_desa id from taswil.a_user_desa AA 	join taswil.a_user cc on aa.id_user = cc.id_user   		JOIN taswil.m_desa bb on aa.id_desa = bb.id_desa 			where cc.username = '"+isValidUser[0].get('id')+"' ) test on A.ID_USER = TEST.ID_USER 	WHERE A.username = '"+isValidUser[0].get('id')+"'")
					#print("Dfsdfsdf " + str(profille))
					profille = getNamaProfil()
					a_id_wilayah=noneToStringNull(session['id_wilayah'])


					resp = make_response(render_template('index.html',menu_html=Markup(pHTML),profille=Markup(profille),dd_change_user=Markup(getDropdownChangeUser()),home_alert=Markup(getHomeAlert()),a_id_wilayah=a_id_wilayah))
					resp.set_cookie('key',encodedjwt)
					return resp
				else:
					session['captcha'] = lablecaptcha
					return render_template('login.html',error="User and Password is not valid",rchar=lablecaptcha)
			else:
				session['captcha'] = lablecaptcha
				return render_template('login.html',error="Chaptcha error",rchar=lablecaptcha)
		except Error  as e:
			session['captcha'] = lablecaptcha
			return render_template('login.html',error="Error connection",rchar=lablecaptcha)
		
	else:
		# print(app.config['FLASK_ENV'])
		decodejwt = request.cookies.get('key')			
		#print(decodejwt)
		if decodejwt is not None and validJWT(decodejwt) != '-':
			#return render_template('index.html')
			#return render_template('login.html',error="")					
			isValidUser = validJWT(decodejwt)
			#print(isValidUser[0].get('id'))
			
			# profille = getOneValueByQuery("SELECT COALESCE('Nama : '||a.fullname,'')|| COALESCE(', '||test.nama,'')|| COALESCE(', Role : '||b.name_group,'') || ' <script>var id_kabkota_desa = '''||test.id||'''</script>' namaa FROM TASWIL.A_USER A 	LEFT JOIN TASWIL.A_group B ON A.ID_group = B.ID_group 	LEFT JOIN 	( 		select 'Kecamatan '||bb.nama nama,aa.ID_USER ,aa.id_kabkota id from taswil.a_user_moderator AA 		join taswil.a_user cc on aa.id_user = cc.id_user   	JOIN taswil.m_kabkota bb on aa.id_kabkota = bb.id_kabkota 			where cc.username = '"+isValidUser[0].get('id')+"' 		union 		select 'Desa '||bb.nama nama,aa.ID_USER,aa.id_desa id from taswil.a_user_desa AA 	join taswil.a_user cc on aa.id_user = cc.id_user   		JOIN taswil.m_desa bb on aa.id_desa = bb.id_desa 			where cc.username = '"+isValidUser[0].get('id')+"' ) test on A.ID_USER = TEST.ID_USER 	WHERE A.username = '"+isValidUser[0].get('id')+"'")
			profille =getNamaProfil()

			# profille ='Nama : '+ session["fullname"] 
			# print(isValidUser)
			a_id_wilayah = noneToStringNull(session["id_wilayah"])
			pHTML = getUserRole(isValidUser,False)			
			return render_template('index.html',menu_html=Markup(pHTML),profille=Markup(profille), dd_change_user=Markup(getDropdownChangeUser()),			home_alert=Markup(getHomeAlert()),	a_id_wilayah=a_id_wilayah)
		else:
			lablecaptcha = randomCharacter(5)
			session['captcha'] = lablecaptcha
			return render_template('login.html',error="",rchar=lablecaptcha)
			
def getDropdownChangeUser():
	con  = connect_db()
	c = con.cursor() 	
	dropdownHtml = ''
	if(IS_DEVELOPMENT):	
		dropdownHtml = ' <select name="" id="dropdown-c-user" class="form-control"><option value="" selected disabled>--Plih akun--</option>'
		c.execute("SELECT id_user,username,fullname,b.name_group FROM taswil.a_user a, taswil.a_group b WHERE a.isdelete <> 1 and a.id_group=b.id_group ORDER BY fullname asc")
		for x in c.fetchall():
			dropdownHtml+= '<option value="'+x[0]+'" >'+x[2]+' ('+x[1]+') | '+x[3]+' </option>'

		dropdownHtml +='</select>'

	c.close()
	con.close()
	return dropdownHtml


def getNamaProfil():
	profille ='Nama : '+ session["fullname"]
	id_wilayah =  noneToStringNull(session['id_wilayah'])
	if len(id_wilayah) != 0:
		wilayah = getWilayahById(id_wilayah)
		# print(wilayah)
		profille += ', '+wilayah['nama']
	
	return profille

def getHomeAlert():
	id_level_group = session["id_level_group"]
	iscomplete = session["iscomplete"]

	htmlAlert = ''

	if(id_level_group > 1 and iscomplete == False):
		htmlAlert ="""
			 <div class="alert alert-danger" style="width: 100%;" role="alert">
                        Untuk dapat menggunakan semua fitur aplikasi silakan lengkapi data profil <a class="alert-link"
                            href="javascript:void(0)" onclick="execURL('/profil')">disini</a>.
            </div>
		"""
	
	return htmlAlert

@app.route('/session')
def session_get():
	print(session)
	return session["username"]
	



@app.route('/captcha')
#@check_session
def api_captcha():
	
	lablecaptcha = randomCharacter(5)
	session['captcha'] = lablecaptcha
	
	return jsonify(
       data = lablecaptcha
    )
	
	#return ""


from app.admin.routes import mod
from app.master.routes import mod
from app.transaction.routes import mod
from app.chat.routes import mod

from app.profil.routes import mod

from app.toponim.routes import mod

from app.transaction.routes_kab import mod

from app.monitoring.routes import mod

app.register_blueprint(admin.routes.mod, url_prefix='/admin')
app.register_blueprint(master.routes.mod, url_prefix='/master')
app.register_blueprint(transaction.routes.mod, url_prefix='/transaction')
app.register_blueprint(chat.routes.mod, url_prefix='/chat')
app.register_blueprint(profil.routes.mod, url_prefix='/profil')

app.register_blueprint(toponim.routes.mod, url_prefix='/toponim')

app.register_blueprint(transaction.routes_kab.mod, url_prefix='/transaction')


app.register_blueprint(monitoring.routes.mod, url_prefix='/monitoring')


@app.before_request
def before_request():
	
	timestamp = strftime('[%Y-%b-%d %H:%M]')
	#app.logger.info('%s Headers: %s', timestamp, request.headers)
	#app.logger.info('%s Body: %s', timestamp, request.get_data())
	

'''
@app.after_request
def after_request(response):
	timestamp = strftime('[%Y-%b-%d %H:%M]')
	app.logger.info('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)	
	return response


@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    app.logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, tb)
    return e.status_code

'''