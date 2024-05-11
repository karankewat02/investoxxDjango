echo " BUILD START"
python3.9 -m pip install -r requirements.txt
python3.9 manage.py runserver --noinput --clear
echo " BUILD END"