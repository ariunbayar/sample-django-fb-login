# Sample django base Facebook login

This project implements facebook login.


# How to setup

Before you install, make sure you have python3 installed.

1. Install requirements:

```
pip install -r requirements.txt
cp main/local_settings.py.def main/local_settings.py
```

2. Configure variables in `main/local_settings.py`

3. Run migrations:

```
python manage.py migrate
```


# Reference

FB doc for developers: https://developers.facebook.com/docs/facebook-login
