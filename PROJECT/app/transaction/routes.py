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

mod = Blueprint('transaction', __name__, template_folder='templates')

######################
#### DROPDOWNLIST ####
######################


@mod.route('/dropdownlist')
def master_dropdownlist():
    strQuery = ""
    type = request.args.get('type')
    search = request.args.get('search')
    if type == "1":
        strQuery = "SELECT ID,NAME FROM  where  isdelete<>'1' and active <> '1' and lower(name) like lower('%" + \
            search + "%')"
    if type == "2":
        strQuery = "SELECT ID,NAME FROM  where  isdelete<>'1' and active <> '1' and lower(name) like lower('%" + \
            search + "%')"
    if type == "3":
        strQuery = "SELECT ID,NAME FROM  where  isdelete<>'1' and lower(name) like lower('%" + \
            search + "%')"

    con = connect_db()
    cur = con.cursor()
    # print(username[0].get('id'))
    # cur.execute('SELECT * FROM m_medicinecategory ')
    cur.execute(strQuery)
    # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
    es = [dict(id=row[0], name=row[1]) for row in cur.fetchall()]
    cur.close()
    con.close()

    return jsonify(data=es)


##############
#### dokumen desa  ####
##############


@mod.route('/dokumendesa')
@check_session
def dokumendesa_index():
    id_wilayah = noneToStringNull(session["id_wilayah"])
    return jsonify(data=render_template('dokumendesa.html', user_id_wilayah=id_wilayah),
                   header='Dokumen Desa')


@mod.route('/dokumendesa/form')
@check_session
def dokumendesa_form():
    a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
    id_wilayah_selected = noneToStringNull(request.args.get("id_wilayah"))

    if (len(id_wilayah_selected) < len(a_user_id_wilayah)):
        id_wilayah_selected = a_user_id_wilayah
    elif (len(id_wilayah_selected) == len(a_user_id_wilayah)):
        id_wilayah_selected = a_user_id_wilayah

    if(len(id_wilayah_selected) == 10):
        nama_wilayah = getWilayahById(id_wilayah_selected)['fullname_wilayah']
        return jsonify(data=render_template('dokumendesa_form.html', nama_wilayah=nama_wilayah, id_desa=id_wilayah_selected))
    else:
        redirect("/dokumendesa")


@mod.route('/dokumendesa/data')
@check_session
def dokumendesa_data():
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

        filterQueryCond += " and id_desa LIKE '" + filterIdWil + "%' "
    else:
        filterQueryCond += " and id_desa LIKE '" + sesIdWil + "%' "

    cur.execute(
        convertSQLDataTable(
            "SELECT * FROM TASWIL.T_DOKUMEN_DESA WHERE ISDELETE = 0" + filterQueryCond))
    # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
    es = [
        dict(
            nama=row[2],
            description=row[3],
            tgl=row[4],
            btn='<div id="dt-buttons" class="dt-buttons"><a class="dt-button buttons-copy buttons-html5 btnViewForm" dataid="'
            + (row[0]) +
            '" tabindex="0" href="#" data-target="#top-modal"><span>View / Download</span></a><a class="dt-button buttons-copy buttons-html5 btnDeleteForm" dataid="'
            + (row[0]) +
            '" tabindex="0" href="#" data-toggle="modal" data-target="#top-modal"><span>Delete</span></a></div></div>'
        ) for row in cur.fetchall()
    ]
    cur.close()
    con.close()

    # print(list)
    # print(es)
    jmldata = getCountTable(
        "select count(1) count1 from TASWIL.T_DOKUMEN_DESA  where ISDELETE <> 0"
    )
    return jsonify(draw=int(request.args.get('draw')),
                   recordsTotal=jmldata,
                   recordsFiltered=jmldata,
                   data=es)


@mod.route('/dokumendesa/crud', methods=['POST', 'DELETE'])
@check_session
def dokumendesa_crud():
    paramResult = True
    paramError = ''

    # type = session['type']
    # print(id)
    # asdasd111 = request.form['userprofile_user']
    strError = ''

    # print(request.form)

    # print(request.files['file'])

    error = ''
    # return redirect(url_for('download_file', name=filename))
    conn = connect_db()
    c = conn.cursor()

    try:
        if request.is_json == True and 'type' in request.json and request.json[
                'type'] == 3:

            c.execute(
                'update taswil.t_dokumen_desa set isdelete= %s , useredit = %s,dateedit = now() where id = %s',
                ['1', getUserName(), request.json['id']])
        else:
            fileU = request.files['file']

            if 'nama_dok' in request.form and request.form['nama_dok'] == '':
                strError = strError + 'Nama Dokumen'
            if 'file' not in request.files:
                strError = strError + 'FILE'

            if strError != '':
                return strError + " : empty"

            if fileU and allowed_file(fileU.filename):
                filename = secure_filename(fileU.filename)
                dateTimeObj = datetime.now()
                timestampStr = dateTimeObj.strftime("%Y%m%d_%H%M%S")
                filename_add = timestampStr + '_' + filename
                folder = os.path.join(basedir(), "dataupload/dokumen_desa",
                                      getUserName())
                if not os.path.exists(folder):
                    os.makedirs(folder)
                fileU.save(os.path.join(folder, filename_add))

                idd = getMD5()
                # print(idd)
                c.execute(
                    'insert into taswil.t_dokumen_desa select %s , %s , %s , %s ,now() , %s,%s,%s,%s ,now(),%s ',
                    [
                        idd, request.form['desa'], request.form['nama_dok'],
                        request.form['ket_dok'],
                        os.path.join(folder, filename_add),
                        getUserName(), '0', filename,
                        getUserName()
                    ])
            else:
                return "upload file dalam bentuk dok"
        paramError = "Save data success"
    except Error as e:
        print(e)
        error = str(e)
        paramResult = False
        paramError = str(e)
        # assert 'table movies already exists' in str(e)
    if request.is_json == True and 'type' in request.json and request.json[
            'type'] == 3:
        error = jsonify(result=paramResult, error=paramError)

    conn.commit()
    conn.close()

    return error


@mod.route('/dokumendesa/dokumen')
@check_just_session
def dokumendesa_dokumen():
    error = ""
    id = request.args.get('id')
    pathFile = getOneValue("taswil.t_dokumen_desa", "path||'#####'||filename",
                           "id='" + id + "' and isdelete=0")
    slitt = pathFile.split("#####")
    extension = os.path.splitext(slitt[1])[1]
    if os.path.exists(slitt[0]):
        with open(slitt[0], "rb") as binary_file:
            # Read the whole file at once
            data = binary_file.read()
            response = make_response(data)
            response.headers['Content-Type'] = 'application/' + extension
            #	response.headers['Content-Disposition'] = \
            #		'inline; filename=%s.xlsx' % 'yourfilename'
            response.headers[
                'Content-Disposition'] = 'inline; filename=' + slitt[1]
            # +'.'+extension
    else:
        response = render_template('404.html'), 404

    return response


@mod.route('/download/dokumen')
@check_just_session
def upload_dokumen():
    error = ""
    id = request.args.get('id')
    pathFile = getOneValue("taswil.t_uploadpeta", "path",
                           "id='" + id + "' and isdelete=0")
    slitt = pathFile.split("#####")
    extension = os.path.splitext(slitt[0])[1]
    if os.path.exists(slitt[0]):
        with open(slitt[0], "rb") as binary_file:
            # Read the whole file at once
            data = binary_file.read()
            response = make_response(data)
            response.headers[
                'Content-Type'] = 'application/' + extension.replace(".", "")
            #	response.headers['Content-Disposition'] = \
            #		'inline; filename=%s.xlsx' % 'yourfilename'
            response.headers[
                'Content-Disposition'] = 'inline; filename=' + "test"  # slitt[1]
            # +'.'+extension
    else:
        response = render_template('404.html'), 404

    return response

##############
#### upload  ####
##############


@mod.route('/uploadpeta')
@check_session
def upload_index():
    return jsonify(data=render_template('upload.html'), header='UPLOAD PETA')


@mod.route('/uploadpeta/form1')
@check_session
def upload_form():

    return jsonify(data=render_template('upload_form.html'))


@mod.route('/uploadpeta/form')
@check_session
def role_form1():
    # res
    # return render_template('userprofile.html',header_menu='USER PROFILE')

    type = request.args.get('type')
    layer1_filezipshp = ''
    layer2_title = ''
    layer2_abstract = ''
    layer2_epsd = ''
    layer3_filemetadata = ''
    layer3_keyword = ''
    layer3_tags = ''
    typechar = 'TAMBAH'
    a_role_disabled = ''

    session['type'] = type

    if type == '2' or type == '3':
        typechar = 'UBAH'
        if type == '3':
            typechar = 'LIHAT'
        id = request.args.get('id')
        con = connect_db()
        cur = con.cursor()
        cur.execute(
            "SELECT  a.id,filename,layer_title,layer_abstract,kode_epsg,content_metadata,keyword, string_agg(b.tags, ', ') FROM BATNAS.t_upload a join batnas.t_upload_tags b on a.id = b.id WHERE isdelete = 0 and a.id = %s group by a.id,filename,layer_title,layer_abstract,kode_epsg,content_metadata,keyword ",
            [id])
        a_role_disabled = 'disabled'
        # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
        for es in cur.fetchall():
            id = es[0]
            layer1_filezipshp = noneToStringNull(str(es[1]))
            layer2_title = noneToStringNull(str(es[2]))
            layer2_abstract = noneToStringNull(str(es[3]))
            layer2_epsd = noneToStringNull(str(es[4]))
            layer3_filemetadata = noneToStringNull(str(es[5]))
            layer3_keyword = noneToStringNull(str(es[6]))
            layer3_tags = noneToStringNull(str(es[7]))
        cur.close()
        con.close()
        session['p1'] = id
    return jsonify(
        data=render_template('upload_form.html',
                             layer1_filezipshp=layer1_filezipshp,
                             layer2_title=layer2_title,
                             layer2_abstract=layer2_abstract,
                             typechar=typechar,
                             layer2_epsd=layer2_epsd,
                             layer3_filemetadata=layer3_filemetadata,
                             layer3_keyword=layer3_keyword,
                             layer3_tags=layer3_tags))


@mod.route('/uploadpeta/data')
@check_session
def upload_data():
    con = connect_db()
    cur = con.cursor()

    cur.execute(
        convertSQLDataTable(
            "SELECT a.*,b.nama FROM TASWIL.T_uploadpeta a join taswil.m_desa b on a.id_Desa = b.id_Desa where isdelete = 0 "
        ))
    # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
    es = [
        dict(
            nama_desa=row[6],
            nama=row[3],
            keterangan=row[5],
            btn=('<div id="dt-buttons" class="dt-buttons"><a class="dt-button buttons-copy buttons-html5 btnViewForm1" dataid="'
                 + (row[0]) +
                 '" tabindex="0" href="#" data-target="#top-modal"><span>Unduh</span></a><a class="dt-button buttons-copy buttons-html5 btnViewForm" dataid="'
                 + (row[0]) +
                 '" tabindex="0" href="#" data-target="#top-modal"><span>Lihat</span></a><a class="dt-button buttons-copy buttons-html5 btnEditForm" dataid="'
                 + (row[0]) +
                 '" tabindex="0" href="#" ><span>Ubah</span></a><a class="dt-button buttons-copy buttons-html5 btnDeleteForm" dataid="'
                 + (row[0]) +
                 '" tabindex="0" href="#" data-toggle="modal" data-target="#top-modal"><span>Hapus</span></a></div></div>'
                 )) for row in cur.fetchall()
    ]
    cur.close()
    con.close()

    # print(list)
    # print(es)
    jmldata = getCountTable(
        "select count(1) count1 from taswil.T_UPLOAD  where ISDELETE = 0")
    return jsonify(draw=int(request.args.get('draw')),
                   recordsTotal=jmldata,
                   recordsFiltered=jmldata,
                   data=es)


@mod.route('/uploadpeta/crud', methods=['POST', 'DELETE'])
@check_session
def upload_crud():
    paramResult = True
    paramError = ''
    strError = ''
    error = ''
    conn = connect_db()
    c = conn.cursor()

    try:
        if request.is_json == True and 'type' in request.json and request.json[
                'type'] == 3:

            c.execute(
                'update BATNAS.T_UPLOAD set isdelete= %s , useredit = %s,dateedit = now() where id = %s',
                ['1', getIdUserName(), request.json['id']])
        elif request.is_json == True and 'type' in request.json and request.json[
                'type'] == 2:
            if 'layer2_tags' in request.json and request.json[
                    'layer2_tags'] == '':
                strError = strError + 'Tags, '
            if strError != '':
                return strError + " : empty (Input mandatory *)"
            p1 = session['p1']
            c.execute(
                'update BATNAS.T_UPLOAD set useredit = %s,dateedit = now(),layer_title = %s ,layer_abstract = %s,kode_epsg = %s,keyword = %s where id = %s',
                [
                    getIdUserName(), request.json['layer2_title'],
                    request.json['layer2_abstract'],
                    request.json['layer2_epsd'],
                    request.json['layer3_keyword'], p1
                ])
            c.execute('delete from BATNAS.T_UPLOAD_tags where id = %s', [p1])
            tagsss = request.json['layer2_tags']
            for i in range(len(tagsss)):
                # print(list[i])
                tt = tagsss[i].strip()
                c.execute('INSERT INTO batnas.t_upload_tags select %s, %s',
                          [p1, tt])

        # p1 = session['p1']
        else:

            if 'uDesc' in request.form and request.form['uDesc'] == '':
                strError = strError + 'Keterangan , '
            if 'file' not in request.files:
                strError = strError + 'File ZIP (shp,dbf,etc) / KML / KMZ '
            if 'uNama' in request.form and request.form['uNama'] == '':
                strError = strError + 'Nama, '

            if strError != '':
                return strError + " : empty (Input mandatory *)"

            fileU = request.files['file']
            print(fileU.filename)

            if fileU == False or allowed_file_zip(fileU.filename) == False:
                return "Upload shapefile dalam bentuk ZIP"

            filename = secure_filename(fileU.filename)

            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y%m%d_%H%M%S")
            # print(timestampStr)
            # filename_add = timestampStr +'_'+filename;

            pathname, extension = os.path.splitext(filename)
            filename_non_ext = pathname.split('\\')[-1]
            filename_add = filename_non_ext + "_" + timestampStr + extension

            folder = os.path.join(basedir(), "dataupload", getIdUserName())
            if not os.path.exists(folder):
                os.makedirs(folder)
            fileU.save(os.path.join(folder, filename_add))

            idd = getMD5()
            # print(idd)

            c.execute(
                'INSERT INTO taswil.t_uploadpeta (id, id_desa, nama, path, usr_crt,  keterangan) VALUES (%s, %s, %s, %s, %s, %s);',
                [
                    idd, request.form['desa'], request.form['uNama'],
                    os.path.join(folder, filename_add),
                    getIdUserName(), request.form['uDesc']
                ])

            # print(c.query)
            '''
			if fileU and allowed_file_zip(fileU.filename):
				filename = secure_filename(fileU.filename)
				dateTimeObj = datetime.now()
				timestampStr = dateTimeObj.strftime("%Y%m%d_%H%M%S")
				filename_add = timestampStr +'_'+filename;
				folder = os.path.join(basedir(),"dataupload",kode_kl, getIdUserName())
				# if not os.path.exists(folder):
				#	os.makedirs(folder)
				# fileU.save(os.path.join(folder, filename_add))

				idd = getMD5()
				# print(idd)
				# c.execute('insert into BATNAS.T_UPLOAD select %s , %s , %s , %s ,now() , %s,%s,%s,%s ,now(),%s ',[idd,request.form['desa'],request.form['nama_dok'],request.form['ket_dok'],os.path.join(folder, filename_add),getIdUserName(),'0',filename,getIdUserName()] )
			else:
				return "Upload shapefile dalam bentuk ZIP"
			'''
        paramError = "Save data success"
    except Error as e:
        print(e)
        error = str(e)
        paramResult = False
        paramError = str(e)
        # assert 'table movies already exists' in str(e)
    if request.is_json == True and 'type' in request.json and request.json[
            'type'] == 3:
        error = jsonify(result=paramResult, error=paramError)

    conn.commit()
    conn.close()

    return error


# MENU KLAIM BATAS DESA

@mod.route('/klaimbatasdesa')
@check_session
def klaimbatasdesa_index():
    a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
    # print((a_user_id_wilayah))

    return jsonify(data=render_template('klaim_batas_desa.html',
                                        a_user_id_wilayah=a_user_id_wilayah),
                   header='Klaim Batas Desa')


@mod.route('/klaimbatasdesa/delete', methods=["POST"])
@check_session
def klaimbatasdesa_delete():
    id = request.json["id"]
    result = True
    error = "Berhasil menghapus data "
    con = connect_db()
    c = con.cursor()
    try:
        c.execute(
            "DELETE from taswil.t_klaim_batas_desa WHERE id_klaim_batas_desa = %s", [id])
        con.commit()
    except Error as er:
        result = False
        error = str(er)

    con.close()
    return jsonify(result=result, error=error)

@mod.route('/klaimbatasdesa/setmainmap', methods=["POST"])
@check_session
def klaimbatasdesa_setmainmap():
    id = request.json["id"]
    idWilayah = request.json["id_wilayah"]
    result = True
    error = "Berhasil mengganti peta utama "
    con = connect_db()
    c = con.cursor()
    try:
        c.execute("SELECT * from taswil.t_klaim_batas_desa WHERE id_klaim_batas_desa = %s and id_desa=%s", [id,idWilayah])
        isExist = (len(c.fetchall()) > 0)
        if (isExist) :
            c.execute("UPDATE taswil.t_klaim_batas_desa set ismainmap =false where id_desa =%s",[idWilayah])
            c.execute("UPDATE taswil.t_klaim_batas_desa set ismainmap =true, modifiedby=%s,modifiedat = now() where id_klaim_batas_desa = %s and id_desa =%s",[getUserName(),id, idWilayah  ])
            con.commit()
        else :
            result = False
            error = 'Data tidak ditemukan'
    except Error as er:
        result = False
        error = str(er)

    con.close()
    return jsonify(result=result, error=error)


@mod.route('/klaimbatasdesa/editor')
@check_session
def klaimbatasdesa_editor():
	con = connect_db()
	c = con.cursor()
	a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
	a_id_klaim_batas_desa = noneToStringNull(request.args.get("gid"))
	# print((a_user_id_wilayah))
	id_wilayah_selected = noneToStringNull(request.args.get("id_wilayah"))
	
	if (len(id_wilayah_selected) < len(a_user_id_wilayah)):
		id_wilayah_selected = a_user_id_wilayah
	elif (len(id_wilayah_selected) == len(a_user_id_wilayah)):
		id_wilayah_selected = a_user_id_wilayah
	
	data = False
	header = "Terjadi kesalahan memuat halaman"

	if (len(id_wilayah_selected) == 10):
        # print()
		id_button = "btnInsert"
		class_button = ""
		nama_wilayah = getWilayahById(id_wilayah_selected)['fullname_wilayah']
		geodata = ""
		
		if (len(a_id_klaim_batas_desa) != 0):
			c.execute("SELECT  ST_AsGeoJSON(geom) FROM taswil.t_klaim_batas_desa WHERE id_desa= %s and id_klaim_batas_desa=%s ", [
                      id_wilayah_selected, a_id_klaim_batas_desa])
			data = c.fetchall()
			if(len(data) == 1):
                # print(data[0][0])
				geodata = "=" + data[0][0]

		result = render_template("gambarbatasdesa.html",
                                 nama_wilayah=nama_wilayah,
                                 id_wilayah=id_wilayah_selected,
                                 id_button=id_button,
                                 class_button=class_button,
                                 a_id_klaim_batas_desa=a_id_klaim_batas_desa,
                                 geodata=Markup(geodata))
		header = "Editor Batas Desa"
		
	return jsonify(data=result, header=header)


@mod.route('/klaimbatasdesa/upload', methods=["POST"])
@check_session
def klaimbatasdesa_upload():
    con = connect_db()
    c = con.cursor()

    id_wilayah = request.json["id_wilayah"]
    feature = request.json["geom"]
    print(feature["geometry"])
    geom = json.dumps(feature["geometry"])
    id_klaim_batas_desa = request.json['id_klaim_batas_desa']

    # print(type(geom))
    result = True
    header = "Berhasil menyimpan"
    insert_id = ""

    username = getUserName()
    try:
        # print(id_wilayah, id_klaim_batas_desa, geom)
        if(id_klaim_batas_desa == ""):
            insert_id = str(uuid.uuid4())
            params = [insert_id, id_wilayah,
                      username, username, geom]
            c.execute("""
            INSERT INTO taswil.t_klaim_batas_desa
            (id_klaim_batas_desa,id_desa,createdby,modifiedby,geom)
            VALUES (%s,  %s, %s,%s,ST_GeomFromGeoJSON(%s))
            """, params)
            
            con.commit()
        else:
            insert_id = id_klaim_batas_desa
            c.execute(
                "SELECT * FROM taswil.t_klaim_batas_desa WHERE id_desa= %s and id_klaim_batas_desa=%s ", [id_wilayah, insert_id])
            exist = c.fetchall()
            if (len(exist) > 0):
                params = [username, geom, insert_id]

                c.execute(
                    "UPDATE taswil.t_klaim_batas_desa SET modifiedby = %s, modifiedat = now(), geom = ST_GeomFromGeoJSON(%s) WHERE id_klaim_batas_desa = %s", params)
                con.commit()
                result = True
                header = "Data berhasil diperbaharui"
            else:
                result = False
                header = "Terjadi kesalahan, data tidak ditemukan"
            print("update")
    except Error as er:
        result = False
        header = str(er)

    # print(c.query)
    con.close()
    return jsonify(result=result, error=header, insert_id=insert_id, id_wilayah=id_wilayah)


@mod.route('/klaimbatasdesa/data')
@check_session
def klaimbatasdesadata_index():
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

        filterQueryCond += " and a.id_desa LIKE '" + filterIdWil + "%' "
    else:
        filterQueryCond += " and a.id_desa LIKE '" + sesIdWil + "%' "

    cur.execute(
        convertSQLDataTable(
            "SELECT id_klaim_batas_desa, a.id_desa,ismainmap,a.createdby,a.modifiedby, to_char(a.createdat, 'YYYY-MM-DD HH24:MI:SS') as createdat,to_char(a.modifiedat, 'YYYY-MM-DD HH24:MI:SS') as modifiedat,b.nama FROM taswil.t_klaim_batas_desa a, m_desa b WHERE a.id_desa=b.id_desa"
            + filterQueryCond))
    # es = [dict(id=row[0], movie_name=row[1]) for row in cur.fetchall()]
    # print( "SELECT id_klaim_batas_desa, a.id_desa,ismainmap,createdby,modifiedby,createdat,modifiedat,b.nama FROM taswil.t_klaim_batas_desa a, m_desa b WHERE a.id_desa=b.id_desa"
    #         + filterQueryCond)

    es = [
        dict(
            id=row[0],
            id_desa=row[1],
            nama_desa=row[7],
            peta_utama=getlabeStatusPeta(row[2]),
            uploadby=row[3],
            uploadat=row[5],
            modifiedby=row[4],
            modifiedat=row[6],
            btn='<div id="dt-buttons" class="dt-buttons">' +
            '<a class="btn btn-primary btnEditForm mr-1" nm-desa="'+row[7]+'" dataid="' + (row[0]) + '" dataidwilayah="' + (row[1]) + '" onclick="setMainMap(this)"><span class="text-white">Jadikan Peta Utama</span></a>' +
            '<a class="btn btn-info btnEditForm mr-1" dataid="' + (row[0]) + '" dataidwilayah="' + (row[1]) + '" tabindex="0"  onclick="viewData(this)"><span>Edit/Lihat</span></a>' +
            '<a class="btn btn-danger btnDeleteForm" dataid="' + (row[0]) + '" tabindex="0"  data-toggle="modal" data-target="#top-modal"><span>Hapus</span></a> ' +

            '</div>'
        ) for row in cur.fetchall()
    ]
    jmldata = len(es)
    cur.close()
    con.close()

    # print(list)
    # print(es)
    # jmldata = getCountTable(
    #     "SELECT count(1) FROM TASWIL.a_user a join taswil.a_group b on a.id_group = b.id_group where 1=1 and a.isdelete<>'1'"
    #     + filterQueryCond)
    return jsonify(draw=int(request.args.get('draw')),
                   recordsTotal=jmldata,
                   recordsFiltered=jmldata,
                   data=es)


def getlabeStatusPeta(status):
    if(status):
        return '<span class="badge badge-success badge-fs">Ya</span>'
    else:
        return '<span class="badge badge-light badge-fs">Tidak</span>'


# MENU DESA BERSEBELAHAN

@mod.route("/desabersebelahan")
@check_session
def desabersebelahan_index():
    a_user_id_wilayah = noneToStringNull(session["id_wilayah"])
    return jsonify(data=render_template('desabersebelahan2.html',
                                        user_id_wilayah=a_user_id_wilayah),
                   header='Input Desa Bersebelahan')


@mod.route("/desabersebelahan/data")
@check_session
def desabersebelahan_data():
    con = connect_db()
    c = con.cursor()

    filterIdWil = noneToStringNull(request.args.get("id_wilayah"))
    sesIdWil = noneToStringNull(session['id_wilayah'])
    idWil = ""
    if filterIdWil != "":
        if(len(filterIdWil) < len(sesIdWil)):
            filterIdWil = sesIdWil

        idWil =  filterIdWil 
    else:
        idWil =  sesIdWil 

    # try :
    # except Error as er:
    #     result
    status = True
    err = ""
    result=dict()
    try :
        query = """
                select
                	case
                		when requestby = %s then 'pengajuan'
                		else 'permintaan'
                	end as tipe,
                	case 
                		when desa_1 = %s then desa_2 
                		else desa_1 
                	end as id_desa_tujuan,
                	case 
                		when desa_1 = %s then concat(c.nama,', ',e.nama )
		                else concat(b.nama,', ',d.nama)
                	end as nama_desa_tujuan,
                	case 
                		when isrejected = true then 'ditolak' 
                		when (konfirm_desa_1 =true AND konfirm_desa_2 =true) then 'terkonfirmasi'
                		else 'menunggu konfirmasi'
                	end as status,
                    a.id_desa_bersebelahan
                from
                	taswil.t_desa_bersebelahan_2 a
                left join taswil.m_desa b on a.desa_1 =b.id_desa 
                left join taswil.m_desa c on a.desa_2 =c.id_desa 
                join taswil.m_kecamatan d on b.id_kecamatan=d.id_kecamatan 
                join taswil.m_kecamatan e on c.id_kecamatan=e.id_kecamatan 
                where
                	id_desa_bersebelahan like %s

        """
        c.execute(query,[idWil,idWil,idWil,"%id."+idWil+'%'])
        data= [dict(tipe=r[0],id_desa_tujuan=r[1],nama_desa_tujuan=r[2],status=r[3],id=r[4]) for r in c.fetchall()]
        result['list']=data
        result['id_desa_asal'] = idWil
    except Error as er :
        status=False
        err = str(er)

    return jsonify(data=result,status=status,error=err)


@mod.route("/desabersebelahan/add", methods=["POST"])
@check_session
def desabersebelahan_add():
    con = connect_db()
    c = con.cursor()

    id_desa_asal = noneToStringNull(request.json["id_desa_asal"])
    id_desa_tujuan = noneToStringNull(request.json["id_desa_tujuan"])
    username = getUserName()

    idInsert = generateIdDesaBersebelahan(id_desa_asal, id_desa_tujuan)

    result = True
    error = "Berhasil menambahkan data"
    try:
        # print()
        c.execute("SELECT requestby FROM taswil.t_desa_bersebelahan_2 WHERE id_desa_bersebelahan =%s",
                  [idInsert])
        tmpData = c.fetchall()
        isExist = len(tmpData) > 0

        desa_1 = id_desa_asal
        desa_2 = id_desa_tujuan

        c_1 = True
        c_2=False

        if(desa_2<desa_1):
            desa_1 = id_desa_tujuan
            desa_2 = id_desa_asal
            c_1=False
            c_2=True

        if (isExist == False):
            c.execute('INSERT INTO taswil.t_desa_bersebelahan_2 (id_desa_bersebelahan,desa_1,desa_2,konfirm_desa_1,konfirm_desa_2,requestby,createdby,modifiedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            [idInsert,desa_1,desa_2,c_1,c_2,id_desa_asal,username,username])
            print(c.query)
            con.commit()
        else:
            # print(tmpData[0][0])
            if(tmpData[0][0]!= id_desa_asal):
                
                c.execute('UPDATE taswil.t_desa_bersebelahan_2 SET konfirm_desa_2 = true,konfirm_desa_1=true, isrejected=false, modifiedby=%s,modifiedat=now() WHERE id_desa_bersebelahan=%s',
                [username,idInsert])
                con.commit()
            else:
                result = False
                error = "Anda sudah menambahkan desa tersebut"

    except Error as er:
        result = False
        error = str(er)

    con.close()
    return jsonify(result=result, error=error)

@mod.route("/desabersebelahan/reject", methods=["POST"])
@check_session
def desabersebelahan_reject():
    con = connect_db()
    c = con.cursor()

    id_desa_asal = noneToStringNull(request.json["id_desa_asal"])
    id_desa_tujuan = noneToStringNull(request.json["id_desa_tujuan"])
    username = getUserName()

    insertId = generateIdDesaBersebelahan(id_desa_asal, id_desa_tujuan)
    result = True
    error = "Berhasil menolak permintaan"
    try:
        # print()
        c.execute("SELECT * FROM taswil.t_desa_bersebelahan_2 WHERE id_desa_bersebelahan = %s",
                  [insertId])
        isExist = len(c.fetchall()) > 0

        if (isExist == True):
            
            c.execute("UPDATE taswil.t_desa_bersebelahan_2 set isrejected=true,modifiedby=%s,modifiedat =now() WHERE id_desa_bersebelahan = %s", [
                       username, insertId])
            con.commit()
        else:
            result = False
            error = "Data tidak ditemukan"

    except Error as er:
        result = False
        error = str(er)

    con.close()
    return jsonify(result=result, error=error)

@mod.route("/desabersebelahan/delete", methods=["POST"])
@check_session
def desabersebelahan_delete():
    con = connect_db()
    c = con.cursor()

    id_desa_asal = noneToStringNull(request.json["id_desa_asal"])
    id_desa_tujuan = noneToStringNull(request.json["id_desa_tujuan"])
    username = getUserName()

    insertId = generateIdDesaBersebelahan(id_desa_asal, id_desa_tujuan)
    result = True
    error = "Berhasil menghapus pengajuan"
    try:
        # print()
        c.execute("SELECT * FROM taswil.t_desa_bersebelahan_2 WHERE id_desa_bersebelahan = %s",
                  [insertId])
        isExist = len(c.fetchall()) > 0

        if (isExist == True):
            
            c.execute("DELETE FROM taswil.t_desa_bersebelahan_2 WHERE id_desa_bersebelahan = %s", [
                        insertId])
            con.commit()
        else:
            result = False
            error = "Data tidak ditemukan"

    except Error as er:
        result = False
        error = str(er)

    con.close()
    return jsonify(result=result, error=error)

    con.close()
    return jsonify(result=result, error=error)


def generateIdDesaBersebelahan(desa1,desa2):
    a =['id.'+desa1,'id.'+desa2]
    return ''.join(sorted(a))