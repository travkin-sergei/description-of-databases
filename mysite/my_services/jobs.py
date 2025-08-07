def check_all_links_job():
    import requests
    from django.utils import timezone
    from my_services.models import DimLink

    for link in DimLink.objects.filter(is_active=True):
        try:
            response = requests.head(link.link, timeout=5)
            link.status_code = response.status_code
        except Exception as e:
            print(f"Ошибка при проверке {link.link}: {e}")
            link.status_code = None

        link.last_checked = timezone.now()
        link.save()

    print("Проверка завершена.")

