Mini wallet installation

1. Create python3 environment and run the environment, please make sure you have python3 installed on your server
```
python3 -m venv wallet_env
source wallet_env/bin/activate
```

2. Install dependencies from requirements.txt and wait until it finish
```
pip install -r requirements.txt
```

3. created PostgreSQL database and `.env` file inside the project to configure the database

4. Before we run the app, run the following command to migrate the database
```
python manage.py migrate
```

5. Then we can run the server using command below
```
python manage.py runserver
```
