from fastapi import FastAPI
from database import User, Project, Transaction, Survey
from objects import UserInfo, ProjectInfo, TransactionInfo, SurveyInfo
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/signup")
def signup(user: UserInfo):
    try:
        db = User()
        db.insert_user(user)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.post("/login")
def login(email: str, password: str):
    try:
        db = User()
        user = db.get_user_by_email(email)
        if user["password"] == password:
            return {"status": "success", "user_id": str(user["_id"])}
        else:
            return {"status": "error", "message": "Invalid password"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/delete_user")
def delete_user(email: str):
    try:
        db = User()
        db.delete_user_by_email(email)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.post("/create_project")
def create_project(project: ProjectInfo):
    try:
        db = Project()
        db.insert_project(project)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.post("/get_project")
def get_project(title: str, owner: str):
    try:
        db = Project()
        project = db.get_project(title, owner)
        return {"status": "success", "project": project}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/delete_project")
def delete_project(title: str, owner_email: str):
    try:
        db = Project()
        db.delete_project(title, owner_email)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

    
@app.post("/list_my_projects")
def list_projects(owner_email: str):
    try:
        db = Project()
        projects = db.list_my_projects(owner_email=owner_email)
        return {"status": "success", "projects": projects}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/list_public_projects")
def list_public_projects():
    try:
        db = Project()
        projects = db.list_public_projects()
        return {"status": "success", "projects": projects}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.post("/join_project")
def join_project(title: str, owner: str, participant_email: str):
    try:
        db = Project()
        db.join_project(title, owner, participant_email)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.post("/leave_project")
def leave_project(title: str, owner_email: str, participant_email: str):
    try:
        db = Project()
        db.leave_project(title, owner_email, participant_email)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.post("/delete_survey")
def delete_survey(seller_id: str, buyer_id: str, project_id: str):
    try:
        db = Survey()
        db.delete_survey(seller_id, buyer_id, project_id)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
@app.post("/send_survey")
def send_survey(survey: SurveyInfo):
    try:
        db = Survey()
        db.send_survey(survey)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/get_survey")
def get_survey(seller_id: str, buyer_id: str, project_id: str):
    try:
        db = Survey()
        survey = db.get_survey(seller_id, buyer_id, project_id)
        return {"status": "success", "survey": survey}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.post("/answer_survey")
def answer_survey(survey: SurveyInfo):
    try:
        db = Survey()
        db.answer_survey(survey)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@app.post("/verify_survey")
def verify_survey(survey: SurveyInfo):
    try:
        db = Survey()
        db.verify_survey(survey)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@app.post("/give_feedback")
def give_feedback(survey: SurveyInfo):
    try:
        db = Survey()
        db.give_feedback(survey)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.post("/pay")
def pay(transaction: TransactionInfo):
    try:
        db = Transaction()
        db.pay(transaction)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)