from flask import Blueprint, render_template,jsonify,request,g,session
from app import connect_db,validJWT,noneToStringNull,decodeBase64,encodeBase64,getCountTable,convertSQLDataTable,randomCharacter,getUserName,check_session,getOneValue
#from sqlite3 import Error
from psycopg2 import Error

from coolname import generate

from markupsafe import Markup

mod = Blueprint('monitoring', __name__, template_folder='templates')



##############
#### monito klaim desa ####
##############


@mod.route('/klaimdesa')
@check_session
def klaimdesa_index():	

	return jsonify(
        data=render_template('monitorklaimdesa.html',a_user_id_wilayah=session['id_wilayah']),        
        header='Monitoring Klaim Batas Desa'
		
    )

@mod.route('/klaimdesa/data')
@check_session
def klaimdesa_data():	
	con = connect_db()
	cur = con.cursor()
    # print(username[0].get('id'))
    # cur.execute('SELECT * FROM m_patient ')
	filterIdWil = noneToStringNull(request.args.get("id_wilayah"))
	sesIdWil = noneToStringNull(session['id_wilayah'])
	filterQueryCond = ""
	if filterIdWil != "":
	    if(len(filterIdWil) < len(sesIdWil)):
	        filterIdWil = sesIdWil	
	    filterQueryCond += " c.id_desa LIKE '" + filterIdWil + "%' "
	else:
	    filterQueryCond += " c.id_desa LIKE '" + sesIdWil + "%' "	

	queryy =    """
			select
				Z.nama as nama_provinsi,
				A.NAMA as nama_kabkota,
				B.NAMA as nama_kecamatan,
				C.NAMA as nama_desa,
				coalesce(TEMPTABLE.JUMLAH, 0) JUMLAH,
				coalesce(TEMPTABLE.MAINMAP, 0) MAINMAP
			from
				taswil.m_provinsi Z
			join
				taswil.m_kabkota A on
				A.id_provinsi = Z.id_provinsi
			join TASWIL.M_KECAMATAN B on
				A.ID_KABKOTA = B.ID_KABKOTA
			join TASWIL.M_DESA C on
				C.ID_KECAMATAN = B.ID_KECAMATAN
			left join (
				select
					ID_DESA,
					COUNT(1) JUMLAH,
					SUM(case when ISMAINMAP = true then 1 else 0 end) MAINMAP
				from
					TASWIL.T_KLAIM_BATAS_DESA
				group by
					ID_DESA ) TEMPTABLE on
				C.ID_dESA = TEMPTABLE.ID_dESA
			WHERE			
			""" + filterQueryCond
	# print(queryy)
	cur.execute(
        convertSQLDataTable(queryy))
    # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
	es = [
        dict(
		provinsi=row[0],kabkota=row[1],
        kecamatan=row[2], desa=row[3], 
		jumlah=row[4], mainmap=row[5]
        ) for row in cur.fetchall()
    ]
	cur.close()
	con.close()

    # print(list)
    # print(es)
	jmldata = getCountTable("SELECT count(*) count1 from ("+queryy+") a")
	return jsonify(draw=int(request.args.get('draw')),
                   recordsTotal=jmldata,
                   recordsFiltered=jmldata,
                   data=es)

@mod.route('/klaimdesa/total')
@check_session
def klaimdesa_total():
	con = connect_db()
	cur = con.cursor()
    # print(username[0].get('id'))
    # cur.execute('SELECT * FROM m_patient ')
	filterIdWil = noneToStringNull(request.args.get("id_wilayah"))
	sesIdWil = noneToStringNull(session['id_wilayah'])
	filterQueryCond = ""
	if filterIdWil != "":
	    if(len(filterIdWil) < len(sesIdWil)):
	        filterIdWil = sesIdWil	
	    filterQueryCond += " c.id_desa LIKE '" + filterIdWil + "%' "
	else:
		filterIdWil=sesIdWil
		filterQueryCond += " c.id_desa LIKE '" + sesIdWil + "%' "

	lenId = len(filterIdWil) 
	groupBy = " "
	if(lenId == 2):
		groupBy += "GROUP BY Z.id_provinsi"
	elif (lenId == 4):
		groupBy += "GROUP BY A.id_kabkota"
	elif (lenId == 7):
		groupBy += "GROUP BY B.id_kecamatan"	
	elif (lenId ==10):
		groupBy += "GROUP BY C.id_desa"

	queryy =    """
			select
				count(*) FILTER (WHERE TEMPTABLE.JUMLAH is not null and TEMPTABLE.MAINMAP is not null ) done,
				count(*) FILTER (WHERE TEMPTABLE.JUMLAH is null) undone
			from
				taswil.m_provinsi Z
			join
				taswil.m_kabkota A on
				A.id_provinsi = Z.id_provinsi
			join TASWIL.M_KECAMATAN B on
				A.ID_KABKOTA = B.ID_KABKOTA
			join TASWIL.M_DESA C on
				C.ID_KECAMATAN = B.ID_KECAMATAN
			left join (
				select
					ID_DESA,
					COUNT(1) JUMLAH,
					SUM(case when ISMAINMAP = true then 1 else 0 end) MAINMAP
				from
					TASWIL.T_KLAIM_BATAS_DESA
				group by
					ID_DESA ) TEMPTABLE on
				C.ID_dESA = TEMPTABLE.ID_dESA
			WHERE			
			""" + filterQueryCond + groupBy

	cur.execute(queryy)
	data = cur.fetchall()
	print(data)
	if(len(data) > 0 ):
		result=	dict(jumlah=int(data[0][1]),main=int(data[0][0]))
	else:
		result = dict(jumlah=0,main=0)
	return jsonify(data =result)
	

@mod.route('/tahapan')
@check_session
def tahapan_index():	
	#res
	#return render_template('userprofile.html',header_menu='USER PROFILE')
	con  = connect_db()
	id_wilayah = noneToStringNull(session["id_wilayah"])
	
	
		
	cur = con.cursor() 		
	cur.execute("select c.nama,b.nama,e.nama,d.nama ,coalesce(temptabel.simpul,0) simpul,coalesce(temptabel.karto,0) karto,coalesce(f.id_Desa_bersebelahan,'') subsegmen ,coalesce(g.id_Desa_bersebelahan,'') kesepakatan from taswil.t_desa_bersebelahan_2 a join taswil.m_desa b on a.desa_1 = b.id_Desa 	join taswil.m_kecamatan c on b.id_kecamatan = c.id_kecamatan join taswil.m_desa d on a.desa_2 = d.id_Desa join taswil.m_kecamatan e on d.id_kecamatan = e.id_kecamatan left join ( select id_Desa_bersebelahan,coalesce(sum(case when issimpul=2 then 1 else 0 end),0) simpul ,coalesce(sum(case when issimpul=1 then 1 else 0 end),0) karto from taswil.t_titikkartometri  group by id_Desa_bersebelahan ) temptabel on a.id_Desa_bersebelahan = temptabel.id_Desa_bersebelahan  left join taswil.t_subsegmen f on f.id_Desa_bersebelahan = a.id_Desa_bersebelahan left join taswil.t_kesepakatan g on g.id_Desa_bersebelahan = a.id_Desa_bersebelahan where konfirm_Desa_1 = true and konfirm_Desa_2 = true and (c.id_kabkota = %s or (a.desa_1 = %s or a.desa_2 = %s)) group by c.nama,b.nama,e.nama,d.nama ,coalesce(temptabel.simpul,0),coalesce(temptabel.karto,0) ,coalesce(f.id_Desa_bersebelahan,'')  	,coalesce(g.id_Desa_bersebelahan,'') ",[id_wilayah,id_wilayah,id_wilayah])
	
	es = [dict(kecamatan1=row[0], desa1=row[1],kecamatan2=row[2], desa2=row[3], simpul=row[4], karto=row[5], subsegmen=row[6], kesepakatan=row[7]) for row in cur.fetchall()]
	
	cur.close()
		
	con.close()
	return jsonify(
        data=render_template('monitortahapan.html',loopdatas=es),        
        header='Monitoring Tahapan'
		
    )