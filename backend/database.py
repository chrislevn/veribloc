from pymongo import MongoClient
from dotenv import load_dotenv
import os
from objects import UserInfo, ProjectInfo, TransactionInfo, SurveyInfo
from datetime import datetime

load_dotenv(override=True)

class User:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))

    def ping(self):
        try:
            self.client.admin.command("ping")
            return True
        except Exception as e:
            return False

    def get_users_database(self):
        return self.client["labcoin"]["users"]

    def insert_user(self, user: UserInfo):
        users = self.get_users_database()
        try:
            if users.find_one({"email": user.email}):
                raise Exception("User already exists")
            else:
                users.insert_one(user.to_dict())
                return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_user_id_by_email(self, email):
        """
        Get user by email
        """
        users = self.get_users_database()
        return users.find_one({"email": email})["_id"]

    def get_user_by_id(self, id) -> dict:
        users = self.get_users_database()
        return users.find_one({"_id": id})
    
    def get_user_by_email(self, email):
        """
        Get user by email
        """
        users = self.get_users_database()
        return users.find_one({"email": email})

    def update_user(self, email, user):
        users = self.get_users_database()
        users.update_one({"email": email}, {"$set": user})

    def delete_user_by_email(self, email):
        """
        Delete user by email
        """
        users = self.get_users_database()
        users.delete_one({"email": email})

    def get_user_id(self, email, password):
        users = self.get_users_database()
        return users.find_one({"email": email, "password": password})["_id"]

    def get_user_projects(self, email):
        users = self.get_users_database()
        return users.find_one({"email": email})["projects"]
    
    def get_user_participated_projects(self, email):
        users = self.get_users_database()
        return users.find_one({"email": email})["participated_projects"]
    
    def increase_balance(self, email, amount):
        user = self.get_user_by_email(email)
        user["balance"] += amount
        self.update_user(email, user)
        return {"status": "success"}
    
    def decrease_balance(self, email, amount):
        user = self.get_user_by_email(email)
        if user["balance"] < amount:
            raise Exception("User does not have enough balance")
        else:
            user["balance"] -= amount
            self.update_user(email, user)
            return {"status": "success"}
        
class Project:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))

    def ping(self):
        try:
            self.client.admin.command("ping")
            return True
        except Exception as e:
            return False
        
    def get_projects_database(self):
        return self.client["labcoin"]["projects"]

    def insert_project(self, project: ProjectInfo):
        projects = self.get_projects_database()
        if projects.find_one({"title": project.title, "owner": project.owner}):
            raise Exception("Project already exists")
        else:
            projects.insert_one(project.to_dict())
            return {"status": "success"}

    def get_project(self, id):
        projects = self.get_projects_database()
        return projects.find_one({"_id": id})
    
    def get_project_id(self, title, owner):
        projects = self.get_projects_database()
        result = projects.find_one({"title": title, "owner": owner})
        return result["_id"]
    
    def join_project(self, title, owner, participant):
        projects = self.get_projects_database()
        project = projects.find_one({"title": title, "owner": owner})
        number_of_participants = len(project["participants"])
        expected_number_of_participants = project["budget"] // project["salary"]
        if number_of_participants >= expected_number_of_participants:
            raise Exception("Project is full")
        if participant in project["participants"]:
            raise Exception("Participant already exists")
        else:
            project["participants"].append(participant)
            projects.update_one({"title": title, "owner": owner}, {"$set": project})
            return {"status": "success"}
        
    def leave_project(self, title, owner, participant):
        projects = self.get_projects_database()
        project = projects.find_one({"title": title, "owner": owner})
        if participant not in project["participants"]:
            raise Exception("Participant does not exist")
        else:
            project["participants"].remove(participant)
            projects.update_one({"title": title, "owner": owner}, {"$set": project})
            return {"status": "success"}
        
    def update_project(self, id, project):
        projects = self.get_projects_database()
        projects.update_one({"_id": id}, {"$set": project})

    def search_project(self, query):
        projects = self.get_projects_database()
        return projects.find(query)
    
    def get_project_id(self, title, owner):
        projects = self.get_projects_database()
        return projects.find_one({"title": title, "owner": owner})
    
    def delete_project(self, title, owner):
        projects = self.get_projects_database()
        projects.delete_one({"title": title, "owner": owner})

    def list_my_projects(self, owner_email):
        projects = self.get_projects_database()
        return projects.find({"owner": owner_email})
    
    def list_projects_participants(self, participant):
        projects = self.get_projects_database()
        return projects.find({"participants": participant})
    
    def list_public_projects(self):
        projects = self.get_projects_database()
        return projects.find({"project_type": "public"})
    
    def add_fund_to_project(self, title, owner, amount):
        projects = self.get_projects_database()
        project = projects.find_one({"title": title, "owner": owner})
        project["budget"] += amount
        user = User()
        user.decrease_balance(owner, amount)
        projects.update_one({"title": title, "owner": owner}, {"$set": project})
        return {"status": "success"}
    
    def verify_project(self, title, owner):
        projects = self.get_projects_database()
        project = projects.find_one({"title": title, "owner": owner})
        if project["end_date"] < str(datetime.now()):
            project["is_active"] = False
            projects.update_one({"title": title, "owner": owner}, {"$set": project})
            return {"status": "success"}
    
    def set_project_salary(self, title, owner, salary):
        projects = self.get_projects_database()
        project = projects.find_one({"title": title, "owner": owner})
        project["salary"] = salary
        projects.update_one({"title": title, "owner": owner}, {"$set": project})
        return {"status": "success"}
    
    def get_project_number_of_expected_participants(self, title, owner):
        projects = self.get_projects_database()
        project = projects.find_one({"title": title, "owner": owner})
        project_budget = project["budget"]
        project_salary = project["salary"]
        return project_budget // project_salary
    
    def get_project_participants(self, title, owner):
        projects = self.get_projects_database()
        project = projects.find_one({"title": title, "owner": owner})
        return project["participants"]
    
    def add_participant(self, title, owner, participant):
        projects = self.get_projects_database()
        project = projects.find_one({"title": title, "owner": owner})
        expected_number_of_participants = self.get_project_number_of_expected_participants(title, owner)
        if len(project["participants"]) >= expected_number_of_participants:
            raise Exception("Project is full")
        if participant in project["participants"]:
            raise Exception("Participant already exists")
        else:
            project["participants"].append(participant)
            projects.update_one({"title": title, "owner": owner}, {"$set": project})
            return {"status": "success"}
        
class Transaction:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))

    def ping(self):
        try:
            self.client.admin.command("ping")
            return True
        except Exception as e:
            return False
        
    def get_transactions_database(self):
        return self.client["labcoin"]["transactions"]
    
    def insert_transaction(self, transaction: TransactionInfo):
        transactions = self.get_transactions_database()
        if transactions.find_one({"transaction_id": transaction["transaction_id"]}):
            raise Exception("Transaction already exists")
        else:
            transactions.insert_one(transaction.to_dict())

    def search_transaction(self, query):
        transactions = self.get_transactions_database()
        return transactions.find(query)
    
    def get_transactions(self, seller_id, buyer_id, project_id):
        transactions = self.get_transactions_database()
        return transactions.find({"seller_id": seller_id, "buyer_id": buyer_id, "project_id": project_id})
    
    def find_transaction(self, transaction_id):
        transactions = self.get_transactions_database()
        return transactions.find_one({"transaction_id": transaction_id})
    
    def pay_helper(self, transaction: TransactionInfo): 
        try:
            userdb = User()
            projectdb = Project()
            project = projectdb.get_project(transaction.project_id)
            buyer = userdb.get_user_by_id(transaction.buyer_id)

    
            if transaction.project_id in buyer["projects"]:
                if project["budget"] < transaction.amount:
                    raise Exception("Seller does not have enough balance")
                else:
                    buyer["budget"] += transaction.amount
                    project["budget"] -= transaction.amount
                    userdb.update_user(buyer.email, buyer)
                    projectdb.update_project(transaction.project_id, project)
                    return {"status": "success"}
            else: 
                raise Exception("Buyer is not a participant of the project")
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def pay(self, transaction: TransactionInfo):
        """
        Pay for a project with a transaction

        Args:
            TransactionInfo: Transaction information. Includes: 
            transaction_id (str): Transaction ID
            project_id (str): Project ID
            seller_id (str): Seller ID
            buyer_id (str): Buyer ID
            amount (float): Amount to pay
            valid_until (str): Valid duration. After this, transaction won't be accepted (default: 30 days from now)
        
        """
        try:
            transactions = self.get_transactions_database()
            survey = Survey()
            survey_status  = survey.verify_survey(transaction.seller_id, transaction.buyer_id, transaction.project_id)
            if survey_status:
                transactions.insert_one(transaction)
                self.pay_helper(transaction)
                if self.find_transaction(transaction.transaction_id):
                    raise Exception("Transaction already exists")
                else:
                    self.insert_transaction(transaction)
                return {"status": "success"}
            else:
                raise Exception("Survey is not verified")
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
    def delete_transaction(self, transaction_id):
        transactions = self.get_transactions_database()
        transactions.delete_one({"transaction_id": transaction_id})


class Survey:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))

    def ping(self):
        try:
            self.client.admin.command("ping")
            return True
        except Exception as e:
            return False
        
    def get_surveys_database(self):
        return self.client["labcoin"]["surveys"]
    
    def insert_survey(self, survey: SurveyInfo):
        surveys = self.get_surveys_database()
        if surveys.find_one({"seller_id": survey.seller_id, "buyer_id": survey.buyer_id, "project_id": survey.project_id}):
            raise Exception("Survey already exists")
        else:
            surveys.insert_one(survey.to_dict())
            return {"status": "success"}

    def get_survey_content(self, seller_id, buyer_id, project_id):
        surveys = self.get_surveys_database()
        survey = surveys.find_one({"seller_id": seller_id, "buyer_id": buyer_id, "project_id": project_id})

        if survey:
            return survey
        else:
            raise Exception("Survey does not exist")
        
    def get_survey(self, seller_id, buyer_id, project_id):
        surveys = self.get_surveys_database()
        return surveys.find_one({"seller_id": seller_id, "buyer_id": buyer_id, "project_id": project_id})


    def accept_survey(self, seller_id, buyer_id, project_id, content, answers):
        if self.get_survey(seller_id, buyer_id, project_id):
            if self.verify_survey(seller_id, buyer_id, project_id):
                survey = SurveyInfo(seller_id, buyer_id, project_id, content, answers, True)
                self.insert_survey(survey.to_dict())
                return {"status": "success"}
            else:
                raise Exception("Survey is not completed")
        else:
            raise Exception("Survey does not exist")
        
    def get_survey_content(self, seller_id, buyer_id, project_id):
        survey = self.get_survey(seller_id, buyer_id, project_id)
        return survey["content"]
    
    def get_survey_answers(self, seller_id, buyer_id, project_id):
        survey = self.get_survey(seller_id, buyer_id, project_id)
        return survey["answers"]
    
    def get_survey_status(self, seller_id, buyer_id, project_id):
        survey = self.get_survey(seller_id, buyer_id, project_id)
        return survey["is_accepted"]
    
    def verify_survey(self, seller_id, buyer_id, project_id):
        survey = self.get_survey(seller_id, buyer_id, project_id)
        survey_answers = survey["answers"]
        return all(answer != "" for answer in survey_answers)
    
    def delete_survey(self, seller_id, buyer_id, project_id):
        surveys = self.get_surveys_database()
        try:
            if surveys.find_one({"seller_id": seller_id, "buyer_id": buyer_id, "project_id": project_id}):
                surveys.delete_one({"seller_id": seller_id, "buyer_id": buyer_id, "project_id": project_id})
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
        
    def answer_survey(self, seller_id, buyer_id, project_id, answers):
        survey = self.get_survey(seller_id, buyer_id, project_id)
        survey["answers"] = answers
        self.insert_survey(survey)
        return {"status": "success"}
    
    def give_feedback(self, seller_id, buyer_id, project_id, feedback):
        survey = self.get_survey(seller_id, buyer_id, project_id)
        survey["feedback"] = feedback
        self.insert_survey(survey)
        return {"status": "success"}
    