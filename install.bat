python -m pip install --upgrade pip
pip install virtualenv
set mypath=%cd% 
virtualenv venv
cd ./venv/Scripts
call activate
cd ..
cd ..
pip install -U pylint
pip install flask
pip install -U WTForms
mkdir flaskr
mkdir tests
cd ./flaskr
mkdir static
mkdir templates
ECHO INSTALLATION IS COMPLETE
:End
cmd \k
PAUSE