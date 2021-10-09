import os
import urllib

import pandas as pd
import requests
import selenium
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from django.http import JsonResponse

import io
from django.core.files.images import ImageFile
from .models import Plot
from django.http import FileResponse
from django.shortcuts import get_object_or_404


def show(request):
    # plot = Plot.objects.filter(user_id=request.user.id).first()
    # if plot:
    #     if plot[0].figure:
    #         plot[0].figure.delete()
    # if plot:
    #     plot.delete()

    if request.method == "POST":
        job_title = request.POST["query"]
        job_list = find_jobs_from(request, "Indeed", job_title, "india", ["titles"], filename="results.csv")
        job_list["query"] = job_title
        return JsonResponse(job_list) #render(request, "home.html", job_list)
    
    return render(request, "home.html")


def plot_image(request):
    img = open('media/figures/'+request.user.username+'.png', 'rb')

    response = FileResponse(img)

    return response


def find_jobs_from(request, website, job_title, location, desired_characs, filename="results.xls"):
    
    while(True):
        if website == 'Indeed':
            job_soup = load_indeed_jobs_div(job_title, location)
            jobs_list, num_listings, nums = extract_job_information_indeed(job_soup, desired_characs)

            if nums !=0:
                break
    
    
    save_jobs_to_excel(request, num_listings, filename)

    return jobs_list
    


def save_jobs_to_excel(request, jobs_list, filename):
    df = pd.DataFrame(jobs_list)

    

    # time = df['salaries'].str.split(expand = True)
    df["time"][df["time"] == "month"] = 1
    df["time"][df["time"] == "year"] = 12
    df["time"][df["time"] == "hour"] = 1/30 * 1/24
    df["time"][df["time"] == "week"] = 1/4
    df['salaries']= df['salaries'].astype(str).str.replace('₹','').str.replace(',','')
    
    df["salaries"] = df["salaries"].apply (pd.to_numeric, errors='coerce')
    df = df.dropna(axis=0, how='any')
    for i in df["salaries"]:
        print(i)

    df["salary"] = df["salaries"].astype(float)/df["time"].astype(float)
    df.drop(columns= ["salaries", "time"], inplace =True)

    salary_df = pd.DataFrame({'company':df["company"], 'salary':df["salary"]})
    ax = salary_df.plot(x='company', y='salary', kind='barh', figsize=(20, 10))

    # ax.figure.savefig("results.jpg")

    # response = HttpResponse(content_type='image/png')

    # ax.figure.savefig(response)

    figure = io.BytesIO()
    ax.figure.savefig(figure, format="png")
    content_file = ImageFile(figure)

    plot_instance = Plot(user=request.user)
    plot_instance.figure.save(str(request.user.username)+'.png', content_file)
    plot_instance.save()


def load_indeed_jobs_div(job_title, location):
    getVars = {'q' : job_title, 'l' : location, 'fromage' : 'last', 'sort' : 'date'}
    url = ('https://in.indeed.com/jobs?' + urllib.parse.urlencode(getVars))
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    job_soup = soup.find(id="resultsCol")
    return job_soup

def extract_job_information_indeed(job_soup, desired_characs):

    job_elems = job_soup.find_all('div', class_='jobsearch-SerpJobCard')
    
    cols = []
    titles, salaries,companies, time = [], [], [], []
    extracted_info = []
    tabular_info = []
    
    cols = ['titles','salaries','company','time']

    for job_elem in job_elems:
        row = {}
        row["title"] = extract_job_title_indeed(job_elem)[:20]
        row["link"] = extract_link_indeed(job_elem)
        row["company"] = extract_company_indeed(job_elem)[0:12]
        row["salary"] = extract_salary_indeed(job_elem)

        
        
        titles.append(row["title"])
        salaries.append(row["salary"].split()[0])
        time.append(row["salary"].split()[-1])
        companies.append(row["company"])

        

        extracted_info.append(row)
    
    tabular_info.append(titles)
    tabular_info.append(salaries)
    tabular_info.append(companies)
    tabular_info.append(time)

    print(len(tabular_info[0]))
    # if 'titles' in desired_characs:
    #     titles = []
    #     cols.append('titles')
    #     for job_elem in job_elems:
    #         titles.append(extract_job_title_indeed(job_elem))
    #     extracted_info.append(titles)                    
    
    # if 'companies' in desired_characs:
    #     companies = []
    #     cols.append('companies')
    #     for job_elem in job_elems:
    #         companies.append(extract_company_indeed(job_elem))
    #     extracted_info.append(companies)
    
    # if 'links' in desired_characs:
    #     links = []
    #     cols.append('links')
    #     for job_elem in job_elems:
    #         links.append(extract_link_indeed(job_elem))
    #     extracted_info.append(links)
    
    # if 'date_listed' in desired_characs:
    #     dates = []
    #     cols.append('date_listed')
    #     for job_elem in job_elems:
    #         dates.append(extract_date_indeed(job_elem))
    #     extracted_info.append(dates)

    jobs_list = {}
    jobs_list["extracted_info"] = extracted_info

    # i = 0
    # for job_elem in job_elems:
    #     jobs_list[i] = {"titles": extract_job_title_indeed(job_elem),"links": extract_link_indeed(job_elem)}
    #     i += 1
    
    
    jobs_table = {}
    for j in range(len(cols)):
        jobs_table[cols[j]] = tabular_info[j]
    
    
    num_listings = 0#len(extracted_info[0])
    
    return jobs_list, jobs_table, len(tabular_info[0])


def extract_job_title_indeed(job_elem):
    title_elem = job_elem.find('h2', class_='title')
    title = title_elem.text.strip()
    return title

def extract_company_indeed(job_elem):
    company_elem = job_elem.find('span', class_='company')
    company = company_elem.text.strip()
    return company

def extract_link_indeed(job_elem):
    link = job_elem.find('a')['href']
    link = 'https://in.indeed.com' + link
    return link

def extract_date_indeed(job_elem):
    date_elem = job_elem.find('span', class_='date')
    date = date_elem.text.strip()
    return date

def extract_salary_indeed(job_elem):
    salary_elem = job_elem.find('span', class_='salaryText')
    if salary_elem is None:
        salary = "NA"
    else:
        salary = salary_elem.text.strip()
    return salary


def initiate_driver(location_of_driver, browser):
    if browser == 'chrome':
        driver = webdriver.Chrome(executable_path=(location_of_driver + "/chromedriver"))
    elif browser == 'firefox':
        driver = webdriver.Firefox(executable_path=(location_of_driver + "/firefoxdriver"))
    elif browser == 'safari':
        driver = webdriver.Safari(executable_path=(location_of_driver + "/safaridriver"))
    elif browser == 'edge':
        driver = webdriver.Edge(executable_path=(location_of_driver + "/edgedriver"))
    return driver
