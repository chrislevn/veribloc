from fastapi import FastAPI
from database import User, Project, Transaction, Survey
from objects import UserInfo, ProjectInfo, TransactionInfo, SurveyInfo
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Veriblock API!"}

@app.post("/signup")
def signup(user: UserInfo):
    db = User()
    db.insert_user(user)
    return {"status": "success"}
    
    
@app.post("/login")
def login(email: str, password: str):
    db = User()
    user = db.get_user_by_email(email)
    if user["password"] == password:
        return {"status": "success", "user_id": str(user["_id"])}
    else:
        return {"status": "error", "message": "Invalid password"}
    
@app.post("/delete_user")
def delete_user(email: str):
    db = User()
    db.delete_user_by_email(email)
    return {"status": "success"}
   
    
@app.get("/get_user_id")
def get_user_id(email: str):
    db = User()
    user = db.get_user_by_email(email)
    return {"status": "success", "user_id": str(user["_id"])}
    
    
@app.post("/create_project")
def create_project(project: ProjectInfo):
    db = Project()
    db.insert_project(project)
    return {"status": "success"}

    
@app.post("/get_project")
def get_project(title: str, owner: str):
    db = Project()
    project = db.get_project(title, owner)
    return {"status": "success", "project": project}
    
    
@app.get("/delete_project")
def delete_project(title: str, owner_email: str):
    db = Project()
    db.delete_project(title, owner_email)
    return {"status": "success"}
    

    
@app.post("/list_my_projects")
def list_projects(owner_email: str):
    db = Project()
    projects = db.list_my_projects(owner_email=owner_email)
    return {"status": "success", "projects": projects}
    
    
@app.get("/list_public_projects")
def list_public_projects():
    db = Project()
    projects = db.list_public_projects()
    return {"status": "success", "projects": projects}
   
    
@app.post("/join_project")
def join_project(title: str, owner: str, participant_email: str):
    db = Project()
    db.join_project(title, owner, participant_email)
    return {"status": "success"}
   
    
@app.post("/leave_project")
def leave_project(title: str, owner_email: str, participant_email: str):
    db = Project()
    db.leave_project(title, owner_email, participant_email)
    return {"status": "success"}
    
    
@app.post("/delete_survey")
def delete_survey(seller_id: str, buyer_id: str, project_id: str):
    db = Survey()
    db.delete_survey(seller_id, buyer_id, project_id)
    return {"status": "success"}
   
        
@app.post("/send_survey")
def send_survey(survey: SurveyInfo):
    db = Survey()
    db.send_survey(survey)
    return {"status": "success"}
    
    
@app.get("/get_survey")
def get_survey(seller_id: str, buyer_id: str, project_id: str):
    db = Survey()
    survey = db.get_survey(seller_id, buyer_id, project_id)
    return {"status": "success", "survey": survey}
    
    
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
    db = Survey()
    db.verify_survey(survey)
    return {"status": "success"}

    

@app.post("/give_feedback")
def give_feedback(survey: SurveyInfo):
    db = Survey()
    db.give_feedback(survey)
    return {"status": "success"}

    
@app.post("/pay")
def pay(transaction: TransactionInfo):
    db = Transaction()
    db.pay(transaction)
    return {"status": "success"}
    
@app.get("/delete_transaction")
def delete_transaction(transaction_id: str):
    db = Transaction()
    db.delete_transaction(transaction_id)
    return {"status": "success"}

@app.get("/get_transaction_id")
def get_transaction_id(seller_id: str, buyer_id: str, project_id: str):
    db = Transaction()
    transaction = db.get_transaction_id(seller_id, buyer_id, project_id)
    return {"status": "success", "transaction_id": str(transaction["_id"])}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)