from flask import Blueprint, render_template, jsonify, request, g, session
from app import connect_db, validJWT, noneToStringNull, decodeBase64, encodeBase64, getCountTable, convertSQLDataTable, randomCharacter, getUserName, check_session, getWilayahById
#from sqlite3 import Error
from psycopg2 import Error

from markupsafe import Markup

mod = Blueprint('profil', __name__, template_folder='templates')


@mod.route('/', methods=['GET', 'POST'])
@check_session
def profil_index():
    con = connect_db()
    c = con.cursor()
    if(request.method == 'GET'):

        alert = ''
        id_wilayah = session['id_wilayah']
        id_level_group = session["id_level_group"]
        iscomplete = session["iscomplete"]

        if(iscomplete == False and id_level_group > 1):
            alert = """
             <div id="alert-profil" class="alert alert-warning" style="width: 100%;" role="alert">
                            Lengkapi formulir profile berikut <a class="alert-link"
                                href="javascirpt:void(0)" >dengan benar</a>.
                </div>
            """

        c.execute("SELECT email, address, mobile,fullname, nm_kepala_desa, nm_kepala_camat from taswil.a_user where id_user = %s", [
                  session['id_user']])
        u = c.fetchone()

        a_username = session["username"]
        a_name_group = session["name_group"]
        a_wilayah = getWilayahById(id_wilayah)['fullname_wilayah']
        a_email = u[0]
        a_address = noneToStringNull(u[1])
        a_mobile = noneToStringNull(u[2])
        a_fullname = u[3]
        a_nm_kepala_desa = u[4]
        a_nm_kepala_camat = u[5]

        c.close()
        con.close()
        return jsonify(
            data=render_template('profil_data.html', a_name_group=a_name_group, alert=Markup(
                alert), a_wilayah=a_wilayah, a_email=a_email, a_address=a_address, a_mobile=a_mobile, a_username=a_username, a_fullname=a_fullname,a_nm_kepala_desa=a_nm_kepala_desa,a_nm_kepala_camat=a_nm_kepala_camat),
            header='Profil Pengguna'
        )

    else:
        id_user = session["id_user"]
        username = session["username"]
        fullname = noneToStringNull(request.json["user_fullname"])
        email = noneToStringNull(request.json["user_email"])
        mobile = noneToStringNull(request.json["user_mobile"])
        address = noneToStringNull(request.json["user_address"])
        nm_kepala_desa = noneToStringNull(request.json["user_nm_kepala_desa"])
        nm_kepala_camat = noneToStringNull(request.json["user_nm_kepala_camat"])
        print(id_user, username, fullname, email, mobile, address,nm_kepala_desa,nm_kepala_camat)
        try:
            c.execute("UPDATE taswil.a_user SET fullname = %s, email =%s,mobile =%s,address=%s,useredit=%s,dateedit=now(),iscomplete = true, nm_kepala_desa=%s, nm_kepala_camat=%s where id_user=%s", [
                      fullname, email, mobile, address, username, nm_kepala_desa,nm_kepala_camat,id_user])
            con.commit()
            result = True
            message = "Berhasil memperbarui"
            session["iscomplete"] = True
            session["fullname"] = fullname
            print(session["iscomplete"])
        except Error as e:
            result = False
            message = str(e)

        c.close()
        con.close()
        return jsonify(
            result=result,
            error=message
        )


@mod.route('/ubahpw', methods=["GET", "POST"])
@check_session
def ubahpw():
    if (request.method == "GET"):
        return jsonify(
            data=render_template('ubah_pw.html'),
            header='Ubah Password'
        )
    elif request.method == "POST":
        con = connect_db()
        c = con.cursor()
        id_user = session["id_user"]
        password_active = request.json["password_active"]
        password_baru = request.json["password_baru"]
        password_konfirmasi = request.json["password_konfirmasi"]

        try :
            c.execute("SELECT * FROM taswil.a_user WHERE id_user = %s and password=%s",
                      [id_user, encodeBase64(password_active)])

            exist = c.fetchall()

            if(len(exist) == 1):
                if(password_baru != password_konfirmasi):
                    result =False
                    message = "Password konfirmasi tidak sama"
                else:
                    c.execute("UPDATE taswil.a_user SET password = %s WHERE id_user = %s",[encodeBase64(password_baru),id_user])
                    con.commit()
                    result =True
                    message = "Berhasil memperbarui password"
            else:
                result =False
                message = "Password aktif salah"
        
        except Error as er :
            result = False
            message = str(er)

        c.close()
        con.close()

        return jsonify(
            result=result,
            error=message
        )