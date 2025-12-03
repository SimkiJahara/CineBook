# clone the directory
git clone https://github.com/SimkiJahara/CineBook.git

# switch to a branch
git checkout tanmoy

# create a venv
py -3.11 -m venv movie

# activate it
venv\Scripts\activate (windows) or 
source venv/bin/activate(mac/linux)

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


