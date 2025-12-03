# clone the directory
git clone https://github.com/SimkiJahara/CineBook.git

# move to main directory
cd CineBook

# fetch all branch
git fetch

# switch to a branch
git checkout tanmoy

# go to backend
cd backend

# create a venv
py -3.11 -m venv movie

# activate it
movie\Scripts\activate (windows) or 
source movie/bin/activate(mac/linux)

# download requirement.txt
pip install -r requirements.txt

# start backend
uvicorn main:app --reload

# frontend
 cd .. /n
 cd frontend /n
 right click screenings.html /n
 run with live server

# for documentation
cd backend/docs and then : make html

# for unit test
from backend pytest tests/screening.py


