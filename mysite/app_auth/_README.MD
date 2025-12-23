# Приложение профиль пользователя.

class MyProfile(model.Model)

settings.py
```python
# AUTH_USER_MODEL = 'app_auth.MyProfile'
LOGIN_URL = 'app_auth:login'
LOGIN_REDIRECT_URL = 'app_auth:profile'
LOGOUT_REDIRECT_URL = 'app_auth:login'
```