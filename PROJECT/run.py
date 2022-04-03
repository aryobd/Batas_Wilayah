# run.py

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime




from app import app





if __name__ == "__main__":
	#logging.basicConfig(filename='logs/'+datetime.now().strftime('%Y_%m_%d.log'),level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
	app.run()
	#app.run(host='192.168.100.253')
	#app.run(host='0.0.0.0', port=90)



