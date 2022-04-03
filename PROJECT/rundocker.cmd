@REM docker build -t taswil -f ./Dockerfile.dev .
docker run -it -v D:/Latihan/Flask/taswil/PROJECT:/usr/src/app -p 5050:5000 --name taswil taswil bash -c "export FLASK_ENV=development && flask run --host=0.0.0.0"
