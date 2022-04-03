from flask import Blueprint, render_template,jsonify,request,g,session,make_response
from app import connect_db,noneToStringNull,decodeBase64,encodeBase64,getCountTable,convertSQLDataTable,randomCharacter,getUserName,check_session,getMD5,allowed_file,basedir,getOneValue,check_just_session

from datetime import datetime

from werkzeug.utils import secure_filename

import  os

#from sqlite3 import Error
from psycopg2 import Error

from markupsafe import Markup

mod = Blueprint('chat', __name__, template_folder='templates')



##############
#### dokumen desa  ####
##############


@mod.route('/')
@check_session
def chat_index():	
	return jsonify(
        data=render_template('chat.html'),        
        header='CHAT'
    )