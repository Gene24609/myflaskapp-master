python -m pip install --upgrade pip
set mypath=%cd% 
cd ./venv/Scripts
call activate
cd ..
cd ..
set FLASK_APP=flaskr
set FLASK_ENV=env
call flask run --host=192.168.0.130 --port 80
cd "\Program Files (x86)\Google\Chrome\Application"
chrome http://127.0.0.1/
:End
cmd \k
PAUSE