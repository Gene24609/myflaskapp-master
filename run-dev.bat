@echo off
set mypath=%cd% 
cd ./venv/Scripts
call activate
cd ..
cd ..
set FLASK_APP=flaskr
set FLASK_ENV=development
call flask run --port 80
:End
cmd \k
PAUSE