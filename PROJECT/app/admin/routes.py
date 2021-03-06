from flask import Blueprint, render_template,jsonify,request,g,session
from app import connect_db,validJWT,noneToStringNull,decodeBase64,encodeBase64,getCountTable,convertSQLDataTable,randomCharacter,getUserName,check_session,getOneValue
#from sqlite3 import Error
from psycopg2 import Error

from coolname import generate

from markupsafe import Markup

mod = Blueprint('admin', __name__, template_folder='templates')


######################
#### DROPDOWNLIST ####
######################


@mod.route('/role/dropdownlist')
@check_session
def role_dropdownlist():
	strQuery = ""
	type = request.args.get('type')
	search = request.args.get('search')
	if type == "1":
		strQuery = "SELECT ID_GROUP,NAME_GROUP FROM taswil.a_group where id_group <> '1mfR' and isdelete<>'1' and lower(name_group) like lower('%"+search+"%')"

	con  = connect_db()
	cur = con.cursor() 
	#print(username[0].get('id'))
	#cur.execute('SELECT * FROM taswil.a_group ')
	cur.execute(strQuery)
	#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	es = [dict(id=row[0],name=row[1]) for row in cur.fetchall()]
	cur.close()
	con.close()
	
	return jsonify(		
        data=es
    )


######################
#### USER PROFILE ####
######################


@mod.route('/userprofile')
@check_session
def userprofile_index():
	#res
	#return render_template('userprofile.html',header_menu='USER PROFILE')
	username = validJWT(request.cookies.get('key'))
	
	con  = connect_db()
	cur = con.cursor() 
	#print(username[0].get('id'))
	cur.execute('SELECT * FROM TASWIL.a_user WHERE username = %s',[username[0].get('id')] )
	#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	for  es in cur.fetchall():		
		id = es[0]
		userprofile_user = noneToStringNull(str(es[1]))
		userprofile_pass = noneToStringNull(decodeBase64(str(es[2])))
		userprofile_fullname = noneToStringNull(str(es[3]))
		userprofile_phone = noneToStringNull(str(es[18]))
		userprofile_address = noneToStringNull(str(es[20]))
		userprofile_bplace = noneToStringNull(str(es[17]))
		userprofile_bdate = noneToStringNull(str(es[16]))
		userprofile_email = noneToStringNull(str(es[19]))
		userprofile_sex = noneToStringNull(str(es[12]))
	#es = [dict(id_role=row[0]) for row in cur.fetchall()]	
	cur.close()
	con.close()
	session['id'] = id
	return jsonify(
        data=render_template('userprofile_form.html',userprofile_user=userprofile_user,userprofile_pass=userprofile_pass,userprofile_fullname=userprofile_fullname,userprofile_phone=userprofile_phone,userprofile_address=userprofile_address,userprofile_bplace=userprofile_bplace,userprofile_bdate=userprofile_bdate,userprofile_email=userprofile_email,userprofile_sex=userprofile_sex),        
        header='USER PROFILE'
    )

@mod.route('/userprofile/update', methods=['POST'])
@check_session
def userprofile_update():
	paramResult = True
	paramError = ''
	
	id = session['id']
	#print(id)
	asdasd111 = request.form['userprofile_user']
	
	conn = connect_db()
	c = conn.cursor()
	try:
		'''c.execute('create table movies (id int, name text, category text)')
		c.execute('insert into movies (id, name, category) values (?, ?, ?)', (1, 'Alien', 'sci-fi'))
		c.execute('insert into movies (id, name, category) values (?, ?, ?)', (2, 'Aliens', 'sci-fi'))
		c.execute('insert into movies (id, name, category) values (?, ?, ?)', (3, 'Prometheus', 'sci-fi'))'''
		c.execute('update TASWIL.a_user set password = %s,gender = %s, fullname = %s,mobile = %s,address = %s, birth_place = %s,birth_date = %s,email = %s where id_user = %s',[encodeBase64(request.form['userprofile_pass']),request.form['userprofile_sex'],request.form['userprofile_fullname'],request.form['userprofile_phone'],request.form['userprofile_address'],request.form['userprofile_bplace'],request.form['userprofile_bdate'],request.form['userprofile_email'],id])
		paramError = "Save data success"
	except Error  as e:
		result = False
		paramError = str(e)
		assert 'table movies already exists' in str(e)
		
		
	conn.commit()
	conn.close()
	
	#res
	#return render_template('userprofile.html',header_menu='USER PROFILE')
	#session.pop('id', None) #clear session key id
	return jsonify(
        result = paramResult,
		error = paramError
    )



##############
#### ROLE ####
##############


@mod.route('/role')
@check_session
def role_index():	
	return jsonify(
        data=render_template('role.html'),        
        header='ROLE'
    )

@mod.route('/role/form')
@check_session
def role_form():	
	#res
	#return render_template('userprofile.html',header_menu='USER PROFILE')
	con  = connect_db()

	type = request.args.get('type')
	a_role_id_group = ''
	a_role_name_group = ''
	a_role_active = ''
	a_role_disabled = ''
	typechar = 'Tambah'
	rc = con.cursor()
	rc.execute("Select * from taswil.a_level_group where isactive =true")
	role_scopes = rc.fetchall()
	
	session['type'] = type
	
	selected_scope = 0

	if type == '2':
		typechar = 'Edit'
		id = request.args.get('id')
		
		cur = con.cursor() 		
		cur.execute('SELECT * FROM taswil.a_group WHERE isdelete = %s and id_group <> %s and id_group = %s',['0','1mfR',id])
		a_role_disabled = 'disabled'
		#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
		for  es in cur.fetchall():		
			id = es[0]
			# print(es)
			a_role_id_group = noneToStringNull(str(es[0]))		
			a_role_name_group = noneToStringNull(str(es[1]))
			a_role_active = noneToStringNull(str(es[6]))	
			selected_scope = es[8]	
		cur.close()
		session['p1'] = id
	
	scopes_html = ""
	for r in role_scopes:
		selected =""
		if r[0] == selected_scope:
			selected= "selected"

		scopes_html += '<option value="'+noneToStringNull(r[0])+'" '+selected+'>'+r[1]+'</option>'

	# print(scopes_html)
	con.close()

	return jsonify(
        data=render_template('rule_form.html',a_role_id_group=a_role_id_group,a_role_name_group=a_role_name_group,a_role_active=a_role_active,type=typechar,a_role_disabled=a_role_disabled,a_role_scope=Markup(scopes_html))
    )

@mod.route('/role/data')
@check_session
def role_data():		
	con  = connect_db()
	cur = con.cursor() 
	#print(username[0].get('id'))
	#cur.execute('SELECT * FROM taswil.a_group ')
	cur.execute(convertSQLDataTable("SELECT a.ID_GROUP,a.NAME_GROUP,b.description as scope FROM taswil.a_group a,taswil.a_level_group b where a.id_group <> '1mfR' and a.isdelete<>'1' and a.id_level_group=b.id_level"))
	#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	es = [dict(id=row[0],name=row[1],scope=row[2],btn='<div id="dt-buttons" class="dt-buttons"><a class="dt-button buttons-copy buttons-html5 btnEditForm" dataid="'+(row[0])+'" tabindex="0" ><span>Edit</span></a><a class="dt-button buttons-copy buttons-html5 btnDeleteForm" dataid="'+(row[0])+'" tabindex="0"  data-toggle="modal" data-target="#top-modal"><span>Delete</span></a></div>') for row in cur.fetchall()]
	cur.close()
	con.close()
	
	#print(list)
	print(es)
	jmldata = getCountTable("select count(1) count1 from taswil.a_group  where id_group <> '1mfR' and isdelete<>'1'")
	return jsonify(
		draw =  int(request.args.get('draw')), recordsTotal= jmldata , recordsFiltered = jmldata,
        data=es
    )

@mod.route('/role/crud', methods = ['POST', 'DELETE'])
@check_session
def role_crud():		
	paramResult = True
	paramError = ''
	
	type = session['type']
	#print(id)
	#asdasd111 = request.form['userprofile_user']
	
	conn = connect_db()
	c = conn.cursor()
	try:
		if 'type' in request.json and request.json['type'] == 3:			
			c.execute('update taswil.a_group set isdelete= %s , useredit = %s,dateedit = now() where id_group = %s',['1',getUserName(),request.json['id']])
		
		else:	
			
			if type == '2':
				p1 = session['p1']
				params = [request.json['role_name_group'],request.json['role_active'],getUserName(),request.json['role_scope'],p1]
				c.execute('update taswil.a_group set name_group = %s,active = %s, useredit = %s,dateedit = now(), id_level_group= %s where id_group = %s',params)
			if type == '1':		
				params = [
					request.json['role_id_group'],
					request.json['role_name_group'],
					getUserName(),
					getUserName(),
					request.json['role_active'],
					'0',
					request.json['role_scope']
					] 
				print(params)	
				c.execute('insert into taswil.a_group select %s , %s , %s , %s ,now() , now() , %s , %s,%s ',params)
				
		paramError = "Save data success"
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
		
		
	conn.commit()
	conn.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )
	

###################
#### ROLE MENU ####
###################

@mod.route('/role_menu')
@check_session
def role_menu_index():	
	con  = connect_db()
	cur = con.cursor()
	cur.execute("SELECT ID_GROUP,NAME_GROUP FROM taswil.a_group where id_group <> '1mfR' and isdelete<>'1'")
	eHTML = " <select id='menu_role_id_group' class='form-control' >"
	eHTML = eHTML + "<option value="">--Select one--</option>"
	#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]	
	for  es in cur.fetchall():
		eHTML = eHTML + "<option value="+str(es[0])+">"+str(es[1])+"</option>"
	eHTML = eHTML + " </select>"
	cur.close()
	con.close()
	
	return jsonify(
        data=render_template('role_menu.html',role_menu_group=Markup(eHTML)),        
        header='ROLE MENU'
    )

def role_menu_data_child(id_grup,parent_id,id):
	con  = connect_db()
	cur = con.cursor() 
	eHTML = ''
	#print(username[0].get('id'))
	cur.execute("SELECT *,COALESCE (COUNTCHILD,0) COUNTCHILD1 FROM taswil.a_menu A LEFT JOIN taswil.a_group_MENU B ON A.ID_MENU = B.ID_MENU AND B.id_group = %s LEFT JOIN (SELECT PARENT_ID,COALESCE (COUNT(1),0) COUNTCHILD FROM taswil.a_menu where active = 0 GROUP BY PARENT_ID ) HAVECHILD ON A.ID_MENU = HAVECHILD.PARENT_ID WHERE ACTIVE = '0' AND A.PARENT_ID = %s order by a.sort",[id_grup,parent_id])	
	for  es in cur.fetchall():		
		check = ''	
		checkAdd = ''
		checkUpdate = ''	
		checkDelete = ''
		checkApprove = ''
		if  noneToStringNull(es[7]) != '':
			check = 'checked'
		if  noneToStringNull(es[9]) != 'False' and noneToStringNull(es[9]) != '':			
			checkAdd = 'checked'
		if  noneToStringNull(es[10]) != 'False'  and noneToStringNull(es[10]) != '':
			checkUpdate = 'checked'
		if  noneToStringNull(es[11]) != 'False'  and noneToStringNull(es[11]) != '':
			checkDelete = 'checked'
		if  noneToStringNull(es[12]) != 'False'  and noneToStringNull(es[12]) != '':
			checkApprove = 'checked'
		idnode = id+'-'+str(es[0])		
		if es[15] > 0:			
			eHTML = eHTML + '<li><i class="fa fa-minus"></i> <label> <input id="node'+idnode+'" class="parentTreeview1" '+check+'  data-id="'+str(es[0])+'" type="checkbox"> '+str(es[1])+'</label>'
			eHTML = eHTML + '<ul>'
			eHTML = eHTML + role_menu_data_child(id_grup,es[0],idnode)
			eHTML = eHTML + '</ul></li>'
		else:
			eHTML = eHTML + '<li class="noparentTreeview1">'
			#eHTML = eHTML + '<table><tr>'
			#eHTML = eHTML + '<td width="400px"><label> <input class="hummingbirdNoParent" id="node'+idnode+'" '+check+' data-id="'+str(es[0])+'"  type="checkbox"> '+str(es[1])+'</label></td>'
			eHTML = eHTML + '<label style="width:400px"> <input class="hummingbirdNoParent" id="node'+idnode+'" '+check+' data-id="'+str(es[0])+'"  type="checkbox"> '+str(es[1])+'</label>'
			
			
			
			eHTML = eHTML + '&nbsp;  &nbsp; <input  '+checkAdd+'   type="checkbox">Add'
			eHTML = eHTML + '&nbsp;  &nbsp; <input  '+checkUpdate+'   type="checkbox">Update'
			eHTML = eHTML + '&nbsp;  &nbsp; <input  '+checkDelete+'   type="checkbox">Delete'
			eHTML = eHTML + '&nbsp;  &nbsp;  <input  '+checkApprove+'   type="checkbox">Approve '
			#eHTML = eHTML + '<td width="100px"> <input  '+checkAdd+'   type="checkbox">Add</td>'
			#eHTML = eHTML + '<td width="100px"><input  '+checkUpdate+'   type="checkbox">Update</td>'
			#eHTML = eHTML + '<td width="100px"> <input  '+checkDelete+'   type="checkbox">Delete</td>'
			#eHTML = eHTML + '<td width="100px"> <input  '+checkApprove+'   type="checkbox">Approve </td>'
			#eHTML = eHTML + '</tr></table>'
			eHTML = eHTML + '</li>'		
	cur.close()
	con.close()
	return eHTML	

@mod.route('/role_menu/data')
@check_session
def role_menu_data():	
	id_group = request.args.get('id_group')
	ehtml = ' <ul id="treeview1" class="hummingbird-base">'
	ehtml = ehtml + role_menu_data_child(id_group,0,'')
	ehtml = ehtml + '</ul>'
	return jsonify(
        data=Markup(ehtml)        
    )

def inserttree(id_group,id_menu):		
	conn = connect_db()
	c = conn.cursor()
	try:				
		parent_id = getOneValue('taswil.a_menu','parent_id',"id_menu = "+str(id_menu))
		jmldata1 = getCountTable("select count(1) count1 from taswil.a_MENU  where id_menu = "+str(parent_id))
		#print("parent_id "+str(parent_id)+",jmldata "+str(jmldata1))
		if jmldata1 > 0 :
			jmldata2 = getCountTable("select count(1) count1 from taswil.a_group_menu  where id_menu = "+str(parent_id)+" and id_group='"+id_group+"'")
			if jmldata2 == 0:			
				#print("insert  "+str(id_group)+","+str(parent_id))
				c.execute("insert into taswil.a_group_MENU select '"+str(id_group)+"',"+str(parent_id)+",false,false,false,false")
				#print("---------------")
				conn.commit()
				inserttree(id_group,parent_id)
			
		
	except Error  as e:		
		print(e)
	
	c.close()
	conn.close()	
	
	

@mod.route('/role_menu/submit', methods = ['POST'])
@check_session
def role_menu_submit():	
	paramResult = True
	conn = connect_db()
	c = conn.cursor()
	listcheck = request.json['menu_role_data']	
	#listcheck = request.form['menu_role_data'];	
#	print(listcheck)
	#aaaa = ""
	try:				
		c.execute('delete from taswil.a_group_MENU where id_group = %s',[request.json['menu_role_id_group']])
		if len(listcheck) > 0:
			for i in range(len(listcheck)):
				#print(request.json['menu_role_id_group']+","+str(listcheck[i]['data_id']))
				c.execute("insert into taswil.a_group_MENU select '"+request.json['menu_role_id_group']+"','"+str(listcheck[i]['data_id'])+"',"+str(listcheck[i]['add'])+","+str(listcheck[i]['update'])+","+str(listcheck[i]['delete'])+","+str(listcheck[i]['approve'])+"")
				conn.commit()
				inserttree(request.json['menu_role_id_group'],str(listcheck[i]['data_id']))
		
		paramError = "Save data success"
		#paramError = aaaa
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
	
	c.close()
	conn.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )




##############
#### USER ####
##############


@mod.route('/user')
@check_session
def user_index():	
	return jsonify(
        data=render_template('user.html'),        
        header='USER'
    )

@mod.route('/user/form')
@check_session
def user_form():	
	con  = connect_db()
	#res
	#return render_template('userprofile.html',header_menu='USER PROFILE')
	
	type = request.args.get('type')
	a_user_username = ''
	a_user_password = ''
	a_user_email = ''
	a_user_active = ''
	a_user_disabled = ''
	a_user_group_id = ''
	a_user_id_wilayah = ''
	typechar = 'Tambah Pengguna'
	
	session['type'] = type
	#print("Level group : ",session['id_level_group'])

	id_level_group = session['id_level_group']
	
	gr = con.cursor()
	gr.execute("SELECT a.id_group, a.name_group,a.id_level_group,b.length_id_wilayah FROM a_group a, a_level_group b WHERE a.id_level_group=b.id_level and a.id_level_group >= %s and active=0 and isdelete <> '1' and id_group!='1mfR'",[id_level_group])
	all_option_group = gr.fetchall()
	htmlGroupOptions = '<option value="" selected disabled>--Pilih Group--</option>'
	# print(all_option_group)
	
	if type == '2':
		typechar = 'Edit Pengguna'
		
		htmlGroupOptions = '<option value="" disabled>--Pilih Group--</option>'
		id = request.args.get('id')
		
		cur = con.cursor() 		
		cur.execute("SELECT  A.*,B.NAME_GROUP FROM TASWIL.A_USER A LEFT JOIN taswil.a_group B ON A.ID_GROUP = B.ID_GROUP  WHERE A.isdelete = %s and A.id_user = %s",['0',id])
		a_user_disabled = 'disabled'
		#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
		for es in cur.fetchall():		
			id = es[0]		
			a_user_username = noneToStringNull(str(es[1]))		
			a_user_password = decodeBase64(noneToStringNull(str(es[2])))	
			a_user_group_id = noneToStringNull(str(es[4]))	
			a_user_active = noneToStringNull(str(es[5]))	
			a_user_email = noneToStringNull(str(es[12]))
			a_user_id_wilayah = noneToStringNull(str(es[14]))		
					
								
		cur.close()
		con.close()
		session['p1'] = id
		print('4')
	for r in all_option_group:
		selected = ''
		if(a_user_group_id == r[0]):
			selected = 'selected'
		htmlGroupOptions += '<option id="os-'+ noneToStringNull(r[0]) +'" value="'+ noneToStringNull(r[0]) +'" length-id="'+ noneToStringNull(r[3]) +'" '+selected+'>'+ noneToStringNull(r[1])+'</option>'

	return jsonify(
        data=render_template('user_form.html',
						a_user_username = a_user_username,
						a_user_password = a_user_password,
						a_user_group_id = a_user_group_id,
			  			a_user_email = a_user_email,  
			  			a_user_active = a_user_active,
						a_user_id_wilayah=a_user_id_wilayah, 
				   		type=typechar,
				   		a_user_disabled=a_user_disabled,
				   		a_option_group=Markup(htmlGroupOptions)
						)
    	)

@mod.route('/user/data')
@check_session
def user_data():		
	con  = connect_db()
	cur = con.cursor() 
	#print(username[0].get('id'))
	#cur.execute('SELECT * FROM taswil.a_group ')
	filterIdWil = noneToStringNull(session['id_wilayah'])
	filterQueryCond = ""
	if filterIdWil!="": 
		filterQueryCond += " and id_wilayah LIKE '"+filterIdWil+"%' "

	cur.execute(convertSQLDataTable("SELECT id_user,username,fullname,name_group, CASE WHEN A.ACTIVE = 0 THEN 'ACTIVE' ELSE 'NO' END ACTIVE FROM TASWIL.a_user a join taswil.a_group b on a.id_group = b.id_group where a.isdelete<>'1' and a.id_group <> '1mfR'" +filterQueryCond))
	#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	es = [dict(username=row[1],fullname=row[2],role=row[3],active=row[4],btn='<div id="dt-buttons" class="dt-buttons"><a class="dt-button buttons-copy buttons-html5 btnEditForm" dataid="'+(row[0])+'" tabindex="0"  ><span>Edit</span></a><a class="dt-button buttons-copy buttons-html5 btnDeleteForm" dataid="'+(row[0])+'" tabindex="0" href="#" data-toggle="modal" data-target="#top-modal"><span>Delete</span></a></div>') for row in cur.fetchall()]
	cur.close()
	con.close()
	
	#print(list)
	#print(es)
	jmldata = getCountTable("SELECT count(1) FROM TASWIL.a_user a join taswil.a_group b on a.id_group = b.id_group where 1=1 and a.isdelete<>'1'" +filterQueryCond)
	return jsonify(
		draw =  int(request.args.get('draw')), recordsTotal= jmldata , recordsFiltered = jmldata,
        data=es
    )

@mod.route('/user/crud', methods = ['POST', 'DELETE'])
@check_session
def user_crud():		
	paramResult = True
	paramError = ''
	
	type = session['type']
	
	#asdasd111 = request.form['userprofile_user']
	
	
	conn = connect_db()
	c = conn.cursor()
	try:
		if 'type' in request.json and request.json['type'] == 3:		
			
			c.execute('update taswil.a_user set isdelete= %s , useredit = %s,dateedit = now() where id_user = %s',['1',getUserName(),request.json['id']])
			
		else:		
			if request.json['user_email'] == '' or request.json['user_username'] == '' or request.json['user_password'] == '' or request.json['user_group_id'] == '':
				return jsonify(
					result = False,
					error = 'Input Mandatory'
				)

			if type == '2':
				# bDate = 'null'
				# if request.json['user_bdate'] != '':
				# 	bDate = request.json['user_bdate']
				p1 = session['p1']
				c.execute('UPDATE taswil.a_user SET password= %s,  id_group=%s, active=%s,  useredit=%s, dateedit=now(),    email=%s where id_user = %s',[encodeBase64(request.json['user_password']),request.json['user_group_id'],request.json['user_active'],getUserName(),request.json['user_email'],p1])
				
			if type == '1':		
#id_user, username, password, fullname, id_group, active, userinput, useredit, dateinput, dateedit, isdelete, gender, birth_date, birth_place, mobile, email, address)		
				
				# bDate = 'null'
				# if request.json['user_bdate'] != '':
				# 	bDate = request.json['user_bdate']
				# print(request.json)
				if(isUsernameUsed(request.json['user_username']) == False):
					id_wilayah = None
					if "user_id_wilayah" in request.get_json():
						id_wilayah = request.json["user_id_wilayah"]

					data = [
						randomCharacter(50),
						request.json['user_username'],
						encodeBase64(request.json['user_password']),
						request.json['user_group_id'],
						id_wilayah,
						request.json['user_email'],
						request.json['user_active'],
						session["generated_fullname"], 
						getUserName(),
						getUserName()
						]
					c.execute("insert into TASWIL.a_user (id_user,username,password,id_group,id_wilayah,email,active,fullname,userinput,useredit,dateinput,dateedit,nm_kepala_desa,nm_kepala_camat) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),'','')",data )
				else :
					return jsonify(
						result = False,
						error = "Username telah digunakan"
					)
				
		paramError = "Berhasil menyimpan data"
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
		
		
	conn.commit()
	conn.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )
	



###################
#### USER DESA ####
###################

@mod.route('/user_desa')
@check_session
def user_desa_index():	
	
	
	return jsonify(
        data=render_template('user_desa.html'),        
        header='MAPPING USER DESA'
    )

def user_desa_data_child(id_desa):
	con  = connect_db()
	cur = con.cursor() 
	eHTML = ''
	#print(username[0].get('id'))
	cur.execute(" SELECT a.id_user,USERNAME,FULLNAME,COALESCE(b.id_user,'') id FROM TASWIL.A_USER a left join taswil.a_user_desa b on a.id_user = b.id_user  WHERE a.TIPE = 1 AND a.ID_USER not IN (SELECT ID_USER FROM TASWIL.A_USER_DESA) AND a.ID_USER not IN (SELECT ID_USER FROM TASWIL.A_USER_moderATOR) 	AND a.ACTIVE = 0 AND a.ISDELETE = 0 and a.id_user <>'IuPx5Wuz1TjHvWZj3bJdzdhLz7QP0v8GksnfxziP5X6gXavVAk' union SELECT a.id_user,USERNAME,FULLNAME,COALESCE(b.id_user,'') id  FROM TASWIL.A_USER a 	join taswil.a_user_desa b on a.id_user = b.id_user WHERE a.TIPE = 1 AND b.id_desa = '"+id_desa+"'AND a.ACTIVE = 0 AND a.ISDELETE = 0 and a.id_user <>'IuPx5Wuz1TjHvWZj3bJdzdhLz7QP0v8GksnfxziP5X6gXavVAk'")	
	for  es in cur.fetchall():
		check = ''
		if  noneToStringNull(es[3]) != '':
			check = 'checked'
		eHTML = eHTML + '<tr>'		
		eHTML = eHTML + '<td> <input class="noparentTreeview1" '+check+' data-id="'+str(es[0])+'"  type="checkbox"></td>'
		eHTML = eHTML + '<td>'+str(es[1])+'</td>'
		eHTML = eHTML + '<td>'+str(es[2])+'</td>'
		eHTML = eHTML + '</tr>'	
		
	cur.close()
	con.close()
	return eHTML	

@mod.route('/user_desa/data')
@check_session
def user_desa_data():	
	id_desa = request.args.get('id_desa')
	ehtml = ' <table  class="table"><thead><tr><th></th><th  scope="col">Username</th><th  scope="col">Full Name</th></tr></thead>'
	ehtml = ehtml + user_desa_data_child(id_desa)
	ehtml = ehtml + '</table>'
	return jsonify(
        data=Markup(ehtml)        
    )

	
	

@mod.route('/user_desa/submit', methods = ['POST'])
@check_session
def user_desa_submit():	
	paramResult = True
	conn = connect_db()
	c = conn.cursor()
	listcheck = request.json['user_desa_data']	
	#listcheck = request.form['menu_role_data'];	
#	print(listcheck)
	#aaaa = ""
	try:				
		c.execute('delete from taswil.a_user_desa where id_desa = %s',[request.json['user_desa_id_user']])
		if len(listcheck) > 0:
			for i in range(len(listcheck)):
				#print(request.json['menu_role_id_group']+","+str(listcheck[i]['data_id']))
				c.execute("insert into taswil.a_user_desa select '"+request.json['user_desa_id_user']+"','"+str(listcheck[i]['data_id'])+"'")
				
		conn.commit()		
		paramError = "Save data success"
		#paramError = aaaa
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
	
	c.close()
	conn.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )




###################
#### USER MODERATOR ####
###################

@mod.route('/user_moderator')
@check_session
def user_moderator_index():	
	
	
	return jsonify(
        data=render_template('user_moderator.html'),        
        header='MAPPING USER MODERATOR'
    )

def user_moderator_data_child(id_kabkota):
	con  = connect_db()
	cur = con.cursor() 
	eHTML = ''
	#print(username[0].get('id'))
	cur.execute(" SELECT a.id_user,USERNAME,FULLNAME,COALESCE(b.id_user,'') id FROM TASWIL.A_USER a left join taswil.a_user_moderator b on a.id_user = b.id_user  WHERE a.TIPE = 2 AND a.ID_USER not IN (SELECT ID_USER FROM TASWIL.A_USER_DESA) AND a.ID_USER not IN (SELECT ID_USER FROM TASWIL.A_USER_moderATOR) 	AND a.ACTIVE = 0 AND a.ISDELETE = 0 and a.id_user <>'IuPx5Wuz1TjHvWZj3bJdzdhLz7QP0v8GksnfxziP5X6gXavVAk' union SELECT a.id_user,USERNAME,FULLNAME,COALESCE(b.id_user,'') id  FROM TASWIL.A_USER a 	join taswil.a_user_moderator b on a.id_user = b.id_user WHERE a.TIPE = 2 AND b.id_kabkota = '"+id_kabkota+"'AND a.ACTIVE = 0 AND a.ISDELETE = 0 and a.id_user <>'IuPx5Wuz1TjHvWZj3bJdzdhLz7QP0v8GksnfxziP5X6gXavVAk'")	
	for  es in cur.fetchall():
		check = ''
		if  noneToStringNull(es[3]) != '':
			check = 'checked'
		eHTML = eHTML + '<tr>'		
		eHTML = eHTML + '<td> <input class="noparentTreeview1" '+check+' data-id="'+str(es[0])+'"  type="checkbox"></td>'
		eHTML = eHTML + '<td>'+str(es[1])+'</td>'
		eHTML = eHTML + '<td>'+str(es[2])+'</td>'
		eHTML = eHTML + '</tr>'	
		
	cur.close()
	con.close()
	return eHTML	

@mod.route('/user_moderator/data')
@check_session
def user_moderator_data():	
	id_desa = request.args.get('id_desa')
	ehtml = ' <table  class="table"><thead><tr><th></th><th  scope="col">Username</th><th  scope="col">Full Name</th></tr></thead>'
	ehtml = ehtml + user_moderator_data_child(id_desa)
	ehtml = ehtml + '</table>'
	return jsonify(
        data=Markup(ehtml)        
    )


@mod.route('/user_moderator/submit', methods = ['POST'])
@check_session
def user_moderator_submit():	
	paramResult = True
	conn = connect_db()
	c = conn.cursor()
	listcheck = request.json['user_moderator_data']	
	#listcheck = request.form['menu_role_data'];	
#	print(listcheck) 
	#aaaa = ""
	try:				
		c.execute('delete from taswil.a_user_moderator where id_kabkota = %s',[request.json['user_moderator_id_user']])
		if len(listcheck) > 0:
			for i in range(len(listcheck)):
				#print(request.json['menu_role_id_group']+","+str(listcheck[i]['data_id']))
				c.execute("insert into taswil.a_user_moderator select '"+request.json['user_moderator_id_user']+"','"+str(listcheck[i]['data_id'])+"'")
				
		conn.commit()		
		paramError = "Save data success"
		#paramError = aaaa
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
	
	c.close()
	conn.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )
 
@mod.route('/generateUsername')
# @check_session
def generate_username_by_id_wilayah():
	id_group = request.args.get("id_group")
	id_wilayah = noneToStringNull(request.args.get("id_wilayah"))
	 
	conn = connect_db()
	c = conn.cursor() 
	c.execute("SELECT b.length_id_wilayah FROM taswil.a_group a, taswil.a_level_group b where id_group = %s and isdelete <> '1' and a.id_level_group=b.id_level",[noneToStringNull(id_group)])

	exist = [dict(len=row[0]) for row in c.fetchall()]
	 
	if(len(exist) <1):
		return jsonify(error=True, err_msg="Harap pilih id group" )
	 
	if exist[0]['len'] != 0 :
		#print(len(id_wilayah),exist[0]['len']
		#if(len(id_wilayah) != exist[0]['len'] or id_wilayah.isnumeric() != True ):
		if(len(id_wilayah) != exist[0]['len'] ):
			return jsonify(error=True, err_msg="Id wilayah tidak cocok dengan level group" )
		
		len_id = exist[0]['len']
		table_name = 'taswil.m_provinsi'
		table_col_id = 'id_provinsi'
		username = id_wilayah[0:5] +'.'
		if(len_id == 5):
			table_name = 'taswil.m_kabkota'
			table_col_id = 'id_kabkota'
		elif(len_id == 8):
			table_name = 'taswil.m_kecamatan'
			table_col_id = 'id_kecamatan'
			username += "kec."
		elif (len_id== 13):
			table_name = 'taswil.m_desa'
			table_col_id = 'id_desa'
			print(id_wilayah[9])
			if id_wilayah[9] == "1":
				username += "kl."
			else:
				username += "ds."
		 
		c.execute(f'SELECT nama from {table_name} where {table_col_id} = %s',[id_wilayah])
		full_name =c.fetchone()[0]
	
		username += full_name.replace(" ", "_").lower()

		c.execute('SELECT * FROM a_user WHERE id_wilayah = %s',[id_wilayah])
		wil_ke = len(c.fetchall()) 
		if wil_ke != 0:
			username += noneToStringNull(wil_ke)
			full_name +' '+noneToStringNull(wil_ke)

		session['generated_fullname'] = full_name
		# print(username,wil_ke)
	else :
		# username ="".join(generate(2))
		isUnique = False
		while isUnique ==False:
			arr_generated = [x.capitalize() for x in generate(2)]
			full_name = " ".join(arr_generated)
			username = "".join(arr_generated)
		
			if(isUsernameUsed(username) == False):
				isUnique = True  
		
		session['generated_fullname'] = full_name 
	
	c.close()
	conn.close()
	return jsonify(username=username)

def isUsernameUsed(username):
	conn = connect_db()
	c = conn.cursor() 
	c.execute("SELECT username FROM taswil.a_user WHERE username = %s", [username])
	data = c.fetchall()
	c.close()
	conn.close()
	if(len(data) == 0):
		return False
	else : 
		return True 