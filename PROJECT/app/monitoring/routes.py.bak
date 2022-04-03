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
	#res
	#return render_template('userprofile.html',header_menu='USER PROFILE')
	con  = connect_db()
	id_wilayah = noneToStringNull(session["id_wilayah"])
	
	whereCondition = " A.ID_KABKOTA"
	if len(id_wilayah) > 6:
		whereCondition = " C.ID_DESA "
		
	cur = con.cursor() 		
	cur.execute('select A.NAMA,B.NAMA,C.NAMA,coalesce(TEMPTABLE.JUMLAH,0) JUMLAH,coalesce(TEMPTABLE.MAINMAP,0) MAINMAP from taswil.m_kabkota A JOIN TASWIL.M_KECAMATAN B ON A.ID_KABKOTA = B.ID_KABKOTA JOIN TASWIL.M_DESA C ON C.ID_KECAMATAN = B.ID_KECAMATAN LEFT JOIN 	( 	SELECT ID_DESA, COUNT(1) JUMLAH,SUM(CASE WHEN ISMAINMAP = TRUE THEN 1 ELSE 0 END) MAINMAP FROM TASWIL.T_KLAIM_BATAS_DESA GROUP BY ID_DESA ) TEMPTABLE ON C.ID_dESA = TEMPTABLE.ID_dESA 	where '+whereCondition+' = %s ORDER BY B.NAMA,C.NAMA',[id_wilayah])
	
	es = [dict(kecamatan=row[1], desa=row[2], jumlah=row[3], mainmap=row[4]) for row in cur.fetchall()]
	
	cur.close()
		
	con.close()
	return jsonify(
        data=render_template('monitorklaimdesa.html',loopdatas=es),        
        header='Monitoring Klaim Batas Desa'
		
    )

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