from django.contrib.sessions.models import Session
from django.utils import timezone

def count_authenticated_sessions():
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_ids = []

    for session in active_sessions:
        data = session.get_decoded()
        user_id = data.get('_auth_user_id')
        if user_id:
            user_ids.append(user_id)

    unique_user_ids = set(user_ids)
    return len(unique_user_ids)
