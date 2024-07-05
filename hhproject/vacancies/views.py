from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.urls import reverse
import requests

# Create your views here.
from django.db import connection

def get_data_from_table(experience):
    data = []

    with connection.cursor() as cursor:
        request1 = "SELECT * FROM Вакансия"
        request2 = "SELECT count(job) FROM Вакансия"

        if experience:
            request1 = f"SELECT * FROM Вакансия WHERE experience='{experience}'"
            request2 = f"SELECT count(job) FROM Вакансия WHERE experience='{experience}'"

        cursor.execute(request1)
        vacancies = cursor.fetchall()

        cursor.execute(request2)
        quantity = cursor.fetchall()

        data.append(vacancies)
        data.append(quantity)

        cursor.execute("DELETE FROM Вакансия")

    return data


def news_home(request):
    search_query = ''
    search_region = ''
    experience = ''
    data = ''

    if request.method == 'POST':
        # Получаем данные из формы
        search_query = request.POST.get('search')
        search_region = request.POST.get('region')
        experience = request.POST.get('experience')

        if not search_query:
            home_url = reverse('home')
            return redirect(home_url)

        get_info_from_hh(search_query, search_region)
        data = get_data_from_table(experience)

    return render(request, 'vacancies/vacancies_list.html', {'data': data[0], 'quantity': data[1][0]})


def get_region(info, search_query, search_region):
    if info['pages'] <= 20:
        quantity = info['pages'] - 1
    else:
        quantity = 19

    page = 1
    data = []

    while page <= quantity:
        url = f'https://api.hh.ru/vacancies?clusters=true&only_with_salary=true&enable_snippets=true&st=searchVacancy&text={search_query}&search_field=name&per_page=100&page={page}&area={search_region}'

        data.append(requests.get(url).json())
        page += 1

    return data

def get_info_from_hh(search_query, search_region):
    url = f'https://api.hh.ru/vacancies?clusters=true&only_with_salary=true&enable_snippets=true&st=searchVacancy&text={search_query}&search_field=name&per_page=100&area={search_region}'

    info = requests.get(url).json()
    result = get_region(info, search_query, search_region)

    for j in range(len(result)):
        for i in range(len(result[j]['items'])):
            id_vacancy = result[j]['items'][i]['id']
            job = str(result[j]['items'][i]['name']).replace("'", "").replace("<highlighttext>", "").replace("</highlighttext>", "")
            city = result[j]['items'][i]['area']['name']

            salary_from = "-"

            if result[j]['items'][i]['salary']['from'] is not None:
                salary_from = result[j]['items'][i]['salary']['from']
            
            salary_to = "-"

            if result[j]['items'][i]['salary']['to'] is not None:
                salary_to = result[j]['items'][i]['salary']['to']

            address = "Точный адрес не указан"

            if result[j]['items'][i]['address'] is not None:
                address = result[j]['items'][i]['address']['raw']

            requirement = str(result[j]['items'][i]['snippet']['requirement']).replace("'", "").replace("<highlighttext>", "").replace("</highlighttext>", "")
            responsibility = str(result[j]['items'][i]['snippet']['responsibility']).replace("'", "").replace("<highlighttext>", "").replace("</highlighttext>", "")
            professional_roles = str(result[j]['items'][i]['professional_roles'][0]['name']).replace("'", "").replace("<highlighttext>", "").replace("</highlighttext>", "")
            experience = str(result[j]['items'][i]['experience']['name']).replace("'", "").replace("<highlighttext>", "").replace("</highlighttext>", "")

            action = f"INSERT INTO Вакансия (id_vacancy, job, city, salary_from, salary_to, address, requirement, responsibility, professional_roles, experience) VALUES ({id_vacancy}, '{job}', '{city}', '{salary_from}', '{salary_to}', '{address}', '{requirement}', '{responsibility}', '{professional_roles}', '{experience}')"

            try:
                with connection.cursor() as cursor:
                    cursor.execute(action)
            except:
                continue

    #return profession

