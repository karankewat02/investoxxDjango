echo " BUILD START"
python -m pip install -r requirements.txt
python manage.py runserver --noinput --clear
echo " BUILD END"