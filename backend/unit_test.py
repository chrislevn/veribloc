import pytest
from database import User, Project, Transaction, Survey
from objects import UserInfo, ProjectInfo, TransactionInfo, SurveyInfo
from datetime import datetime, timedelta


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

    print(project_id)

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
    assert survey.insert_survey(survey_info) == {"status": "success"}

    # Participant read survey
    read_survey = survey.get_survey_content(seller_id=str(seller_id), buyer_id=str(buyer_id), project_id=str(project_id))
    assert read_survey != None

    # Participant answers survey
    answers = ["Answer 1", "Answer 2"]
    survey.answer_survey(seller_id=str(seller_id), buyer_id=str(buyer_id), project_id=str(project_id), answers=answers)

    # Owner/system verifies survey
    verify_status = survey.verify_survey(survey_info)
    assert verify_status == True

    # Owner/system gives feedback
    feedback = "Good job!"
    survey.give_feedback(seller_id=str(seller_id), buyer_id=str(buyer_id), project_id=str(project_id), feedback=feedback)

    # Owner/system pays participant
    if verify_status:
        transaction = Transaction()
        transaction_info = TransactionInfo(
            transaction_id="123",
            project_id="Project 1",
            seller_id=seller_id,
            buyer_id=buyer_id,
            amount=10.0,
        )
        transaction.pay(transaction_info)

    # Clean up
    transaction.delete_transaction(transaction_info.transaction_id)
    user.delete_user_by_email(seller_info.email)
    user.delete_user_by_email(buyer_info.email)
    project.delete_project("Project 1", seller_info.email)


if __name__ == "__main__":
    pytest.main(["-s", "unit_test.py"])
