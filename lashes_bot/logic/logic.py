from db.models.models import Master, Service
from config.config import config

import requests
import re


# Инициализируем url и headers
url = "https://api.yclients.com/api/v1/book_staff/550726"

headers = {
    "Accept": "application/vnd.yclients.v2+json",
    "accept-language": "ru-RU",
    "authorization": f"Bearer {config.yclients_token_partner}",
    "baggage": "sentry-environment=live,sentry-release=225160.a54b5b28,sentry-public_key=0007a4d5532549699d3854b2edb11b63,sentry-trace_id=be26941c15c64281bba1d11085cfa04c,sentry-sampled=false",
    # 'cookie': 'yc_utm_campaign=; yc_utm_content=; yc_utm_term=; yc_utm_click_id=; yc_utm_source=www.yandex.ru; yc_utm_medium=referral; yc_referral_url=https%3A%2F%2Fwww.yandex.ru%2F; original_utm_referer_v2=(not_set); tmr_lvid=d21edc0346d62ca0e788f4615df6402b; tmr_lvidTS=1719040219822; _ym_uid=1719040221369778136; _ym_d=1719040221; landing_lang=ru; analytics-udid=sNEZDjTgnWQh7a2urhD4R8bB0yEMPA1mmj6qNtGm; _ga_4Z5R7DZBLZ=GS1.2.1719222722.2.0.1719222722.60.0.0; _ga_CZ0CKD8R74=GS1.1.1719222720.3.0.1719222730.0.0.0; _ga=GA1.1.2028114192.1719040219; _cfuvid=sir0HVaGrZ3M08GsGbnfzdeE0FHhgXWgdonmv9S2bRA-1725276900979-0.0.1.1-604800000; lang=1; ycl_language_id=1; erp_language_id=1; _gcl_au=1.1.124876351.1730372747; original_utm_source_v2=www.yandex.ru; original_utm_medium_v2=organic; original_utm_campaign_v2=(not_set); original_utm_term_v2=(not_set); _ga_P2LM7D8KSM=GS1.1.1730372748.6.1.1730372950.60.0.0; _ga_X3P164PV59=GS1.1.1730372748.3.1.1730372950.60.0.0; spid=1730373076799_c9d56d327325e5eee42fa3a4a0ffd98c_lvuepjluwlhg3vpr; spsc=1730373207657_97c63346c230fe2593533a6d26d3f958_e6cfb3ea8f0a0fa28cc6ebefdcae8ea5; app_service_group=0; _ym_isad=2; _ym_visorc=b; __ga_track__=GS1.1-2.1664391493.1.1.1664391604.0.0.0.OUdUaDFNN1k0TXVQMXRTWG5xT2lxS3VtcXJCNms1N0o4QT09; tracking-index=859',
    "priority": "u=1, i",
    "referer": "https://n582759.yclients.com/company/550726/create-record/record?o=m1597921s8125709d2401121245",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sentry-trace": "be26941c15c64281bba1d11085cfa04c-a2a70d03459e2820-0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "x-app-signature": "",
    "X-App-Validation-Token": f"92f9d2dc4d116087c877aeb46140afcf",
    "x-yclients-application-action": "company.new-success-order",
    "x-yclients-application-name": "client.booking",
    "x-yclients-application-platform": "angular-17.3.0",
    "x-yclients-application-version": "225160.a54b5b28",
}

# Выполняем гет запрос
r = requests.get(url=url, headers=headers)


# Функция парсинга мастеров
def pars_master() -> dict:
    """Добавляет мастеров с сайта yclients"""
    masters: dict[int : Master()] = {}
    for i in r.json()["data"]:
        master = Master()
        if i["bookable"]:
            master.id = i["id"]
            master.name = i["name"]
            master.title = (
                re.sub("<[^<]+?>", "", i["information"])
                .replace("&nbsp", " ")
                .replace("&quot;", " ")
            )
            master.foto = i["avatar"]
            master.rating = i["rating"]
            master.massages_ids = pars_services_mast(i["id"])
            masters.update({master.id: master})

    return dict(sorted(masters.items(), key=lambda x: x[1].rating))


# Функция парсинга массажей для конкретного мастера
def pars_services_mast(master_id: str) -> dict:
    """Добавляет массажи для конкретного мастера с сайта yclients"""
    url = f"https://api.yclients.com/api/v1/book_services/550726?staff_id={master_id}"

    r = requests.get(url=url, headers=headers)
    service_id = []
    for i in r.json()["data"]["services"]:
        service_id.append(i["id"])
    return service_id


# Функция парсинга услуг
def pars_services() -> dict:
    """Добавляет услуги с сайта yclients"""
    url = "https://api.yclients.com/api/v1/book_services/550726"
    r = requests.get(url=url, headers=headers)
    services: dict[int : Service()] = {}
    for mass in r.json()["data"]["services"]:
        service = Service()
        service.id = mass["id"]
        service.name = mass["title"]
        service.description = mass["comment"]
        service.price = mass["price_min"]
        service.foto = mass["image"]
        services.update({service.id: service})

    return services


# Функция парсинга времени для записи
def pars_time(master_id: str, service_id: str, date: str) -> dict:
    """Выводит время для записи для конкретного мастера, услуги и на определённый день"""
    url = f"https://api.yclients.com/api/v1/book_times/550726/{master_id}/{date}?service_ids={service_id}"

    r = requests.get(url=url, headers=headers)
    return r.json()["data"]


# Функция парсинга даты для записи
def pars_date(master_id: str, service_id: str) -> dict:
    """Выводит даты для записи для конкретного мастера и услуги"""
    url = f"https://api.yclients.com/api/v1/book_dates/550726?staff_id={master_id}&service_ids={service_id}"
    r = requests.get(url=url, headers=headers)
    return r.json()["data"]


# Функция записи
def to_booking(json: dict):
    """Создаёт запись на сеанс"""
    r = requests.post(
        url="https://api.yclients.com/api/v1/book_record/550726",
        json=json,
        headers=headers,
    )
    print(r.text)
    return r.status_code


services = pars_services()

masters = pars_master()


# Функция поиска мастера по id
def search_master_to_id(id: int) -> Master:
    """По id находит нужного мастера"""

    for master in masters.values():
        if master.id == id:
            return master


# Функция поиска услуги по id
def search_service_to_id(id: int) -> Service:
    """По id находит нужную услугу"""

    for service in services.values():
        if service.id == id:
            return service
