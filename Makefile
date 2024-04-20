install: 
	cd backend && pip3 install --upgrade pip && pip3 install -r requirements.txt
	
run_backend_local: 
	cd backend && uvicorn app:app --reload

test: 
	cd backend && python3 unit_test.py