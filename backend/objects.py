from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from pydantic import BaseModel
@dataclass
class UserInfo(BaseModel): 
    first_name: str
    last_name: str
    email: str
    password: str
    institution: str = None
    projects: list = None
    participated_projects: list = None
    is_active: bool = True
    balance: float = 0.0
    payment: dict = None

    def __init__(self, first_name, last_name, email, password, institution=None, projects=None, participated_projects=None, is_active=True, balance=0.0, payment=None):
        super().__init__(first_name=first_name, last_name=last_name, email=email, password=password, institution=institution, projects=projects, participated_projects=participated_projects, is_active=is_active, balance=balance, payment=payment)

    
    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "institution": self.institution,
            "projects": self.projects,
            "participated_projects": self.participated_projects,
            "is_active": self.is_active,
            "balance": self.balance,
            "payment": self.payment,
        }
     
@dataclass
class ProjectInfo(BaseModel): 
    title: str
    description: str
    owner: str
    members: list
    participants: list
    is_active: bool = True
    project_type: str = "private"
    start_date: str = str(datetime.now())
    end_date: str = str(datetime.now() + timedelta(days=90))
    budget: float = 0.0
    salary: float = 0.0

    def __init__(self, title, description, owner, members, participants, is_active=True, project_type="private", start_date=None, end_date=None, budget=0.0, salary=0.0):
        super().__init__(title=title, description=description, owner=owner, members=members, participants=participants, is_active=is_active, project_type=project_type, start_date=start_date, end_date=end_date, budget=budget, salary=salary)


        
    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "owner": self.owner,
            "members": self.members,
            "participants": self.participants,
            "is_active": self.is_active,
            "project_type": self.project_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "budget": self.budget,
            "salary": self.salary,
        }
    
@dataclass
class TransactionInfo(BaseModel):
    project_id: str
    seller_id: str
    buyer_id: str
    amount: float
    valid_until: str = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    def __init__(self, project_id, seller_id, buyer_id, amount, valid_until=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")):
        super().__init__(project_id=project_id, seller_id=seller_id, buyer_id=buyer_id, amount=amount, valid_until=valid_until)



    def to_dict(self):
        return {
            "project_id": self.project_id,
            "seller_id": self.seller_id,
            "buyer_id": self.buyer_id,
            "amount": self.amount,
            "valid_until": self.valid_until,
        }

@dataclass
class SurveyInfo(BaseModel):
    seller_id: str
    buyer_id: str
    project_id: str
    content: str
    answers: list
    is_accepted: bool
    feedback: str = ""

    def __init__(self, seller_id, buyer_id, project_id, content, answers, is_accepted, feedback=""):
        super().__init__(seller_id=seller_id, buyer_id=buyer_id, project_id=project_id, content=content, answers=answers, is_accepted=is_accepted, feedback=feedback)
 
        
    def to_dict(self):
        return {
            "seller_id": self.seller_id,
            "buyer_id": self.buyer_id,
            "project_id": self.project_id,
            "content": self.content,
            "answers": self.answers,
            "is_accepted": self.is_accepted,
            "feedback": self.feedback,
        }
    
    def __setattr__(self, name: str, value: Any) -> None:
        return super().__setattr__(name, value)
    