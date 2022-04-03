from flask import Blueprint, render_template,jsonify,request,g,session,make_response
from app import connect_db,noneToStringNull,decodeBase64,encodeBase64,getCountTable,convertSQLDataTable,randomCharacter,getUserName,check_session,getMD5,allowed_file,basedir,getOneValue,check_just_session

from datetime import datetime

from werkzeug.utils import secure_filename

import  os

#from sqlite3 import Error
from psycopg2 import Error

from markupsafe import Markup

mod = Blueprint('toponim', __name__, template_folder='templates')

import json

##############
#### dokumen desa  ####
##############


@mod.route('/')
#@check_session
def toponim_index():	
	return render_template('toponim.html')      
       


@mod.route('/test')
#@check_session
def toponim_index1():
	
	
	con  = connect_db()
	cur = con.cursor() 
	#print(username[0].get('id'))
	cur.execute("SELECT id_toponim,namspe,foto1, CASE WHEN geometrytype(geom) = 'POINT'::text THEN 'Titik'::text WHEN geometrytype(geom) = 'LINESTRING'::text THEN 'Garis'::text WHEN geometrytype(geom) = 'POLYGON'::text THEN 'Area'::text ELSE NULL::text END AS jenis_toponim,st_asgeojson(geom) geometry FROM TASWIL.toponim ")
	#es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	test1 = []
	for  es in cur.fetchall():		
		'''
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
		'''
		#aaa = jsonify(es[4])
		aaa = json.loads(es[4])
		obj = {'type' : 'Feature','id':'A'+str(es[0]),'properties':[{ 'id': es[0], 'name' : es[1],'foto1' : es[2],	'tipe_geometri' : es[3]}],'geometry' :aaa }
		test1.append(obj)
	#es = [dict(id_role=row[0]) for row in cur.fetchall()]	
	cur.close()
	con.close()
	#session['id'] = id
	#test = ['type' = 'FeatureCollection','crs' = ['type' = 'name','properties' = ['name' = 'urn:ogc:def:crs:OGC:1.3:CRS84'	] ],'features' = test1]
	#test = {'type': 'FeatureCollection','crs' : [{'type' : 'name','properties' : [{'name' : 'urn:ogc:def:crs:OGC:1.3:CRS84'}]}],'features' : test1}
	test = {'type': 'FeatureCollection','crs': {'type': 'name','properties': {'name': 'EPSG:3857'}},'features' : test1}
	return jsonify(
       test
    )