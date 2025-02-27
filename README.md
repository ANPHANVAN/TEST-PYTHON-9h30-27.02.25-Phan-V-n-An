# TEST-PYTHON-9h30-27.02.25-Phan-V-n-An


## setip
pip install -r requirements.txt
python app.py


curl -X POST -F "file=@sales_data.csv" http://127.0.0.1:5000/upload/
http://127.0.0.1:5000/sales/?start_date=2024-01-01&end_date=2024-02-01&region=USA&product=Laptop
