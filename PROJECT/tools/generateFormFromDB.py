import psycopg2

connTable=psycopg2.connect(user = "postgres", password = "123456", host = "192.168.163.3", port = "5432", database = "hms")

curTable = connTable.cursor()

curTable.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
for table in curTable.fetchall():
	print("--" + table[0])
	curColumn = connTable.cursor()
	curColumn.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"+table[0]+"';")
	#begin form
	formText = """ <div class="row">
            <div class="col-md-8">
              <div class="card">
                <div class="card-header card-header-primary">
                  <h4 class="card-title">header</h4>
                  <p class="card-category">sub_header</p>
                </div>
                <div class="card-body">
                  <form>
				  """
		
		#end form
	for kolom in curColumn.fetchall():
		formText = formText + """<div class="row">
                      <div class="col-md-12">
                        <div class="form-group">
                          <label class="bmd-label-floating">"""+kolom[0]+"""</label>
                          <input type="text" class="form-control"  id='f_"""+kolom[0]+"""'  value="{{"""+kolom[0]+"""}}" />
                        </div>
                      </div>
                    </div>"""
		
		
		print("----" + kolom[0])
		
		
		
	formText = formText + """
		 <input type="button" class="btn btn-primary pull-right" value="Update Profile" onclick="test()" />
                    <div class="clearfix"></div>
		 </form>
                </div>
              </div>
            </div>
		</div>
<script>
	function updateForm(){
		execData('URL',{
			'userprofile_user': $('#userprofile_user').val(),
			'userprofile_pass':$('#userprofile_pass').val(),
			'userprofile_fullname':$('#userprofile_fullname').val(),
			'userprofile_phone':$('#userprofile_phone').val(),
			'userprofile_address':$('#userprofile_address').val(),
			'userprofile_bplace':$('#userprofile_bplace').val(),
			'userprofile_bdate':$('#userprofile_bdate').val(),
			'userprofile_email':$('#userprofile_email').val(),
			'userprofile_sex':$('#userprofile_sex').val()
		
		})
	}
		
  </script>
		"""
	text_file = open("form_"+table[0] + ".txt", "w")
	n = text_file.write(formText)
	text_file.close()
curTable.close()
connTable.close()