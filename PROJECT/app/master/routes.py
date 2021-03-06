from flask import Blueprint, render_template,jsonify,request,g,session
from app import connect_db,validJWT,noneToStringNull,decodeBase64,encodeBase64,getCountTable,convertSQLDataTable,randomCharacter,getUserName,check_session
#from sqlite3 import Error
from psycopg2 import Error

from markupsafe import Markup
import json

mod = Blueprint('master', __name__, template_folder='templates')


######################
#### DROPDOWNLIST ####
######################


@mod.route('/desa/dropdownlist')
@check_session
def desa_dropdownlist():
	strQuery = ""
	type = request.args.get('type')
	search = noneToStringNull(request.args.get('search')) 
	id_provinsi = noneToStringNull(request.args.get('id_provinsi'))
	id_kabkota = noneToStringNull(request.args.get('id_kabkota'))
	id_kecamatan = noneToStringNull(request.args.get('id_kecamatan'))
	if type == "1":
		strQuery = "select a.id_desa,(d.nama||' - '||c.nama||' - '||b.nama||' - '||a.nama) ket from taswil.m_desa a join taswil.m_kecamatan b on a.id_kecamatan = b.id_kecamatan join taswil.m_kabkota c on b.id_kabkota = c.id_kabkota join taswil.m_provinsi d on c.id_provinsi = d.id_provinsi 	where lower(a.id_desa) like lower('%"+search+"%') or lower(d.nama||' - '||c.nama||' - '||b.nama||' - '||a.nama) like lower('%"+search+"%')"
	elif type =="2":
		filterWil = noneToStringNull(session['id_wilayah'])
		deactivateFilter = noneToStringNull(request.args.get("deactivatefilter"))

		strQuery = "select a.id_desa,a.nama,b.nama as nama_kec from taswil.m_desa a join taswil.m_kecamatan b on a.id_kecamatan = b.id_kecamatan join taswil.m_kabkota c on b.id_kabkota = c.id_kabkota join taswil.m_provinsi d on c.id_provinsi = d.id_provinsi where lower(a.nama) like lower('%"+search+"%')"
		if id_provinsi !="":
			strQuery += " and d.id_provinsi='"+id_provinsi+"'"
		
		if id_kabkota != "":
			strQuery += " and c.id_kabkota='"+id_kabkota+"'"

		if id_kecamatan != "":
			strQuery += " and b.id_kecamatan='"+id_kecamatan+"'"
		
		if len(deactivateFilter) ==0:
			if(filterWil != ""):
				# print("null")
				strQuery+= " and a.id_desa like '"+filterWil[:13]+"%'"

		strQuery += " ORDER BY a.nama asc"

	con  = connect_db()
	cur = con.cursor() 
	#print(username[0].get('id'))
	#cur.execute('SELECT * FROM taswil.a_group ')
	cur.execute(strQuery)
	#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	es = [dict(id=row[0],name=row[1],parent_name=row[2]) for row in cur.fetchall()]
	cur.close()
	con.close()
	
	return jsonify(		
        data=es
    )


@mod.route('/kecamatan/dropdownlist')
@check_session
def kecamatan_dropdownlist():
	strQuery = ""
	type = request.args.get('type')
	search = noneToStringNull(request.args.get('search')) 
	id_provinsi = noneToStringNull(request.args.get('id_provinsi'))
	id_kabkota = noneToStringNull(request.args.get('id_kabkota'))
	if type == "1":
		strQuery = "select b.id_kecamatan,(d.nama||' - '||c.nama||' - '||b.nama) ket from taswil.m_kecamatan b join taswil.m_kabkota c on b.id_kabkota = c.id_kabkota join taswil.m_provinsi d on c.id_provinsi = d.id_provinsi 	where lower(b.id_kecamatan) like lower('%"+search+"%') or lower(d.nama||' - '||c.nama||' - '||b.nama) like lower('%"+search+"%')"
	elif type =="2":
		filterWil = noneToStringNull(session['id_wilayah'])
		deactivateFilter = noneToStringNull(request.args.get("deactivatefilter"))

		strQuery = "select b.id_kecamatan,b.nama from taswil.m_kecamatan b join taswil.m_kabkota c on b.id_kabkota = c.id_kabkota join taswil.m_provinsi d on c.id_provinsi = d.id_provinsi where lower(b.nama) like lower('%"+search+"%') "
		if id_provinsi !="":
			strQuery += " and d.id_provinsi='"+id_provinsi+"'"
		
		if id_kabkota != "":
			strQuery += " and c.id_kabkota='"+id_kabkota+"'"
	
		if len(deactivateFilter) ==0:
			if(filterWil != ""):
			# print("null")
				strQuery+= " and b.id_kecamatan like '"+filterWil[:8]+"%'"

		strQuery += " ORDER BY b.nama asc"


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


@mod.route('/kabkota/dropdownlist')
@check_session
def kabkota_dropdownlist():
	strQuery = ""
	type = request.args.get('type')
	search = noneToStringNull(request.args.get('search')) 
	id_provinsi = noneToStringNull(request.args.get('id_provinsi'))
	if type == "1":
		strQuery = "select c.id_kabkota,(d.nama||' - '||c.nama) ket from taswil.m_kabkota c join taswil.m_provinsi d on c.id_provinsi = d.id_provinsi 	where lower(c.id_kabkota) like lower('%"+search+"%') or lower(d.nama||' - '||c.nama) like lower('%"+search+"%')"
	elif type=="2":
		filterWil = noneToStringNull(session['id_wilayah'])
		strQuery = "select c.id_kabkota,c.nama from taswil.m_kabkota c join taswil.m_provinsi d on c.id_provinsi = d.id_provinsi where lower(c.nama) like lower('%"+search+"%')"
		if id_provinsi != "":
			strQuery += " and c.id_provinsi='"+id_provinsi+"'"

		if(filterWil != ""):
			# print("null")
			strQuery+= " and id_kabkota like '"+filterWil[:5]+"%'"

		strQuery += " ORDER BY c.nama asc"

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

@mod.route('/provinsi/dropdownlist')
@check_session
def provinsi_dropdownlist():
	strQuery = "" 
	type = request.args.get('type')
	search = noneToStringNull(request.args.get('search')) 
	if type == "1":
		strQuery = "SELECT id_provinsi,nama FROM taswil.m_provinsi WHERE lower(nama) like lower('%"+search+"%') "
	elif type=="2":
		filterWil = noneToStringNull(session['id_wilayah'])
		strQuery = "SELECT id_provinsi,nama FROM taswil.m_provinsi WHERE lower(nama) like lower('%"+search+"%') " 
		if(filterWil != ""):
			# print("null")
			strQuery+= " and id_provinsi like '"+filterWil[:2]+"%'"
		
		strQuery +=" ORDER BY nama asc"
		# print(type(filterWil),"ahaha")

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


@mod.route('/petadesa')
@check_session
def petadesa_index():
	con  = connect_db()
	cur = con.cursor() 

	allowedType = ['geojson']

	id_desa = noneToStringNull(request.args.get("id_desa"))
	resultType = noneToStringNull(request.args.get("type")).lower()
	result =[]
	if((resultType in allowedType) == False):
		resultType = "geojson"
		# print("tidak ada")

	strQuery = "SELECT id_klaim_batas_desa, ST_ASGEOJSON(geom) as geom,to_char(modifiedat, 'YYYY-MM-DD HH24:MI:SS') as lastupdate,ismainmap,b.nama FROM t_klaim_batas_desa a, m_desa b WHERE a.id_desa=b.id_desa and a.id_desa=%s and ismainmap=true order by modifiedat"
	if(resultType == 'kml'):
		strQuery = "SELECT id_klaim_batas_desa, ST_ASGEOJSON(geom) as geom,to_char(modifiedat, 'YYYY-MM-DD HH24:MI:SS') as lastupdate, ismainmap,b.nama FROM t_klaim_batas_desa a, m_desa b WHERE a.id_desa=b.id_desa and id_desa=%s and ismainmap=true order by modifiedat"

	# print(resultType in allowedType,resultType)
	try:
		cur.execute(strQuery,[id_desa])	
		dt =cur.fetchall()
		if(len(dt) == 0 ):
			strQuery = strQuery.replace('and ismainmap=true', '')
			# print(strQuery)
			cur.execute(strQuery,[id_desa])	
			dt =cur.fetchall()

		
		if(len(dt) >0):
			row =dt[0]
			result = dict(id=row[0],map=row[1],lastupdate=row[2],ismainmap=row[3],nama=row[4],type=resultType)

		
	except Error as er:
		result =[]

	
	con.close()
	
	return jsonify(data=result,id_desa=id_desa)


@mod.route('/petadesa1')
# @check_session
def petadesa1_index():
	con  = connect_db()
	cur = con.cursor() 

	allowedType = ['geojson']

	id_desa = noneToStringNull(request.args.get("id_desa"))
	
	cur.execute("select  ST_AsGeoJSON(c.geom) wilayah_desa_asal,ST_AsText(ST_Centroid(c.geom)) center, b.nama ,c.description from taswil.t_klaim_batas_desa a join taswil.m_Desa b on a.id_desa = b.id_Desa join taswil.t_klaim_batas_desa_Detil c on a.id_klaim_batas_desa = c.id_klaim_batas_desa where a.ismainmap = true and a.id_Desa = %s ",[id_desa])
	test1 = []
	i = 0;
	center = ""
	nama = ""
	for  es in cur.fetchall():	
		i = i+1;
		aaa = json.loads(es[0])
		obj = {'type' : 'Feature','id':'A'+str(i),'properties':{'nama':es[2]},'geometry' :aaa }
		test1.append(obj)
		center = es[1]
		nama = es[2]
	cur.close()
	con.close()
	test = {'type': 'FeatureCollection','crs': {'type': 'name','properties': {'name': 'EPSG:4326'}},'features' : test1}
	return jsonify(
       data = test,center = center,nama = nama
    )