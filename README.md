# clone the directory
git clone https://github.com/SimkiJahara/CineBook.git

# move to main directory
cd CineBook

# switch to a branch
git checkout tanmoy

# create a venv
py -3.11 -m venv movie

# activate it
movie\Scripts\activate (windows) or 
source movie/bin/activate(mac/linux)

# go to backend
cd backend

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


