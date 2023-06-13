import os
import uuid
import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import json

projectsData = []
projectTypes = {}

financesData = []
financeTypes = {}

groupsData = []

milestonesData = []
externalIDs = {}

options = Options()
#options.headless = True
driver = webdriver.Firefox(options = options) #Pro vypnuti logovani nastavit parametr => service_log_path = os.devnull
driver.get("https://vav.unob.cz/auth/login")


def login():
    #Nacteni prihlasovacich udaju z .env
    load_dotenv()
    username = os.getenv("UNAME")
    password = os.getenv("PASSWD")

    #Prihlaseni do systemu
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.NAME, "login").click()


def checkAndAssingType(typesDict, scrapedType):
    if scrapedType in typesDict:
        return typesDict[scrapedType]
    else:
        typesDict[scrapedType] = str(uuid.uuid4())
        return typesDict[scrapedType]


def scrapeProjectData():
    projectData = {}  

    projectData["ID"] =  str(uuid.uuid4())
    projectData["name"] = driver.find_element(By.XPATH, "//table[1]/tbody/tr[1]/td[2]").text

    startYear = driver.find_element(By.XPATH, "//table[1]/tbody/tr[7]/td[2]").text[:4]
    if(startYear[0].isdigit()):
        projectData["startdate"] = str(datetime.datetime(int(startYear), 1, 1, 0, 0))
    else:
        projectData["startdate"] = "Neuvedeno"

    endYear = driver.find_element(By.XPATH, "//table[1]/tbody/tr[8]/td[2]").text[:4]
    if(endYear[0].isdigit()):
        projectData["enddate"] = str(datetime.datetime(int(endYear), 1, 1, 0, 0))
    else:
        projectData["enddate"] = "Neuvedeno"

    projectType = driver.find_element(By.XPATH, "//table[1]/tbody/tr[5]/td[2]").text
    projectData["type_id"] = checkAndAssingType(projectTypes, projectType)

    projectData["group_id"] = scrapeGroupData(projectData["ID"])

    #Prirazeni projectID k external ID code
    externalIDs[projectData["ID"]] = driver.find_element(By.XPATH, "//table[1]/tbody/tr[3]/td[2]").text 

    return projectData


def scrapeGroupData(projectID):
    groupData = {}
    solvers = []

    groupData["ID"] = str(uuid.uuid4())
    groupData["project_id"] = projectID

    groupTableXPATH = "//h2[contains(text(), 'Projektový/záměrový tým')]/following-sibling::table[1]/tbody"
    rows = driver.find_elements(By.XPATH, groupTableXPATH + "/tr")

    if len(rows) == 1:
        singleSolver = {}

        singleSolver["role"] = driver.find_element(By.XPATH, groupTableXPATH + "/tr[1]/td[1]").text
        singleSolver["name"] = driver.find_element(By.XPATH,  groupTableXPATH + "/tr[1]/td[2]").text

        if (singleSolver["name"] != "Řešitelé nejsou uvedeni."):
                singleSolver["vavID"] = driver.find_element(By.XPATH, groupTableXPATH + "/tr[1]/td[2]/a").get_attribute("href")[-6:]
        else:
                singleSolver["vavID"] = " " 

        solvers.append(singleSolver)
                
    else:
        for i in range(2, len(rows) + 1):
            singleSolver = {}

            singleSolver["role"] = driver.find_element(By.XPATH, groupTableXPATH + f"/tr[{i}]/td[1]").text
            singleSolver["name"] = driver.find_element(By.XPATH, groupTableXPATH + f"/tr[{i}]/td[2]").text

            if (singleSolver["name"] != "Řešitelé nejsou uvedeni."):
                singleSolver["vavID"] = driver.find_element(By.XPATH, groupTableXPATH + f"/tr[{i}]/td[2]/a").get_attribute("href")[-6:]
            else:
                singleSolver["vavID"] = " "         

            solvers.append(singleSolver)

    groupData["solvers"] = solvers

    groupsData.append(groupData)

    return groupData["ID"]


def generateProjectMilestone(scrapedProjectData):
    milestoneData = {}

    milestoneData["ID"] =  str(uuid.uuid4())
    milestoneData["name"] = "Placeholder Milestone"
    milestoneData["startdate"] = scrapedProjectData["startdate"]
    milestoneData["enddate"] = scrapedProjectData["enddate"]
    milestoneData["project_id"] = scrapedProjectData["ID"]

    return milestoneData


def scrapeFinanceData(scrapedProjectData, requestsURL):
    financeData = []
    maxPage = driver.find_element(By.XPATH, "//div[@id='main-appmenu']/div[2]/div[1]/strong").text[1:-1]

    for i in range(0, int(maxPage), 25):
        driver.get(requestsURL+f"/{i}")
    
        tableLength = len(driver.find_elements(By.TAG_NAME, "tr"))    
    
        for k in range(2, tableLength + 1): 
            singleFinance = {}

            singleFinance["ID"] = str(uuid.uuid4())
            singleFinance["name"] = driver.find_element(By.XPATH, f"//table[@id='main_table']/tbody/tr[{k}]/td[4]").text
            singleFinance["amount"] = driver.find_element(By.XPATH, f"//table[@id='main_table']/tbody/tr[{k}]/td[5]").text
            
            singleFinance["project_id"] = scrapedProjectData["ID"]

            financeType = driver.find_element(By.XPATH, f"//table[@id='main_table']/tbody/tr[{k}]/td[2]").text
            singleFinance["type_id"] = checkAndAssingType(financeTypes, financeType)

            financeData.append(singleFinance)

    return financeData
    

def scraping():
    driver.get("https://vav.unob.cz/projects/index/0")
    maxPage = driver.find_element(By.XPATH, "//div[@id='main-appmenu']/div[2]/div[1]/strong").text[1:-1]

    #PRO PLNY/CASTECNY SCRAPING VYMENIT FORY
    for i in range(0, int(maxPage), 25): 
    #for i in range(0, 24, 25):
        driver.get(f"https://vav.unob.cz/projects/index/{i}")

        tableLength = len(driver.find_elements(By.TAG_NAME, "tr"))

        for k in range(2, tableLength + 1):
            #Project
            currentProjectURL = driver.find_element(By.XPATH, f"//table[@id='main_table']/tbody/tr[{k}]/td[3]/a").get_attribute("href")
            driver.get(currentProjectURL)
            
            scrapedProjectData = scrapeProjectData()
            projectsData.append(scrapedProjectData)

            #Milestone
            milestonesData.append(generateProjectMilestone(scrapedProjectData))

            #Finance
            requestsURL = driver.find_element(By.XPATH, "//div[@id='main-appmenu']/div[1]/a[2]").get_attribute("href")
            driver.get(requestsURL)

            financesData.append(scrapeFinanceData(scrapedProjectData, requestsURL))

            #Navrat
            driver.get(f"https://vav.unob.cz/projects/index/{i}")


def makeJson():
    data = {}

    data["projects"] = projectsData
    data["finances"] = financesData
    data["milestones"] = milestonesData
    data["groups"] = groupsData
    data["projectTypes"] = projectTypes
    data["financeTypes"] = financeTypes
    data["externalIDs"] = externalIDs

    with open("scrapedData.json", "w", encoding="utf-8") as out_file:
        json.dump(data, out_file, indent = 4, ensure_ascii = False)


def main():
    login()
    scraping()
    makeJson()
    driver.close()

main()