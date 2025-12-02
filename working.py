from fastapi import FastAPI 
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Manager(BaseModel):
    managerID: int
    managerName: str
    managerContact: str
    branchID: int

''' Base class for Screening with all its attributes '''
class Screening(BaseModel):
    screeningID: int
    movieName: str
    hallID: int
    screeningDate: str
    startTime: str
    isPublished: bool = False
    seatsBooked: Optional[int] = None

''' When creating a screenings, we cannot directly publish it.
It will always be created as unpublished.
So ScreeningCreate will not have the attribute isPublished. '''
class ScreeningCreate(BaseModel):
    screeningID: int
    movieName: str
    hallID: int
    screeningDate: str
    startTime: str
    seatsBooked: Optional[int] = None

''' While editing a screening, user can only change its info, not its publish status.
So ScreeningEdit will not include the attributes screeningID and isPublished. '''
class ScreeningEdit(BaseModel):
    movieName: Optional[str] = None
    hallID: Optional[int] = None
    screeningDate: Optional[str] = None
    startTime: Optional[str] = None
    seatsBooked: Optional[int] = None

''' Dummy data structure [list] to contains all screenings. Takes Screening objects. '''
screeningsList = []

@app.get("/")  
def home():
    return {"Data": "Test"}

@app.get("/manager-dashboard")
def manager_dashboard(managerID: int):
    return {"Dashboard": "Loaded"}

'''
schedule_screening will take input from the manager about the screening,
ie the manager will provide the data for the screening object,
then that info will be appended to the list of screenings or added to the database.
'''
@app.post("/schedule-screening")
def schedule_screening(screeningCreate: ScreeningCreate):
    screening = Screening(**screeningCreate.model_dump(), isPublished = False)
    screeningsList.append(screening)
    return screeningsList

'''
Each unpublished screening card will have Edit, Publish, and Delete buttons.
The Edit button will take the manager to the edit page for that screening.
So the url will be /edit-screening/{screeningID}.
Same for the Publish and Delete buttons. They will simply redirect the manager 
to a confirmation page UI.
When you click the confirmation buttons on the redirected pages,
that's when your actual editing/publishing/deleting happens.
This is done by redirecting you to a confirmation page with the url
/screening-edited/{screeningID} or /screening-published/{screeningID} or /screening-deleted/{screeningID}.
'''
@app.get("/get-unpublished-screenings")
def get_unpublished_screenings(hallID: Optional[int] = None, 
                            screeningDate: Optional[str] = None, 
                            movieName: Optional[str] = None):
    
    unpublishedScreeningsList = []
    
    for screening in screeningsList:
        if (screening.isPublished == False 
            and (hallID is None or screening.hallID == hallID) 
            and (screeningDate is None or screening.screeningDate == screeningDate) 
            and (movieName is None or screening.movieName == movieName)):
                
            unpublishedScreeningsList.append(screening)

    return unpublishedScreeningsList

@app.get("/get-published-screenings")
def get_published_screenings(hallID: Optional[int] = None, 
                            screeningDate: Optional[str] = None, 
                            movieName: Optional[str] = None):
    
    publishedScreeningsList = []
    
    for screening in screeningsList:
        if (screening.isPublished == True 
            and screening.screeningDate > '2025 Dec 13th'
            and (hallID is None or screening.hallID == hallID) 
            and (screeningDate is None or screening.screeningDate == screeningDate) 
            and (movieName is None or screening.movieName == movieName)):
            
            publishedScreeningsList.append(screening)

    return publishedScreeningsList

@app.get("/get-past-screenings")
def get_past_screenings():
        pastScreeningsList = []
    
    for screening in screeningsList:
        if (screening.isPublished == True 
            and screening.screeningDate < '2025 Dec 13th'
            and (hallID is None or screening.hallID == hallID) 
            and (screeningDate is None or screening.screeningDate == screeningDate) 
            and (movieName is None or screening.movieName == movieName)):
                
            pastScreeningsList.append(screening)

    return pastScreeningsList

'''
Frontend page to display already existing info of screening with editable fields
'''
@app.get("/edit-screening/{screeningID}")
def edit_screening():
    return True

'''
Calls a function that edits the screening info and returns a confirmation to the frontend.
'''
@app.put("/screening-edited/{screeningID}")
def edit_screening(screeningID: int, screeningEdit: ScreeningEdit):
    for screening in screeningsList:
        if screening.screeningID == screeningID:
            if screeningEdit.movieName is not None:
                screening.movieName == screeningEdit.movieName
            
            if screeningEdit.hallID is not None:
                screening.hallID == screeningEdit.hallID
            
            if screeningEdit.screeningDate is not None:
                screening.screeningDate == screeningEdit.screeningDate
            
            if screeningEdit.startTime is not None:
                screening.startTime == screeningEdit.startTime
            
            ''' if screeningEdit.isPublished is not None:
                screening.isPublished == screeningEdit.isPublished '''
            
            if screeningEdit.seatsBooked is not None:
                screening.seatsBooked == screeningEdit.seatsBooked

            # return "Screening successfully edited\n" + screening
            # you can't add a string to a json response like this
            return {"Confirmation message": "Screening successfully edited\n", "Updated screening": screening}

    return "Screening does not exist"

'''
Frontend page to display already existing info of screening with Publish button
'''
@app.get("/publish-screening/{screeningID}")
def publish_screening():
    return True

'''
Calls a function that edits the screening info and returns a confirmation to the frontend.
'''
@app.put("/screening-published/{screeningID}")
def publish_screening(screeningID: int):
    for screening in screeningsList:
        if screening.screeningID == screeningID:
            screening.isPublished = True
            return "Screening has been published."

    return "Screening does not exist"

'''
Frontend page to display already existing info of screening with Delete button
'''
@app.get("/delete-screening/{screeningID}")
def delete_screening():
    return True

'''
Calls a function that edits the screening info and returns a confirmation to the frontend.
'''
@app.delete("/screening-deleted/{screeningID}")
def delete_screening(screeningID: int):
    for screening in screeningsList:
        if screening.screeningID == screeningID:
            screeningsList.remove(screening)
            return "Screening was successfully deleted."

    return "Screening does not exist."
