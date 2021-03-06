from flask import Blueprint, render_template, jsonify, request, g, session, make_response
from app import connect_db, validJWT, noneToStringNull, decodeBase64, encodeBase64, getCountTable, convertSQLDataTable, randomCharacter, getUserName, check_session, getMD5, allowed_file, basedir, getOneValue, check_just_session, allowed_file_zip, getIdUserName, getWilayahById

from datetime import datetime
import time

from werkzeug.utils import secure_filename

import os

# from sqlite3 import Error
from psycopg2 import Error

from markupsafe import Markup
import uuid
import json

mod = Blueprint('transaction_kab', __name__, template_folder='templates')




def hasil(num):
	huruf = ['nol', 'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan', 'sepuluh', 'sebelas']
	if num < 12:
		if num==0:
			temp = ''
		else:
			temp = ' '+huruf[num]
	elif num < 20:
		temp = str(hasil(num-10))+' belas'
	elif num < 100:
		temp = str(hasil(num//10))+' puluh'+str(hasil(num%10))
	elif num < 200:
		temp = ' seratus'+str(hasil(num-100))
	elif num < 1000:
		temp = str(hasil(num//100))+' ratus'+str(hasil(num%100))
	elif num < 2000:
		temp = ' seribu'+str(hasil(num-1000))
	elif num < 1000000:
		temp = str(hasil(num//1000))+' ribu'+str(hasil(num%1000))
	elif num < 1000000000:
		temp = str(hasil(num//1000000))+' juta'+str(hasil(num%1000000))
	elif num < 1000000000000:
		temp = str(hasil(num//1000000000))+' milyar'+str(hasil(num%1000000000))
	elif num < 1000000000000000:
		temp = str(hasil(num//1000000000000))+' trilyun'+str(hasil(num%1000000000000))
	return temp

def terbilang(num):
	if num < 0:
		hasilV = 'minus '+hasil(num)
	else:
		hasilV = hasil(num)
	return hasilV

##################ktitik sumpul######################

@mod.route('/settitiksimpul')
@check_session
def settitiksimpul_index():
    a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
    # print((a_user_id_wilayah))

    return jsonify(data=render_template('set_titik_simpul.html',
                                        a_user_id_wilayah=a_user_id_wilayah),
                   header='Set Titik Simpul')
				   


@mod.route('/settitiksimpul/data')
@check_session
def settitiksimpuldata_index():
    con = connect_db()
    cur = con.cursor()
    # print(username[0].get('id'))
    # cur.execute('SELECT * FROM taswil.a_group ')

    filterIdWil = noneToStringNull(request.args.get("id_wilayah"))
    sesIdWil = noneToStringNull(session['id_wilayah'])
    filterQueryCond = ""
    if filterIdWil != "":
        if(len(filterIdWil) < len(sesIdWil)):
            filterIdWil = sesIdWil

        filterQueryCond += " and b3.id_kabkota LIKE '" + filterIdWil + "%' "
    else:
        filterQueryCond += " and b3.id_kabkota LIKE '" + sesIdWil + "%' "

    cur.execute(
        #convertSQLDataTable(
        #    "select  a.id_desa_bersebelahan, b1.nama desa_asal,b.createdat tanggal_klaim1 ,b12.nama desa_tujuan,c.createdat tanggal_klaim2 ,b.id_klaim_batas_desa,c.id_klaim_batas_desa 	from taswil.t_desa_bersebelahan_2 a join taswil.t_klaim_batas_desa b on a.desa_1 = b.id_desa join taswil.t_klaim_batas_desa c on a.desa_2 = c.id_desa join taswil.m_desa b1 on a.desa_1 = b1.id_Desa 	join taswil.m_desa b12 on a.desa_2 = b12.id_Desa join taswil.m_kecamatan b2 on b1.id_kecamatan = b2.id_kecamatan 	join taswil.m_kabkota b3 on b2.id_kabkota = b3.id_kabkota where a.isrejected = false and b.ismainmap = true and c.ismainmap = true and konfirm_desa_1 = true and konfirm_desa_2 = true "  + filterQueryCond))
		convertSQLDataTable(
            "select  a.id_desa_bersebelahan, b1.nama desa_asal,b.createdat tanggal_klaim1 ,b12.nama desa_tujuan,c.createdat tanggal_klaim2 from taswil.t_desa_bersebelahan_2 a left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa bb where bb.id_desa = a.desa_1 and bb.ismainmap = true order by createdat desc limit 1 ) b on true left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa cc    where cc.id_desa = a.desa_2 and cc.ismainmap = true order by createdat desc limit 1 ) c on true join taswil.m_desa b1 on a.desa_1 = b1.id_Desa 	join taswil.m_desa b12 on a.desa_2 = b12.id_Desa join taswil.m_kecamatan b2 on b1.id_kecamatan = b2.id_kecamatan join taswil.m_kabkota b3 on b2.id_kabkota = b3.id_kabkota where 1=1 and a.isrejected = false and b.ismainmap = true and c.ismainmap = true and konfirm_desa_1 = true and konfirm_desa_2 = true"  + filterQueryCond+" group by a.id_desa_bersebelahan, b1.nama ,b.createdat  ,b12.nama ,c.createdat  "))
   
    es = [
        dict(
            id=row[0],
            desa_asal=row[1],
            tanggal_klaim1=row[2],
            #peta_utama=getlabeStatusPeta(row[2]),
            desa_tujuan=row[3],
            tanggal_klaim2=row[4],
           
            btn='<div id="dt-buttons" class="dt-buttons">' +            
            '<a class="btn btn-info btnEditForm mr-1" dataid="' + (row[0]) + '"  tabindex="0"  onclick="viewData(this)"><span>Set Titik Simpul</span></a> ' +

            '</div>'
        ) for row in cur.fetchall()
    ]
    jmldata = len(es)
    cur.close()
    con.close()

    return jsonify(draw=int(request.args.get('draw')),
                   recordsTotal=jmldata,
                   recordsFiltered=jmldata,
                   data=es)



@mod.route('/settitiksimpul/form')
@check_session
def settitiksimpul_form():
    # res
    # return render_template('userprofile.html',header_menu='USER PROFILE')

	id = request.args.get('id')
	klaim_batas_desa1 = ""
	klaim_batas_desa2 = ""
	con = connect_db()
	cur = con.cursor()
	cur.execute(
		"select a.id_desa_bersebelahan, b1.nama desa_asal ,b12.nama desa_tujuan , b.id_klaim_batas_desa klaim_batas_desa1, c.id_klaim_batas_desa klaim_batas_desa2,a.desa_1,a.desa_2	from taswil.t_desa_bersebelahan_2 a 	join taswil.t_klaim_batas_desa b on a.desa_1 = b.id_desa and b.ismainmap = true 	 	join taswil.t_klaim_batas_desa c on a.desa_2 = c.id_desa and c.ismainmap = true 		join taswil.m_desa b1 on a.desa_1 = b1.id_Desa	join taswil.m_desa b12 on a.desa_2 = b12.id_Desa	where a.id_desa_bersebelahan = %s",
		[id])
	a_role_disabled = 'disabled'
	# es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	for es in cur.fetchall():
		id = es[0]
		desa_asal = noneToStringNull(str(es[1]))
		desa_tujuan = noneToStringNull(str(es[2]))
		klaim_batas_desa1 = (str(es[3]))
		klaim_batas_desa2 = (str(es[4]))
		id_desa_asal = noneToStringNull(str(es[5]))
		id_desa_tujuan = noneToStringNull(str(es[6]))
	cur.close()
	con.close()
	session['p1'] = id
	a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
	return jsonify(data=render_template('set_titik_simpul_form.html',id_wilayah=a_user_id_wilayah,klaimidDesa1=klaim_batas_desa1,klaimidDesa2=klaim_batas_desa2,desa1 = id_desa_asal,desa2=id_desa_tujuan,id_desa_bersebelahan=id))


@mod.route('/settitiksimpul/geojson')
@check_session
def settitiksimpul_geojson():
	id1 = request.args.get('id1')
	id2 = request.args.get('id2')
	
	con  = connect_db()
	cur = con.cursor() 	
	#cur.execute("SELECT id_toponim,namspe,foto1, CASE WHEN geometrytype(geom) = 'POINT'::text THEN 'Titik'::text WHEN geometrytype(geom) = 'LINESTRING'::text THEN 'Garis'::text WHEN geometrytype(geom) = 'POLYGON'::text THEN 'Area'::text ELSE NULL::text END AS jenis_toponim,st_asgeojson(geom) geometry FROM TASWIL.toponim ")
	cur.execute("select  ST_AsGeoJSON(c.geom) wilayah_desa_asal,ST_AsText(ST_Centroid(c.geom)) center, b.nama ,c.description from taswil.t_klaim_batas_desa a join taswil.m_Desa b on a.id_desa = b.id_Desa join taswil.t_klaim_batas_desa_Detil c on a.id_klaim_batas_desa = c.id_klaim_batas_desa where a.ismainmap = true and (a.id_Desa = %s or a.id_Desa = %s)",[id1,id2])
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
	
@mod.route('/settitiksimpul/geojson1')
@check_session
def settitiksimpul_geojson1():
	id1 = request.args.get('id1')
	id2 = request.args.get('id2')
	
	con  = connect_db()
	cur = con.cursor() 	
	cur.execute("select distinct ST_AsGeoJSON(geom) ,no,keterangan,a.id_titikkartometri from TASWIL.t_titikkartometri a	join TASWIL.t_titikkartometri_desa b on a.id_titikkartometri = b.id_titikkartometri	where (b.id_desa = %s or b.id_desa = %s)	and a.issimpul = 2",[id1,id2])
	test1 = []
	i = 0;
	center = ""
	nama = ""
	for  es in cur.fetchall():	
		i = i+1;
		aaa = json.loads(es[0])
		aab = es[1]
		aac = es[2]
		obj = {'type' : 'Feature','id':es[3],'properties':{'no':str(aab),'keterangan':aac},'geometry' :aaa }
		test1.append(obj)
		
	cur.close()
	con.close()
	test = {'type': 'FeatureCollection','crs': {'type': 'name','properties': {'name': 'EPSG:4326'}},'features' : test1}
	return jsonify(
       data = test
    )
	
@mod.route('/settitiksimpul/crud', methods=['POST', 'DELETE'])
@check_session
def settitiksimpul_crud():
	paramResult = True
	paramError = ''
	con  = connect_db()
	cur = con.cursor() 	
	try:
		idd = getMD5()
		params = [
					idd,
					request.json['geom'],
					request.json['no'],
					request.json['keterangan'],
					getUserName(),
					getUserName(),					
					'2'
					,'0'
					,session['p1']
					] 
		
		cur.execute('insert into taswil.t_titikkartometri select %s ,ST_TRANSFORM(ST_GeomFromGeoJSON(%s),4326) , %s , %s ,now()  , now(), %s , %s,%s,%s,%s ',params)
		
		arraydesa = request.json['listdesa']
		for x in arraydesa:
			cur.execute('insert into taswil.t_titikkartometri_desa select %s , %s ',[idd,x])
		paramError = "Save data success"
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
		
		
	con.commit()
	con.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )

	
@mod.route('/settitiksimpul/crude', methods=['POST', 'DELETE'])
@check_session
def settitiksimpul_crude():
	paramResult = True
	paramError = ''
	con  = connect_db()
	cur = con.cursor() 	
	try:
		arraydesa = request.json['listdesa']
		print(arraydesa)
		for x in arraydesa:
			#print(x['datajson'])
			#xx = json.loads(x)
			cur.execute('update taswil.t_titikkartometri set geom =  ST_TRANSFORM(ST_GeomFromGeoJSON(%s),4326) ,dtm_upd = now(),usr_upd = %s where id_titikkartometri = %s ',[x['datajson'],getUserName(),x['id']])
		paramError = "Save data success"
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
		
		
	con.commit()
	con.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )

##################ktitik sumpul######################


##################ktitik kartometri######################

@mod.route('/settitikkartometri')
@check_session
def settitikkartometri_index():
    a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
    # print((a_user_id_wilayah))

    return jsonify(data=render_template('set_titik_kartometri.html',
                                        a_user_id_wilayah=a_user_id_wilayah),
                   header='Set Titik Kartometrik')
				   


@mod.route('/settitikkartometri/data')
@check_session
def settitikkartometridata_index():
    con = connect_db()
    cur = con.cursor()
    # print(username[0].get('id'))
    # cur.execute('SELECT * FROM taswil.a_group ')

    filterIdWil = noneToStringNull(request.args.get("id_wilayah"))
    sesIdWil = noneToStringNull(session['id_wilayah'])
    filterQueryCond = ""
    if filterIdWil != "":
        if(len(filterIdWil) < len(sesIdWil)):
            filterIdWil = sesIdWil

        filterQueryCond += " and b3.id_kabkota LIKE '" + filterIdWil + "%' "
    else:
        filterQueryCond += " and b3.id_kabkota LIKE '" + sesIdWil + "%' "

    cur.execute(convertSQLDataTable(
        "select  a.id_desa_bersebelahan, b1.nama desa_asal,b.createdat tanggal_klaim1 ,b12.nama desa_tujuan,c.createdat tanggal_klaim2 from taswil.t_desa_bersebelahan_2 a left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa bb where bb.id_desa = a.desa_1 and bb.ismainmap = true order by createdat desc limit 1 ) b on true left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa cc    where cc.id_desa = a.desa_2 and cc.ismainmap = true order by createdat desc limit 1 ) c on true join taswil.m_desa b1 on a.desa_1 = b1.id_Desa 	join taswil.m_desa b12 on a.desa_2 = b12.id_Desa join taswil.m_kecamatan b2 on b1.id_kecamatan = b2.id_kecamatan join taswil.m_kabkota b3 on b2.id_kabkota = b3.id_kabkota where 1=1 and a.isrejected = false and b.ismainmap = true and c.ismainmap = true and konfirm_desa_1 = true and konfirm_desa_2 = true"  + filterQueryCond+" group by a.id_desa_bersebelahan, b1.nama ,b.createdat  ,b12.nama ,c.createdat  "))
    # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
    # print( "SELECT id_klaim_batas_desa, a.id_desa,ismainmap,createdby,modifiedby,createdat,modifiedat,b.nama FROM taswil.t_klaim_batas_desa a, m_desa b WHERE a.id_desa=b.id_desa"
    #         + filterQueryCond)

    es = [
        dict(
            id=row[0],
            desa_asal=row[1],
            tanggal_klaim1=row[2],
            #peta_utama=getlabeStatusPeta(row[2]),
            desa_tujuan=row[3],
            tanggal_klaim2=row[4],
           
            btn='<div id="dt-buttons" class="dt-buttons">' +            
            '<a class="btn btn-info btnEditForm mr-1" dataid="' + (row[0]) + '"  tabindex="0"  onclick="viewData(this)"><span>Set Titik Kartometrik</span></a> ' +

            '</div>'
        ) for row in cur.fetchall()
    ]
    jmldata = len(es)
    cur.close()
    con.close()

    return jsonify(draw=int(request.args.get('draw')),
                   recordsTotal=jmldata,
                   recordsFiltered=jmldata,
                   data=es)



@mod.route('/settitikkartometri/form')
@check_session
def settitikkartometri_form():
    # res
    # return render_template('userprofile.html',header_menu='USER PROFILE')

	id = request.args.get('id')
	klaim_batas_desa1 = ""
	klaim_batas_desa2 = ""
	con = connect_db()
	cur = con.cursor()
	cur.execute(
		"select a.id_desa_bersebelahan, b1.nama desa_asal ,b12.nama desa_tujuan , b.id_klaim_batas_desa klaim_batas_desa1, c.id_klaim_batas_desa klaim_batas_desa2,a.desa_1,a.desa_2	from taswil.t_desa_bersebelahan_2 a 	join taswil.t_klaim_batas_desa b on a.desa_1 = b.id_desa and b.ismainmap = true 	join taswil.t_klaim_batas_desa c on a.desa_2 = c.id_desa and c.ismainmap = true	join taswil.m_desa b1 on a.desa_1 = b1.id_Desa	join taswil.m_desa b12 on a.desa_2 = b12.id_Desa	where a.id_desa_bersebelahan = %s",
		[id])
	a_role_disabled = 'disabled'
	# es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	for es in cur.fetchall():
		id = es[0]
		desa_asal = noneToStringNull(str(es[1]))
		desa_tujuan = noneToStringNull(str(es[2]))
		klaim_batas_desa1 = (str(es[3]))
		klaim_batas_desa2 = (str(es[4]))
		id_desa_asal = noneToStringNull(str(es[5]))
		id_desa_tujuan = noneToStringNull(str(es[6]))
	cur.close()
	con.close()
	session['p1'] = id
	return jsonify(data=render_template('set_titik_kartometri_form.html',klaimidDesa1=klaim_batas_desa1,klaimidDesa2=klaim_batas_desa2,desa1 = id_desa_asal,desa2=id_desa_tujuan,id_desa_bersebelahan=id))


@mod.route('/settitikkartometri/geojson')
@check_session
def settitikkartometri_geojson():
	id1 = request.args.get('id1')
	id2 = request.args.get('id2')
	
	con  = connect_db()
	cur = con.cursor() 	
	cur.execute("select  ST_AsGeoJSON(c.geom) wilayah_desa_asal,ST_AsText(ST_Centroid(c.geom)) center, b.nama ,c.description,a.id_Desa from taswil.t_klaim_batas_desa a join taswil.m_Desa b on a.id_desa = b.id_Desa join taswil.t_klaim_batas_desa_Detil c on a.id_klaim_batas_desa = c.id_klaim_batas_desa where a.ismainmap = true and (a.id_Desa = %s or a.id_Desa = %s)",[id1,id2])
	test1 = []
	i = 0;
	center = ""
	nama = ""
	for  es in cur.fetchall():	
		i = i+1;
		aaa = json.loads(es[0])
		#aa1 = json.loads(es[3].replace("'","\""))
		aa1 = es[3].replace("'","\"")
		tipe11 = 2
		if es[4] == id1:
			tipe11 = 1
		obj = {'type' : 'Feature','id':'A'+str(i),'properties':{'nama':es[2],'type':tipe11,'description':aa1},'geometry' :aaa }
		test1.append(obj)
		center = es[1]
		nama = es[2]
	cur.close()
	con.close()
	test = {'type': 'FeatureCollection','crs': {'type': 'name','properties': {'name': 'EPSG:4326'}},'features' : test1}
	return jsonify(
       data = test,center = center,nama = nama
    )
	
@mod.route('/settitikkartometri/geojson1')
@check_session
def settitikkartometri_geojson1():
	id1 = request.args.get('id1')
	id2 = request.args.get('id2')
	
	con  = connect_db()
	cur = con.cursor() 	
	cur.execute("select distinct ST_AsGeoJSON(geom) ,no,keterangan,a.id_titikkartometri,issimpul,urut,ST_X(geom), ST_Y(geom) from TASWIL.t_titikkartometri a	join TASWIL.t_titikkartometri_desa b on a.id_titikkartometri = b.id_titikkartometri	where (b.id_desa = %s or b.id_desa = %s)",[id1,id2])
	test1 = []
	i = 0;
	center = ""
	nama = ""
	for  es in cur.fetchall():	
		i = i+1;
		aaa = json.loads(es[0])
		aab = es[1]
		aac = es[2]
		obj = {'type' : 'Feature','id':es[3],'properties':{'no':str(aab),'keterangan':aac,'simpul':es[4],'cx':es[6],'cy':es[7],'urut':es[5],'index':(i),'geom':aaa},'geometry' :aaa }
		test1.append(obj)
		
	cur.close()
	con.close()
	test = {'type': 'FeatureCollection','crs': {'type': 'name','properties': {'name': 'EPSG:4326'}},'features' : test1}
	return jsonify(
       data = test
    )
	
@mod.route('/settitikkartometri/crud', methods=['POST', 'DELETE'])
@check_session
def settitikkartometri_crud():
	paramResult = True
	paramError = ''
	con  = connect_db()
	cur = con.cursor() 	
	try:
		idd = getMD5()
		params = [
					idd,
					request.json['geom'],
					request.json['no'],
					request.json['keterangan'],
					getUserName(),
					getUserName(),					
					'1'
					,request.json['urut']
					,session['p1']
					] 
		
		cur.execute('insert into taswil.t_titikkartometri select %s ,ST_TRANSFORM(ST_GeomFromGeoJSON(%s),4326) , %s , %s ,now()  , now(), %s , %s,%s,%s,%s ',params)
		
		arraydesa = request.json['listdesa']
		for x in arraydesa:
			cur.execute('insert into taswil.t_titikkartometri_desa select %s , %s ',[idd,x])
		paramError = "Save data success"
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
		
		
	con.commit()
	con.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )

	
@mod.route('/settitikkartometri/crude', methods=['POST', 'DELETE'])
@check_session
def settitikkartometri_crude():
	paramResult = True
	paramError = ''
	con  = connect_db()
	cur = con.cursor() 	
	try:
		arraydesa = request.json['listdesa']
		print(arraydesa)
		for x in arraydesa:
			#print(x['datajson'])
			#xx = json.loads(x)
			cur.execute('update taswil.t_titikkartometri set geom =  ST_TRANSFORM(ST_GeomFromGeoJSON(%s),4326),dtm_upd = now(),usr_upd = %s where id_titikkartometri = %s ',[x['datajson'],getUserName(),x['id']])
		paramError = "Save data success"
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
		
		
	con.commit()
	con.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )
	
##################ktitik kartometri######################



##################ksub segmen######################

@mod.route('/setsubsegmen')
@check_session
def setsubsegmen_index():
    a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
    # print((a_user_id_wilayah))

    return jsonify(data=render_template('set_sub_segmen.html',
                                        a_user_id_wilayah=a_user_id_wilayah),
                   header='Set Sub Segmen')
				   


@mod.route('/setsubsegmen/data')
@check_session
def setsubsegmendata_index():
    con = connect_db()
    cur = con.cursor()
    # print(username[0].get('id'))
    # cur.execute('SELECT * FROM taswil.a_group ')

    filterIdWil = noneToStringNull(request.args.get("id_wilayah"))
    sesIdWil = noneToStringNull(session['id_wilayah'])
    filterQueryCond = ""
    if filterIdWil != "":
        if(len(filterIdWil) < len(sesIdWil)):
            filterIdWil = sesIdWil

        filterQueryCond += " and b3.id_kabkota LIKE '" + filterIdWil + "%' "
    else:
        filterQueryCond += " and b3.id_kabkota LIKE '" + sesIdWil + "%' "

    cur.execute(
        convertSQLDataTable(
            "select  a.id_desa_bersebelahan, b1.nama desa_asal,b.createdat tanggal_klaim1 ,b12.nama desa_tujuan,c.createdat tanggal_klaim2 from taswil.t_desa_bersebelahan_2 a left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa bb where bb.id_desa = a.desa_1 and bb.ismainmap = true order by createdat desc limit 1 ) b on true left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa cc    where cc.id_desa = a.desa_2 and cc.ismainmap = true order by createdat desc limit 1 ) c on true join taswil.m_desa b1 on a.desa_1 = b1.id_Desa 	join taswil.m_desa b12 on a.desa_2 = b12.id_Desa join taswil.m_kecamatan b2 on b1.id_kecamatan = b2.id_kecamatan join taswil.m_kabkota b3 on b2.id_kabkota = b3.id_kabkota where 1=1 and a.isrejected = false and b.ismainmap = true and c.ismainmap = true and konfirm_desa_1 = true and konfirm_desa_2 = true"  + filterQueryCond+" group by a.id_desa_bersebelahan, b1.nama ,b.createdat  ,b12.nama ,c.createdat  "))
    # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
    # print( "SELECT id_klaim_batas_desa, a.id_desa,ismainmap,createdby,modifiedby,createdat,modifiedat,b.nama FROM taswil.t_klaim_batas_desa a, m_desa b WHERE a.id_desa=b.id_desa"
    #         + filterQueryCond)

    es = [
        dict(
            id=row[0],
            desa_asal=row[1],
            tanggal_klaim1=row[2],
            #peta_utama=getlabeStatusPeta(row[2]),
            desa_tujuan=row[3],
            tanggal_klaim2=row[4],
           
            btn='<div id="dt-buttons" class="dt-buttons">' +            
            '<a class="btn btn-info btnEditForm mr-1" dataid="' + (row[0]) + '"  tabindex="0"  onclick="viewData(this)"><span>Set Sub Segmen</span></a> ' +

            '</div>'
        ) for row in cur.fetchall()
    ]
    jmldata = len(es)
    cur.close()
    con.close()

    return jsonify(draw=int(request.args.get('draw')),
                   recordsTotal=jmldata,
                   recordsFiltered=jmldata,
                   data=es)



@mod.route('/setsubsegmen/form')
@check_session
def setsubsegmen_form():
    # res
    # return render_template('userprofile.html',header_menu='USER PROFILE')

	id = request.args.get('id')
	klaim_batas_desa1 = ""
	klaim_batas_desa2 = ""
	con = connect_db()
	cur = con.cursor()
	cur.execute(
		"select a.id_desa_bersebelahan, b1.nama desa_asal ,b12.nama desa_tujuan , b.id_klaim_batas_desa klaim_batas_desa1, c.id_klaim_batas_desa klaim_batas_desa2,a.desa_1,a.desa_2	from taswil.t_desa_bersebelahan_2 a 	join taswil.t_klaim_batas_desa b on a.desa_1 = b.id_desa  and b.ismainmap = true 		join taswil.t_klaim_batas_desa c on a.desa_2 = c.id_desa and c.ismainmap = true 		join taswil.m_desa b1 on a.desa_1 = b1.id_Desa	join taswil.m_desa b12 on a.desa_2 = b12.id_Desa	where a.id_desa_bersebelahan = %s",
		[id])
	a_role_disabled = 'disabled'
	# es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	for es in cur.fetchall():
		id = es[0]
		desa_asal = noneToStringNull(str(es[1]))
		desa_tujuan = noneToStringNull(str(es[2]))
		klaim_batas_desa1 = (str(es[3]))
		klaim_batas_desa2 = (str(es[4]))
		id_desa_asal = noneToStringNull(str(es[5]))
		id_desa_tujuan = noneToStringNull(str(es[6]))
	cur.close()
	con.close()
	session['p1'] = id
	
	return jsonify(data=render_template('set_sub_segmen_form.html',klaimidDesa1=klaim_batas_desa1,klaimidDesa2=klaim_batas_desa2,desa1 = id_desa_asal,desa2=id_desa_tujuan,id_desa_bersebelahan=id))


@mod.route('/setsubsegmen/geojson1')
@check_session
def setsetsubsegmen_geojson1():
	
	id = session['p1']
	con  = connect_db()
	cur = con.cursor() 	
	cur.execute("select id_subsegmen,ST_AsGeoJSON(a.geom)  geom,a.keterangan , b.no,c.no from taswil.t_subsegmen a left join taswil.t_titikkartometri b on a.id_titikkartometri_Dari = b.id_titikkartometri and a.id_desa_bersebelahan = b.id_desa_bersebelahan left join taswil.t_titikkartometri c on a.id_titikkartometri_ke = c.id_titikkartometri  and a.id_desa_bersebelahan = c.id_desa_bersebelahan where a.id_desa_bersebelahan = %s",[id])
	test1 = []
	i = 0;
	center = ""
	nama = ""
	for  es in cur.fetchall():	
		i = i+1;
		aaa = json.loads(es[1])		
		aac = es[2]
		obj = {'type' : 'Feature','id':es[0],'properties':{'index':str(i),'keterangan':aac,'tk_dari':es[3],'tk_ke':es[4]},'geometry' :aaa }
		test1.append(obj)
		
	cur.close()
	con.close()
	test = {'type': 'FeatureCollection','crs': {'type': 'name','properties': {'name': 'EPSG:4326'}},'features' : test1}
	return jsonify(
       data = test
    )

	
@mod.route('/setsubsegmen/crud', methods=['POST', 'DELETE'])
@check_session
def setsubsegmen_crud():
	paramResult = True
	paramError = ''
	con  = connect_db()
	cur = con.cursor() 	
	id_titikkartometri_awal = ""
	id_titikkartometri_akhir = ""
	start_point = ""
	end_point = ""
	try:
		id = session['p1']
		
		cur.execute("select temptable2.*,b.id_titikkartometri startpoint,c.id_titikkartometri endpoint from (select * from 	( 		select ST_Distance(ST_EndPoint(ST_TRANSFORM(ST_GeomFromGeoJSON(%s),4326))  , geom) jarak,geom, ST_AsText(geom) endpoint 		,ST_AsText(ST_StartPoint(ST_TRANSFORM(ST_GeomFromGeoJSON(%s),4326))) startpoint from taswil.t_titikkartometri where id_desa_bersebelahan =  %s ) temptable1 order by jarak asc limit 1 ) temptable2 left join  taswil.t_titikkartometri b on temptable2.startpoint = ST_AsText(b.geom) and b.id_desa_bersebelahan =  %s  left join  taswil.t_titikkartometri c on temptable2.endpoint = ST_AsText(c.geom) and c.id_desa_bersebelahan = %s",[request.json['geom'],request.json['geom'],id,id,id])
		i = 0;
		for  es in cur.fetchall():	
			i = i+1;
			id_titikkartometri_awal = es[4]
			id_titikkartometri_akhir = es[5]
			start_point = es[3]
			end_point = es[2]
			
		idd = getMD5()
		params = [
					idd,
					request.json['geom'],
					end_point,
					request.json['keterangan'],
					session['p1'],
					getUserName(),
					getUserName()
					,id_titikkartometri_awal
					,id_titikkartometri_akhir
					
					] 
		
		cur.execute('insert into taswil.t_subsegmen select %s ,ST_TRANSFORM(ST_AddPoint(ST_GeomFromGeoJSON(%s),ST_GeomFromText(%s)),4326) , %s , %s ,now()  , now(), %s , %s ,%s,%s  ',params)
		
		
		paramError = "Save data success"
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
		
		
	con.commit()
	con.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )

	
@mod.route('/setsubsegmen/crude', methods=['POST', 'DELETE'])
@check_session
def setsubsegmen_crude():
	paramResult = True
	paramError = ''
	con  = connect_db()
	cur = con.cursor() 	
	start_point = ""
	end_point = ""
	try:
		arraydesa = request.json['listdesa']
		#print(arraydesa)
		for x in arraydesa:
			cur.execute("select ST_AsText(b.geom) startpoint,ST_AsText(c.geom) endpoint from taswil.t_subsegmen a 	left join taswil.t_titikkartometri b on a.id_titikkartometri_Dari = b.id_titikkartometri and a.id_desa_bersebelahan = b.id_desa_bersebelahan 	left join taswil.t_titikkartometri c on a.id_titikkartometri_ke = c.id_titikkartometri  and a.id_desa_bersebelahan = c.id_desa_bersebelahan where a.id_subsegmen = %s",[x['id']])
			i = 0;
			for  es in cur.fetchall():	
				i = i+1
				start_point = es[0]
				end_point = es[1]
			cur.execute('update taswil.t_subsegmen set geom =  ST_TRANSFORM(ST_AddPoint(ST_AddPoint(ST_GeomFromGeoJSON(%s),ST_GeomFromText(%s),0),ST_GeomFromText(%s)),4326) ,dtm_upd = now(),usr_upd = %s where id_subsegmen = %s ',[x['datajson'],start_point,end_point,getUserName(),x['id']])
		paramError = "Save data success"
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
		
		
	con.commit()
	con.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )
	
##################ksub segmen######################



##################kesepakatan######################

@mod.route('/kesepakatan')
@check_session
def kesepakatan_index():
    a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
    # print((a_user_id_wilayah))

    return jsonify(data=render_template('kesepakatan.html',
                                        a_user_id_wilayah=a_user_id_wilayah),
                   header='Kesepatan')
				   


@mod.route('/kesepakatan/data')
@check_session
def kesepakatandata_index():
    con = connect_db()
    cur = con.cursor()
    # print(username[0].get('id'))
    # cur.execute('SELECT * FROM taswil.a_group ')

    filterIdWil = noneToStringNull(request.args.get("id_wilayah"))
    sesIdWil = noneToStringNull(session['id_wilayah'])
    filterQueryCond = ""
    if filterIdWil != "":
        if(len(filterIdWil) < len(sesIdWil)):
            filterIdWil = sesIdWil

        filterQueryCond += " and b3.id_kabkota LIKE '" + filterIdWil + "%' "
    else:
        filterQueryCond += " and b3.id_kabkota LIKE '" + sesIdWil + "%' "

    cur.execute(convertSQLDataTable(
        "select  a.id_desa_bersebelahan, b1.nama desa_asal,b.createdat tanggal_klaim1 ,b12.nama desa_tujuan,c.createdat tanggal_klaim2 from taswil.t_desa_bersebelahan_2 a left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa bb where bb.id_desa = a.desa_1 and bb.ismainmap = true order by createdat desc limit 1 ) b on true left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa cc    where cc.id_desa = a.desa_2 and cc.ismainmap = true order by createdat desc limit 1 ) c on true join taswil.m_desa b1 on a.desa_1 = b1.id_Desa 	join taswil.m_desa b12 on a.desa_2 = b12.id_Desa join taswil.m_kecamatan b2 on b1.id_kecamatan = b2.id_kecamatan join taswil.m_kabkota b3 on b2.id_kabkota = b3.id_kabkota where 1=1 and a.isrejected = false and b.ismainmap = true and c.ismainmap = true and konfirm_desa_1 = true and konfirm_desa_2 = true"  + filterQueryCond+" group by a.id_desa_bersebelahan, b1.nama ,b.createdat  ,b12.nama ,c.createdat  "))
    # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
    # print( "SELECT id_klaim_batas_desa, a.id_desa,ismainmap,createdby,modifiedby,createdat,modifiedat,b.nama FROM taswil.t_klaim_batas_desa a, m_desa b WHERE a.id_desa=b.id_desa"
    #         + filterQueryCond)

    es = [
        dict(
            id=row[0],
            desa_asal=row[1],
            tanggal_klaim1=row[2],
            #peta_utama=getlabeStatusPeta(row[2]),
            desa_tujuan=row[3],
            tanggal_klaim2=row[4],
           
            btn='<div id="dt-buttons" class="dt-buttons">' +            
            '<a class="btn btn-info btnEditForm mr-1" dataid="' + (row[0]) + '"  tabindex="0"  onclick="viewData(this)"><span>Kesepakatan</span></a> ' +

            '</div>'
        ) for row in cur.fetchall()
    ]
    jmldata = len(es)
    cur.close()
    con.close()

    return jsonify(draw=int(request.args.get('draw')),
                   recordsTotal=jmldata,
                   recordsFiltered=jmldata,
                   data=es)



@mod.route('/kesepakatan/form')
@check_session
def kesepakatan_form():
    # res
    # return render_template('userprofile.html',header_menu='USER PROFILE')

	id = request.args.get('id')
	klaim_batas_desa1 = ""
	klaim_batas_desa2 = ""
	txtTanggal = ""
	txtLokasi = ""
	txtKades1 = ""
	txtCamat1 = ""
	txtKades2 = ""
	txtCamat2 = ""
	namaJabDsAsal = ""
	namaJabDsTujuan= "" 
	txtPbdes = ""
	txtDataDasar = ""
	con = connect_db()
	cur = con.cursor()
	cur.execute(
		"select a.id_desa_bersebelahan, b1.nama desa_asal ,b12.nama desa_tujuan , b.id_klaim_batas_desa klaim_batas_desa1, c.id_klaim_batas_desa klaim_batas_desa2,a.desa_1,a.desa_2 ,b2.nama kecamatan_awal,b22.nama kecamatan_akhir,q1.nm_kepala_desa kades1, q1.nm_kepala_Camat camat1,q2.nm_kepala_desa kades2, q2.nm_kepala_Camat camat2	from taswil.t_desa_bersebelahan_2 a 	join taswil.t_klaim_batas_desa b on a.desa_1 = b.id_desa 	join taswil.t_klaim_batas_desa c on a.desa_2 = c.id_desa 	join taswil.m_desa b1 on a.desa_1 = b1.id_Desa join taswil.m_kecamatan b2 on b1.id_kecamatan = b2.id_kecamatan join taswil.m_desa b12 on a.desa_2 = b12.id_Desa join taswil.m_kecamatan b22 on b12.id_kecamatan = b22.id_kecamatan join taswil.a_user q1 on b1.id_desa = q1.id_wilayah join taswil.a_user q2 on b12.id_desa = q2.id_wilayah where a.id_desa_bersebelahan = %s",
		[id])
	a_role_disabled = 'disabled'
	# es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	for es in cur.fetchall():
		id = es[0]
		desa_asal = noneToStringNull(str(es[1]))
		desa_tujuan = noneToStringNull(str(es[2]))
		klaim_batas_desa1 = (str(es[3]))
		klaim_batas_desa2 = (str(es[4]))
		id_desa_asal = noneToStringNull(str(es[5]))
		id_desa_tujuan = noneToStringNull(str(es[6]))
		kecamatan_asal = noneToStringNull(str(es[7]))
		kecamatan_tujuan = noneToStringNull(str(es[8]))
		txtKades1 = noneToStringNull(str(es[9]))
		txtCamat1 = noneToStringNull(str(es[10]))
		txtKades2 = noneToStringNull(str(es[11]))
		txtCamat2 = noneToStringNull(str(es[12]))
		namaJabDsAsal = getNamaJabDesa(id_desa_asal)
		namaJabDsTujuan = getNamaJabDesa(id_desa_tujuan)
		
	
	cur.execute("SELECT *,to_char(tgl_kesepakaran, 'YYYY-MM-DD') FROM TASWIL.T_KESEPAKATAN where id_desa_bersebelahan = %s",[id])
	a_role_disabled = 'disabled'
	# es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	for es in cur.fetchall():		
		txtTanggal = noneToStringNull(str(es[14]))
		txtLokasi = noneToStringNull(str(es[3]))
		
		txtPbdes = noneToStringNull(str(es[8]))
		txtDataDasar = noneToStringNull(str(es[9]))
		
	
	cur.close()
	con.close()
	session['p1'] = id
	print(txtTanggal)
	return jsonify(data=render_template('kesepakatan_form.html',klaimidDesa1=klaim_batas_desa1,klaimidDesa2=klaim_batas_desa2,desa1 = id_desa_asal,desa2=id_desa_tujuan,kecamatan1=kecamatan_asal,kecamatan2=kecamatan_tujuan,desa_asal=desa_asal,desa_tujuan=desa_tujuan,txtTanggal=txtTanggal,txtLokasi=txtLokasi,txtKades1=txtKades1,txtCamat1=txtCamat1,txtKades2=txtKades2,txtCamat2=txtCamat2,txtPbdes=txtPbdes,txtDataDasar=txtDataDasar,namaJabDsAsal=namaJabDsAsal,namaJabDsTujuan=namaJabDsTujuan,id_desa_bersebelahan=id))


def getNamaJabDesa(idDesa):
	if(idDesa[9] == "1"):
		return "Lurah"
	else :
		return "Kepala Desa"
	
@mod.route('/kesepakatan/crud', methods=['POST', 'DELETE'])
@check_session
def kesepakatan_crud():
	paramResult = True
	paramError = ''
	con  = connect_db()
	cur = con.cursor() 	
	id_titikkartometri_awal = ""
	id_titikkartometri_akhir = ""
	start_point = ""
	end_point = ""
	try:
		id = session['p1']
		cur.execute("SELECT id_desa_bersebelahan FROM TASWIL.T_KESEPAKATAN 	where id_desa_bersebelahan = %s",[id])
		i = 0;
		for  es in cur.fetchall():	
			i = i+1

		if i > 0:
			
			params = [
						
						request.json['txtTanggal'],
						request.json['txtLokasi'],
						"",
						"",
						"",
						"",
						request.json['txtPbdes'],
						request.json['txtDataDasar'],						
						getUserName(),
						session['p1']						
						] 
			
			cur.execute('update taswil.t_kesepakatan set tgl_kesepakatan=%s,lokasi_kesepakatan=%, kades1=%s,camat1=%s, kades2=%s,camat2=%s,moderator=%s,data_dasar=%s,dtm_upd=now(),usr_upd=%s where id_desa_bersebelahan = %s  ',params)
		else:
			idd = getMD5()
			params = [
						idd,
						session['p1'],
						request.json['txtTanggal'],
						request.json['txtLokasi'],
						"",
						"",
						"",
						"",
						request.json['txtPbdes'],
						request.json['txtDataDasar'],						
						getUserName(),
						getUserName()						
						] 
			
			cur.execute('insert into taswil.t_kesepakatan select %s ,%s , %s , %s,%s,%s,%s,%s,%s,%s ,now()  , now(), %s , %s  ',params)
		
		
		paramError = "Save data success"
	except Error  as e:
		print(e)
		paramResult = False
		paramError = str(e)
		#assert 'table movies already exists' in str(e)
		
		
	con.commit()
	con.close()	
	return jsonify(
        result = paramResult,
		error = paramError
    )

	
##################kesepakatan######################



##################beritaacara######################

@mod.route('/beritaacara')
@check_session
def beritaacara_index():
    a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
    # print((a_user_id_wilayah))

    return jsonify(data=render_template('beritaacara.html',
                                        a_user_id_wilayah=a_user_id_wilayah),
                   header='Print Berita Acara')
				   


@mod.route('/beritaacara/data')
@check_session
def beritaacaradata_index():
    con = connect_db()
    cur = con.cursor()
    # print(username[0].get('id'))
    # cur.execute('SELECT * FROM taswil.a_group ')

    filterIdWil = noneToStringNull(request.args.get("id_wilayah"))
    sesIdWil = noneToStringNull(session['id_wilayah'])
    filterQueryCond = ""
    if filterIdWil != "":
        if(len(filterIdWil) < len(sesIdWil)):
            filterIdWil = sesIdWil

        filterQueryCond += " and b3.id_kabkota LIKE '" + filterIdWil + "%' "
    else:
        filterQueryCond += " and b3.id_kabkota LIKE '" + sesIdWil + "%' "

    cur.execute(convertSQLDataTable(
        "select  a.id_desa_bersebelahan, b1.nama desa_asal,b.createdat tanggal_klaim1 ,b12.nama desa_tujuan,c.createdat tanggal_klaim2 from taswil.t_desa_bersebelahan_2 a left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa bb where bb.id_desa = a.desa_1 and bb.ismainmap = true order by createdat desc limit 1 ) b on true left join lateral (select createdat,id_Desa,ismainmap from taswil.t_klaim_batas_desa cc    where cc.id_desa = a.desa_2 and cc.ismainmap = true order by createdat desc limit 1 ) c on true join taswil.m_desa b1 on a.desa_1 = b1.id_Desa 	join taswil.m_desa b12 on a.desa_2 = b12.id_Desa join taswil.m_kecamatan b2 on b1.id_kecamatan = b2.id_kecamatan join taswil.m_kabkota b3 on b2.id_kabkota = b3.id_kabkota where 1=1 and a.isrejected = false and b.ismainmap = true and c.ismainmap = true and konfirm_desa_1 = true and konfirm_desa_2 = true"  + filterQueryCond+" group by a.id_desa_bersebelahan, b1.nama ,b.createdat  ,b12.nama ,c.createdat  "))
    # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
    # print( "SELECT id_klaim_batas_desa, a.id_desa,ismainmap,createdby,modifiedby,createdat,modifiedat,b.nama FROM taswil.t_klaim_batas_desa a, m_desa b WHERE a.id_desa=b.id_desa"
    #         + filterQueryCond)

    es = [
        dict(
            id=row[0],
            desa_asal=row[1],
            tanggal_klaim1=row[2],
            #peta_utama=getlabeStatusPeta(row[2]),
            desa_tujuan=row[3],
            tanggal_klaim2=row[4],
           
            btn='<div id="dt-buttons" class="dt-buttons">' +            
            '<a class="btn btn-info btnEditForm mr-1" dataid="' + (row[0]) + '"  tabindex="0"  onclick="viewData(this)"><span>Print Berita Acara</span></a> ' +

            '</div>'
        ) for row in cur.fetchall()
    ]
    jmldata = len(es)
    cur.close()
    con.close()

    return jsonify(draw=int(request.args.get('draw')),
                   recordsTotal=jmldata,
                   recordsFiltered=jmldata,
                   data=es)



@mod.route('/beritaacara/form')
@check_session
def beritaacara_form():
    # res
    # return render_template('userprofile.html',header_menu='USER PROFILE')
	
	kosong = '<div class="col-lg-12"><div class="card card-outline"><div class="card-body"><div class="card card-outline-info"><div class="card-header"><h4 class="mb-0 text-white">BERITA ACARA</h4></div><div class="card-body">Silakan melakukan kesepakatan terlebih dahulu</div></div></div></div></div>'

	id = request.args.get('id')
	id_desa1 = ""
	id_desa2 = ""
	id_kecamatan1 = ""
	id_kecamatan2 = ""
	nama_desa1 = ""
	nama_desa2 = ""
	namaJabDesa1 = ""
	namaJabDesa2 = ""
	nama_kecamatan1 = ""
	nama_kecamatan2 = ""
	nama_kabupaten = ""
	klaim_batas_desa1 = ""
	klaim_batas_desa2 = ""
	con = connect_db()
	cur = con.cursor()
	HEADER = ""
	cur.execute("select b.id_desa,c.id_kecamatan,b.nama,c.nama,d.id_desa,e.id_kecamatan,d.nama,e.nama ,f.nama,a1.id_klaim_batas_desa,a2.id_klaim_batas_desa from taswil.t_desa_bersebelahan_2 a left join taswil.t_klaim_batas_desa a1 on a1.ismainmap = true and a.desa_1 = a1.id_desa left join taswil.t_klaim_batas_desa a2 on a2.ismainmap = true and a.desa_2 = a2.id_desa left join taswil.m_desa b on a.desa_1 = b.id_desa left join taswil.m_kecamatan c on c.id_kecamatan = b.id_kecamatan 	left join taswil.m_desa d on a.desa_2 = d.id_desa left join taswil.m_kecamatan e on e.id_kecamatan = d.id_kecamatan left join taswil.m_kabkota f on e.id_kabkota = f.id_kabkota where A.id_desa_bersebelahan = %s",[id])
	
	
	for es in cur.fetchall():		
		id_desa1 = str(es[0])
		id_kecamatan1 = str(es[1])
		nama_desa1 = str(es[2])
		nama_kecamatan1 = str(es[3])
		id_desa2 = str(es[4])
		id_kecamatan2 = str(es[5])
		nama_desa2 = str(es[6])
		nama_kecamatan2 = str(es[7])
		nama_kabupaten = str(es[8])
		klaim_batas_desa1 = str(es[9])
		klaim_batas_desa2 = str(es[10])
	
	if id_desa1 == "":
		return jsonify(data=Markup(kosong))

	namaJabDesa1 = getNamaJabDesa(id_desa1)
	namaJabDesa2 = getNamaJabDesa(id_desa2)
		
	
	HEADER	= "<tr><td style='text-align: center'>BERITA ACARA</td></tr>"
	HEADER	+= "<tr><td style='text-align: center'>Delineasi Batas Desa Secara Kartometrik</td></tr>"
	if nama_kecamatan1 == nama_kecamatan2:
		HEADER	+= "<tr><td style='text-align: center'>Dalam Satu Kecamatan di "+nama_kabupaten+"</td></tr>"
	else:
		HEADER	+= "<tr><td style='text-align: center'>Antar Kecamatan di "+nama_kabupaten+"</td></tr>"
	
	TEXT1 = ""
	txtTanggal = ""
	txtLokasi = ""
	txtKades1 = ""
	txtCamat1 = ""
	txtKades2 = ""
	txtCamat2 = ""
	txtPbdes = ""
	txtDataDasar = ""
	txtHari = 0	
	txtBulan = 0
	txtTahun = 0
	txtNamaHari = ""
	#cur.execute("SELECT distinct *,EXTRACT(YEAR FROM  tgl_kesepakaran),EXTRACT(MONTH FROM  tgl_kesepakaran),EXTRACT(DAY FROM  tgl_kesepakaran),to_char(tgl_kesepakaran, 'Day') FROM TASWIL.T_KESEPAKATAN where id_desa_bersebelahan = %s",[id])
	cur.execute("SELECT distinct a.tgl_kesepakaran, a.lokasi_kesepakatan,a.moderator,a.data_dasar, EXTRACT(YEAR FROM  tgl_kesepakaran),EXTRACT(MONTH FROM  tgl_kesepakaran),EXTRACT(DAY FROM  tgl_kesepakaran) ,to_char(tgl_kesepakaran, 'Day')  ,q1.nm_kepala_desa kades1, q1.nm_kepala_Camat camat1 ,q2.nm_kepala_desa kades2, q1.nm_kepala_Camat camat2 FROM TASWIL.T_KESEPAKATAN a join taswil.t_desa_bersebelahan_2 b on a.id_desa_bersebelahan = b.id_desa_bersebelahan join taswil.a_user q1 on b.desa_1 = q1.id_wilayah join taswil.a_user q2 on b.desa_2 = q2.id_wilayah where a.id_desa_bersebelahan  = %s ",[id])
	a_role_disabled = 'disabled'
	# es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	for es in cur.fetchall():		
		txtTanggal = noneToStringNull(str(es[0]))
		txtLokasi = noneToStringNull(str(es[1]))
		txtKades1 = noneToStringNull(str(es[8]))
		txtCamat1 = noneToStringNull(str(es[9]))
		txtKades2 = noneToStringNull(str(es[10]))
		txtCamat2 = noneToStringNull(str(es[11]))
		txtPbdes = noneToStringNull(str(es[2]))
		txtDataDasar = noneToStringNull(str(es[3]))	
		txtTahun = int(es[4])
		#txtBulan = int(es[11])
		txtHari = int(es[6])
		if str(es[7]).strip() == "Monday":
			txtNamaHari = "Senin"
		elif  str(es[7]).strip() == "Tuesday":
			txtNamaHari = "Selasa"
		elif  str(es[7]).strip() == "Wednesday":
			txtNamaHari = "Rabu"
		elif  str(es[7]).strip() == "Thursday":
			txtNamaHari = "Kamis"
		elif  str(es[7]).strip() == "Friday":
			txtNamaHari = "Jumat"
		elif  str(es[7]).strip() == "Saturday":
			txtNamaHari = "Sabtu"
		else:
			txtNamaHari = "Minggu"
			
		if int(es[6]) == 1:
			txtBulan = "Januari"
		elif int(es[6]) == 2:
			txtBulan = "Februari"
		elif int(es[6]) == 3:
			txtBulan = "Maret"
		elif int(es[6]) == 4:
			txtBulan = "April"
		elif int(es[6]) == 5:
			txtBulan = "Mei"
		elif int(es[6]) == 6:
			txtBulan = "Juni"
		elif int(es[6]) == 7:
			txtBulan = "Juli"
		elif int(es[6]) == 8:
			txtBulan = "Agustus"
		elif int(es[6]) == 9:
			txtBulan = "September"
		elif int(es[6]) == 10:
			txtBulan = "Oktober"
		elif int(es[6]) == 11:
			txtBulan = "November"
		else:
			txtBulan = "Desember"
			
	if txtNamaHari == "":
		return jsonify(data=Markup(kosong))		
	
	if nama_kecamatan1 == nama_kecamatan2:
		TEXT1	+= "Pada Hari ini, "+txtNamaHari+" tanggal "+terbilang(txtHari)+" bulan "+txtBulan+" tahun "+terbilang(txtTahun)+" telah dilaksanakan pelacakan garis batas Desa secara kartometrik dalam rangka penegasan batas antara Desa "+nama_desa1+" dan Desa "+nama_desa2+" Kecamatan "+nama_kecamatan1+" bertempat di "+txtLokasi+" Kabupaten "+nama_kabupaten+" dengan hasil kesepakatan sebagai berikut:"
	else:
		TEXT1	+= "Pada Hari ini, "+txtNamaHari+" tanggal "+terbilang(txtHari)+" bulan "+txtBulan+" tahun "+terbilang(txtTahun)+" telah dilaksanakan pelacakan garis batas Desa antar kecamatan secara kartometrik dalam rangka penegasan batas antara Desa "+nama_desa1+" Kecamatan "+nama_kecamatan1+" dan Desa "+nama_desa2+" Kecamatan "+nama_kecamatan2+" bertempat di "+txtLokasi+" Kabupaten "+nama_kabupaten+" dengan hasil kesepakatan sebagai berikut:"
		
	TEXT2 = "<tr><td>1.</td><td> Data dasar yang digunakan dalam kegiatan pelacakan batas Desa adalah sebagai berikut:</td></tr>"
	TEXT2 += "<tr><td></td><td> "+txtDataDasar.replace('\n', '<br />').replace('\r', '<br />')+"</td></tr>"
	
	cur.execute("Select degrees(ST_Azimuth(B.GEOM, C.GEOM)),A.KETERANGAN, B.NO,B.KETERANGAN, C.NO,C.KETERANGAN,D.NAMA,C.ISSIMPUL FROM TASWIL.T_SUBSEGMEN A LEFT JOIN TASWIL.T_TITIKKARTOMETRI B ON A.ID_TITIKKARTOMETRI_dARI = B.ID_TITIKKARTOMETRI 	LEFT JOIN TASWIL.T_TITIKKARTOMETRI C ON A.ID_TITIKKARTOMETRI_KE = C.ID_TITIKKARTOMETRI LEFT JOIN LATERAL ( 	select string_agg(BB.NAMA, ', ') NAMA from TASWIL.T_TITIKKARTOMETRI_desa AA JOIN taswil.m_Desa BB on AA.ID_DESA = BB.ID_DESA WHERE AA.ID_TITIKKARTOMETRI = B.ID_TITIKKARTOMETRI ) D ON TRUE where A.id_desa_bersebelahan = %s ORDER BY B.URUT", [id])
	a_role_disabled = 'disabled'
	# es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	arah = ""
	ketSegmen = ""
	no1 = ""
	no2 = ""
	ket1 = ""
	ket2 = ""
	TEXT3 = "<tr><td>2.</td><td> Deskripsi Segmen Batas :</td></tr>"
	inddex = 0
	TEXT3_detil = ""
	simpul_teakhir = "1"
	desk_desa = ""
	for es in cur.fetchall():
		if float(es[0]) <= 22.5:
			arah = "utara"
		elif float(es[0]) >= 22.6 and float(es[0]) <= 67.5:
			arah = "timur laut"
		elif float(es[0]) >= 67.6 and float(es[0]) <= 112.5:
			arah = "timur"
		elif float(es[0]) >= 112.6 and float(es[0]) <= 157.5:
			arah = "tenggara"
		elif float(es[0]) >= 157.6 and float(es[0]) <= 202.5:
			arah = "selatan"
		elif float(es[0]) >= 202.6 and float(es[0]) <= 247.4:
			arah = "barat daya"
		elif float(es[0]) >= 247.6 and float(es[0]) <= 292.5:
			arah = "barat"
		elif float(es[0]) >= 292.6 and float(es[0]) <= 337.5:
			arah = "barat laut"
		else:
			arah = "utara"
		ketSegmen = noneToStringNull(str(es[1]))
		no1 = noneToStringNull(str(es[2]))
		ket1 = noneToStringNull(str(es[3]))
		no2 = noneToStringNull(str(es[4]))
		ket2 = noneToStringNull(str(es[5]))
		simpul_teakhir = noneToStringNull(str(es[7]))
		desk_desa = noneToStringNull(str(es[6]))
		if inddex == 0:
			TEXT3_detil += " Dimulai dari simpul batas antara desa / kelurahan "+desk_desa+" ("+ket1+") yang terletak pada "+no1+" ke arah "+arah+" "+ketSegmen
		else:
			TEXT3_detil += " hingga bertemu "+ket1+" yang terletak pada "+no1+" dilanjutkan ke arah "+arah+" "+ketSegmen
		inddex = inddex +1
	if simpul_teakhir == "2":
		TEXT3_detil += " hingga bertemu simpul batas anatar desa / kelurahan  "+desk_desa+" ("+ket2+") yang terletak pada "+no2
	else:
		TEXT3_detil += " hingga bertemu "+ket2+" yang terletak pada "+no2
	TEXT3 += "<tr><td></td><td> <i>"+TEXT3_detil+"</i></td></tr>"
	
	
	TEXT4 = ""
	
	# cur.execute("Select  B.NO,b.urut,ST_X(b.geom),ST_Y(b.geom),ST_X(ST_Transform(b.geoM,32630)),ST_Y(ST_Transform(b.geoM,32630)),ST_AsLatLonText(b.geom) FROM TASWIL.T_SUBSEGMEN A LEFT JOIN TASWIL.T_TITIKKARTOMETRI B ON A.ID_TITIKKARTOMETRI_dARI = B.ID_TITIKKARTOMETRI 	LEFT JOIN TASWIL.T_TITIKKARTOMETRI C ON A.ID_TITIKKARTOMETRI_KE = C.ID_TITIKKARTOMETRI where A.id_desa_bersebelahan = %s union Select c.NO,case when c.urut = 0 then 100 else c.urut end,ST_X(C.geom),ST_Y(C.geom),ST_X(ST_Transform(C.geoM,32630)),ST_Y(ST_Transform(C.geoM,32630)),ST_AsLatLonText(c.geom) FROM TASWIL.T_SUBSEGMEN A LEFT JOIN TASWIL.T_TITIKKARTOMETRI B ON A.ID_TITIKKARTOMETRI_dARI = B.ID_TITIKKARTOMETRI LEFT JOIN TASWIL.T_TITIKKARTOMETRI C ON A.ID_TITIKKARTOMETRI_KE = C.ID_TITIKKARTOMETRI where A.id_desa_bersebelahan = %s order by urut",[id,id])
	queryyy = """
		select
			B.NO,
			b.urut,
			ST_X(b.geom),
			ST_Y(b.geom),
			ST_X(ST_Transform(b.geoM, get_utmzone(b.geoM))),
			ST_Y(ST_Transform(b.geoM, get_utmzone(b.geoM))),
			ST_AsLatLonText(b.geom),
			get_utmzone(c.geoM) as utmzone,
			case 
				when ST_Y(b.geom) > 0 then 'N'
				when ST_Y(b.geom) = 0 then ''
				else 'S'
			end 
				as utmcode
		from
			TASWIL.T_SUBSEGMEN A
		left join TASWIL.T_TITIKKARTOMETRI B on
			A.ID_TITIKKARTOMETRI_dARI = B.ID_TITIKKARTOMETRI
		left join TASWIL.T_TITIKKARTOMETRI C on
			A.ID_TITIKKARTOMETRI_KE = C.ID_TITIKKARTOMETRI
		where
			A.id_desa_bersebelahan =%s
		union
		select
			c.NO,
			case
				when c.urut = 0 then 100
				else c.urut
			end,
			ST_X(C.geom),
			ST_Y(C.geom),
			ST_X(ST_Transform(C.geoM, get_utmzone(c.geoM))),
			ST_Y(ST_Transform(C.geoM, get_utmzone(c.geoM))),
			ST_AsLatLonText(c.geom),
			get_utmzone(c.geoM) as utmzone,
				case 
				when ST_Y(b.geom) > 0 then 'N'
				when ST_Y(b.geom) = 0 then ''
				else 'S'
			end 
				as utmcode
		from
			TASWIL.T_SUBSEGMEN A
		left join TASWIL.T_TITIKKARTOMETRI B on
			A.ID_TITIKKARTOMETRI_dARI = B.ID_TITIKKARTOMETRI
		left join TASWIL.T_TITIKKARTOMETRI C on
			A.ID_TITIKKARTOMETRI_KE = C.ID_TITIKKARTOMETRI
		where
			A.id_desa_bersebelahan = %s
		order by
			urut
	"""	
	cur.execute(queryyy,[id,id])
	inddex = 1
	for es in cur.fetchall():		
		urutan = str(es[1])
		if es[1] == 100:
			urutan = 0
		longlat = str(es[6])
		longlat = longlat.replace("E","BT").replace("W","BB").replace("S","LS").replace("N","LT")
		alonglat = longlat.split(" ")		
		x1 = str(es[4])
		x1a = x1.split(".")
		x1b = x1a[0]+"."+str(x1a[1])[0:2]
		x2 = str(es[5])
		x2a = x2.split(".")
		x2b = x2a[0]+"."+str(x2a[1])[0:2]
		TEXT4 +="<tr>"
		TEXT4 += "<td style='border: 1px solid black;'>"+ str(inddex)+"</td>"
		TEXT4 += "<td style='border: 1px solid black;'>"+str(es[0])+"</td>"
		TEXT4 += "<td style='border: 1px solid black;'>"+str(alonglat[0])+"</td>"
		TEXT4 += "<td style='border: 1px solid black;'>"+str(alonglat[1])+"</td>"
		TEXT4 += "<td style='border: 1px solid black;'>"+str(x1b)+"</td>"
		TEXT4 += "<td style='border: 1px solid black;'>"+str(x2b)+"</td>"
		TEXT4 += "<td style='border: 1px solid black;'>"+str(es[7])[-2:]+es[8]+"</td>"
		TEXT4 += "</tr>"
		inddex = inddex + 1
	
	
	cur.close()
	con.close()
	session['p1'] = id
	return jsonify(data=render_template('beritaacara_form.html',txtKades1=txtKades1,txtCamat1=txtCamat1,txtKades2=txtKades2,txtCamat2=txtCamat2,txtPbdes=txtPbdes,desa1=id_desa1,desa2=id_desa2,klaimidDesa1=klaim_batas_desa1,klaimidDesa2=klaim_batas_desa2,TEXT4=Markup(TEXT4),TEXT3=Markup(TEXT3),TEXT2=Markup(TEXT2),TEXT1=Markup(TEXT1),HEADER=Markup(HEADER),nama_desa1=nama_desa1,nama_desa2=nama_desa2,nama_kecamatan1=nama_kecamatan1,nama_kecamatan2=nama_kecamatan2,nama_kabupaten=nama_kabupaten,namaJabDesa1=namaJabDesa1,namaJabDesa2=namaJabDesa2))



	
##################kesepakatan######################
