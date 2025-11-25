# Приложение профиль пользователя.

class MyProfile(model.Model)

settings.py
```python
# AUTH_USER_MODEL = 'my_auth.MyProfile'
LOGIN_URL = 'my_auth:login'
LOGIN_REDIRECT_URL = 'my_auth:profile'
LOGOUT_REDIRECT_URL = 'my_auth:login'
```