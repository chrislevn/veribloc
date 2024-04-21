import pytest
from database import User, Project, Transaction, Survey
from objects import UserInfo, ProjectInfo, TransactionInfo, SurveyInfo
from datetime import datetime, timedelta
import requests
import os

def test_ping_user_db():
    user = User()
    assert user.ping() == True


def test_ping_project_db():
    project = Project()
    assert project.ping() == True


def test_ping_transaction_db():
    transaction = Transaction()
    assert transaction.ping() == True


def test_ping_survey_db():
    survey = Survey()
    assert survey.ping() == True


def test_insert_user():
    user = User()
    user_info = UserInfo(
        first_name="John",
        last_name="Doe",
        email="john_doe@gmail.com",
        password="password123",
        projects=["Project 1", "Project 2"],
        participated_projects=["Project 3", "Project 4"],
        balance=100.0,
        payment={"method": "bitcoin", "amount": 50.0},
        institution="University of Toronto",
        is_active=True,
    )

    user.insert_user(user_info)
    user.delete_user_by_email("john_doe@gmail.com")


def test_create_project():
    project = Project()

    fake_project_info = ProjectInfo(
        title="Fake Project",
        description="This is a fake project",
        owner="Fake Owner",
        members=["Member 1", "Member 2"],
        participants=["Participant 1", "Participant 2"],
        is_active=True,
        start_date=str(datetime.now()),
        end_date=str(datetime.now() + timedelta(days=30)),
        budget=0.0,
        salary=0.0,
        project_type="public",
    )

    project.insert_project(fake_project_info)
    project.delete_project("Fake Project", "Fake Owner")


def test_integration():
    # Create fake users
    user = User()

    buyer_info = UserInfo(
        first_name="Jane",
        last_name="Doe",
        email="jane_doe@gmail.com",
        password="password321",
        projects=["Project 1", "Project 2"],
        institution="N/A",
        is_active=True,
        participated_projects=[],
        balance=100.0,
        payment={"method": "bitcoin", "amount": 50.0},
    )

    seller_info = UserInfo(
        first_name="John",
        last_name="Doe",
        email="john_doe@gmail.com",
        password="password123",
        institution="University of Toronto",
        projects=[""],
        is_active=True,
        participated_projects=["Project 1"],
        balance=100.0,
        payment={"method": "bitcoin", "amount": 50.0},
    )

    # Clean up if user already exists
    user.delete_user_by_email(buyer_info.email)
    user.delete_user_by_email(seller_info.email)

    assert user.insert_user(buyer_info) == {"status": "success"}
    buyer_id = user.get_user_id(buyer_info.email, buyer_info.password)
    assert user.insert_user(seller_info) == {"status": "success"}
    seller_id = user.get_user_id(seller_info.email, seller_info.password)

    # Seller add balance to account
    user.increase_balance(seller_info.email, 1000.0)

    # Create fake project
    project = Project()
    project_info = ProjectInfo(
        title="Project 1",
        description="This is a fake project",
        owner=seller_info.email,
        members=["Member 1", "Member 2"],
        participants=["Participant 1", "Participant 2"],
        is_active=True,
        project_type="public",
        start_date=str(datetime.now()),
        end_date=str(datetime.now() + timedelta(days=30)),
        budget=0.0,
        salary=10.0,
    )

    # clean up if project already exists
    project.delete_project(project_info.title, seller_info.email)
 
    assert project.insert_project(project_info) == {"status": "success"}
    project_id = project.get_project_id(project_info.title, seller_info.email)["_id"]

    # Seller adds budget to project
    project.add_fund_to_project(project_info.title, seller_info.email, 1000.0)

    # Fake owner creates project survey
    survey = Survey()

    survey_info = SurveyInfo(
        seller_id=str(seller_id),
        buyer_id=str(buyer_id),
        project_id=str(project_id),
        content="This is a survey",
        answers=[],
        is_accepted=False,
        feedback="",
    )

    # Fake participant joins project
    project.join_project(
        project_info.title, owner=seller_info.email, participant=buyer_info.email
    )

    # clean up if survey already exists
    survey.delete_survey(seller_id=str(seller_id), buyer_id=str(buyer_id), project_id=str(project_id))

    # System sends survey to participant    
    result_insert_survey = survey.insert_survey(survey_info)
    assert result_insert_survey == {"status": "success"}

    # Participant read survey
    read_survey = survey.get_survey_content(seller_id=str(seller_id), buyer_id=str(buyer_id), project_id=str(project_id))
    assert read_survey != None

    # Participant answers survey
    answers = ["Answer 1", "Answer 2"]
    survey.answer_survey(survey_info.seller_id, survey_info.buyer_id, survey_info.project_id, answers)

    # Owner/system verifies survey
    verify_status = survey.verify_survey(seller_id=str(seller_id), buyer_id=str(buyer_id), project_id=str(project_id))
    assert verify_status == True

    # Owner/system gives feedback
    feedback = "Good job!"
    survey.give_feedback(seller_id=str(seller_id), buyer_id=str(buyer_id), project_id=str(project_id), feedback=feedback)

    transaction = Transaction()
    transaction_info = TransactionInfo(
        project_id=str(project_id),
        seller_id=str(seller_id),
        buyer_id=str(buyer_id),
        amount=10.0,
    )
    # Owner/system pays participant
    if verify_status:
        transaction.pay(transaction_info)

    transaction_id = transaction.get_transaction_id(transaction_id.seller_id, transaction_id.buyer_id, transaction_id.project_id)

    # Clean up
    transaction.delete_transaction(transaction_info.transaction_id)
    user.delete_user_by_email(seller_info.email)
    user.delete_user_by_email(buyer_info.email)
    project.delete_project("Project 1", seller_info.email)
    survey.delete_survey(seller_id=str(seller_id), buyer_id=str(buyer_id), project_id=str(project_id))

def test_api_full():
    # Create fake users
    user = User()

    buyer_info = UserInfo(
        first_name="Jane",
        last_name="Doe",
        email="jane_doe@gmail.com",
        password="password321",
        projects=["Project 1", "Project 2"],
        institution="N/A",
        is_active=True,
        participated_projects=[],
        balance=100.0,
        payment={"method": "bitcoin", "amount": 50.0},
    )

    seller_info = UserInfo(
        first_name="John",
        last_name="Doe",
        email="john_doe@gmail.com",
        password="password123",
        institution="University of Toronto",
        projects=[""],
        is_active=True,
        participated_projects=["Project 1"],
        balance=100.0,
        payment={"method": "bitcoin", "amount": 50.0},
    )
    URL = os.getenv("URL")
    # Clean up if user already exists
    requests.post(URL + "/delete_user", json={"email": buyer_info.email})
    requests.post(URL + "/delete_user", json={"email": seller_info.email})

    requests.post(URL + "/signup", json=buyer_info.to_dict())
    buyer_id = requests.post(URL + "/get_user_id", json={"email": buyer_info.email, "password": buyer_info.password}).json()
    requests.post(URL + "/signup", json=seller_info.to_dict())
    seller_id = requests.post(URL + "/get_user_id", json={"email": seller_info.email, "password": seller_info.password}).json()

    # Seller add balance to account
    requests.post(URL + "/increase_balance", json={"email": seller_info.email, "amount": 1000.0})

    # Create fake project
    project = Project()
    project_info = ProjectInfo(
        title="Project 1",
        description="This is a fake project",
        owner=seller_info.email,
        members=["Member 1", "Member 2"],
        participants=["Participant 1", "Participant 2"],
        is_active=True,
        project_type="public",
        start_date=str(datetime.now()),
        end_date=str(datetime.now() + timedelta(days=30)),
        budget=0.0,
        salary=10.0,
    )

    # clean up if project already exists
    requests.post(URL + "/delete_project", json={"title": project_info.title, "owner_email": seller_info.email})

    requests.post(URL + "/create_project", json=project_info.to_dict())
    project_id = requests.post(URL + "/get_project_id", json={"title": project_info.title, "owner": seller_info.email}).raw

    # Seller adds budget to project
    requests.post(URL + "/add_fund_to_project", json={"title": project_info.title, "owner": seller_info.email, "amount": 1000.0})

    # Fake owner creates project survey
    survey = Survey()

    survey_info = SurveyInfo(
        seller_id=str(seller_id),
        buyer_id=str(buyer_id),
        project_id=str(project_id),
        content="This is a survey",
        answers=[],
        is_accepted=False,
        feedback="",
    )

    # Fake participant joins project
    requests.post(URL + "/join_project", json={"title": project_info.title, "owner": seller_info.email, "participant": buyer_info.email})

    # clean up if survey already exists
    requests.post(URL + "/delete_survey", json={"seller_id": str(seller_id), "buyer_id": str(buyer_id), "project_id": str(project_id)})
    # System sends survey to participant
    requests.post(URL + "/create_survey", json=survey_info.to_dict()).json()

    # Participant read survey
    read_survey = requests.post(URL + "/get_survey_content", json={"seller_id": str(seller_id), "buyer_id": str(buyer_id), "project_id": str(project_id)}).json()

    # Participant answers survey
    answers = ["Answer 1", "Answer 2"]
    requests.post(URL + "/answer_survey", json={"seller_id": survey_info.seller_id, "buyer_id": survey_info.buyer_id, "project_id": survey_info.project_id, "answers": answers})

    # Owner/system verifies survey
    verify_status = requests.post(URL + "/verify_survey", json={"seller_id": str(seller_id), "buyer_id": str(buyer_id), "project_id": str(project_id)})

    # Owner/system gives feedback
    feedback = "Good job!"
    requests.post(URL + "/give_feedback", json={"seller_id": str(seller_id), "buyer_id": str(buyer_id), "project_id": str(project_id), "feedback": feedback})

    # Owner/system pays participant

    transaction = Transaction()
    transaction_info = TransactionInfo(
        project_id="Project 1",
        seller_id=str(seller_id),
        buyer_id=str(buyer_id),
        amount=10.0,
    )

    if verify_status:
        requests.post(URL + "/pay", json=transaction_info.to_dict())

    transaction_id = requests.post(URL + "/get_transaction_id", json={"seller_id": transaction_info.seller_id, "buyer_id": transaction_info.buyer_id, "project_id": transaction_info.project_id}).json()
    # Clean up
    requests.post(URL + "/delete_transaction", json={"transaction_id": transaction_info.transaction_id})
    requests.post(URL + "/delete_user", json={"email": seller_info.email})
    requests.post(URL + "/delete_user", json={"email": buyer_info.email})
    requests.post(URL + "/delete_project", json={"title": project_info.title, "owner_email": seller_info.email})



if __name__ == "__main__":
    pytest.main(["-s", "unit_test.py"])
