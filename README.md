# Prerequisites
- Python 3
# How to run
Install dependencies
```
pip install -r requirements.txt
```
Start server on port 5500:
```
python app.py
```
Visit http://localhost:5500.

# Introduction
This tool consists of 3 functionalities:
1. Create sample project from an existing one. You can randomly select a subset of documents from an existing project to test the quality of the labelled data.
2. Evaluate the quality of the labelled data. The data after being labelled and corrected are then go through this function to automatically calculate various metrics such as accuracy, precision and recall.
3. Download data to excel. Though you can change the output format to what ever you like.

Function #2 currently only work for document classification (i.e. intent), which means that if you want to evaluate the quality of entities, you must change this code.

The credential to connect to the server is hard-coded, so remember to change this if you change the server ip or admin password.
