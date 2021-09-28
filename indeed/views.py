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



def show(request):
    job_list = find_jobs_from("Indeed", "software", "india", ["titles", "links"], filename="results.xls")
    if request.method == "POST":
        print(request.POST["query"])
        job_title = request.POST["query"]
        job_list = find_jobs_from("Indeed", job_title, "india", ["titles"], filename="results.xls")
        job_list["query"] = request.POST["query"]
    return render(request, "home.html", job_list)


def find_jobs_from(website, job_title, location, desired_characs, filename="results.xls"):
    
    if website == 'Indeed':
        job_soup = load_indeed_jobs_div(job_title, location)
        jobs_list, num_listings = extract_job_information_indeed(job_soup, desired_characs)
    
    
    save_jobs_to_excel(jobs_list, filename)
    
    print('{} new job postings retrieved from {}. Stored in {}.'.format(num_listings, 
                                                                        website, filename))
    return jobs_list
    



def save_jobs_to_excel(jobs_list, filename):
    jobs = pd.DataFrame(jobs_list)
    jobs.to_excel(filename)




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
    extracted_info = []
    
    for job_elem in job_elems:
        row = {}
        row["title"] = extract_job_title_indeed(job_elem)
        row["link"] = extract_link_indeed(job_elem)
        row["company"] = extract_company_indeed(job_elem)
        row["salary"] = extract_salary_indeed(job_elem)

        extracted_info.append(row)
    
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
    
    
    
    # for j in range(len(cols)):
    #     jobs_list[cols[j]] = extracted_info[j]
    
    # jobs_list = zip(jobs_list["titles"], jobs_list["links"])
    num_listings = 0#len(extracted_info[0])
    
    return jobs_list, num_listings


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
