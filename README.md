- python version 3.9
- install docker
- run initialization.sh to start docker container
- localhost:56733/echo
```commandline
request:
{
    "data": "base64_string"
}

response:
{
    "id": "1234 567890",
    "surname": "Иванов",
    "name": "Иван",
    "secondname": "Иванович",
    "bdate": "11.11.1999",
    "gender": "Муж" 
}
```

- Alternarive runapp
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/app.py
```