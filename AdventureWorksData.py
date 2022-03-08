import pyodbc
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
#%matplotlib


def HandleHierarchyId(v):
      return str(v)

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=localhost;' 
                      'DATABASE=AdventureWorks2019;' 
                       'Trusted_connection=yes;')

conn.add_output_converter(-151, HandleHierarchyId)             
 
cursor = conn.cursor()

def getOrgLevelnames(level):
    
    firstNames = []
    lastNames = []
    IDs = []
    names = []
    addr = []
    IDNames = {}
    if int(level) not in range (1,5):
        print('That level is not in the company')
        return null
    else:
        cursor.execute('''select FirstName, LastName, P.BusinessEntityID, AddressLine1, City, Name
                          FROM Person.Person P,HumanResources.Employee HD,Person.Address PA,Person.BusinessEntityAddress PB,
                          Person.StateProvince PS
                          Where HD.OrganizationLevel = ? AND P.BusinessEntityID = HD.BusinessEntityID 
                          AND PB.AddressID = PA.AddressID  AND P.BusinessEntityID = PB.BusinessEntityID
                          AND PS.StateProvinceID = PA.StateProvinceID
                        ''', level)
    for row in cursor:
        #print('Name: ' , row)
        
        firstNames.append(row[0])
        lastNames.append(row[1])
        names.append(row[0] + ' '+ row[1])
        IDs.append(row[2])
        #IDNames[row[2]] = row[0] + ' ' + row[1]
        addr.append(row[3] + ' ' + row[4] + ', ' + row[5])
    addr_df = pd.DataFrame({'Entity ID': IDs, 'Employee Name': names, 'Address': addr})
    
    return addr_df.head()
   
def getAllSalaries():
    names = []
    rates = [] 
    cursor.execute('''SELECT FirstName, LastName, P.BusinessEntityID,Rate
                   FROM Person.Person P,HumanResources.EmployeePayHistory HE
                   WHERE P.BusinessEntityID = HE.BusinessEntityID
                   ORDER BY P.BusinessEntityID''')
    
    for row in cursor:
        names.append(row[0] + ' ' + row[1])
        
        rates.append(round(row[3], 2))
    rate_df = pd.DataFrame({"Employee Name": names, "Pay Rate(1 week)": rates})
    return rate_df.head()

def getRate(name):
        cursor.execute('''SELECT FirstName, LastName,P.BusinessEntityID,Rate
                   FROM Person.Person P,HumanResources.EmployeePayHistory HE
                   WHERE P.BusinessEntityID = HE.BusinessEntityID
                   ORDER BY P.BusinessEntityID''')
        for row in cursor:
            
            fullName = row[0] + ' ' + row[1]
        
            if fullName == name:
                rate = str(round(row[3], 2))
                return rate
        return "Name not found"




def payRateHistorybyPosition(userJobChoice,currentYear = 2013):

    HireDates = []
    rates = []  


    rateTotalJob = 0
    jobCount = 0

    yearsWorked = 0


    cursor.execute('''SELECT P.BusinessEntityID, FirstName, LastName,Rate, JobTitle, HireDate
                   FROM Person.Person P,HumanResources.EmployeePayHistory HEP, HumanResources.Employee HE
                   WHERE P.BusinessEntityID = HEP.BusinessEntityID  AND HE.BusinessEntityID = P.BusinessEntityID AND
				   JobTitle LIKE CONCAT('%',?,'%') 
                   ORDER BY HireDate ASC;''', userJobChoice)
    currentYear = 2013


    for row in cursor:
        datetime = str(row[5])
        year = datetime[:4]
        #print(row[5])
        HireDates.append(year)
        rates.append(row[3])

    k=0
    yearAvgs = []
    yearAvg = {}
    years = []

    try:

        print("\nPay Rate history for "+ userJobChoice) 
        print("\nLast payrate recorded in year ", currentYear, "\n")
        for j in range(len(HireDates)):
   
                try:
                    if HireDates[j] != HireDates[j+1]:
                            if j == 0:
                                k+=1
                                print("Average pay rate in", HireDates[j], "("+str(len(HireDates[:k]))+" employees): ",
                                      round(sum(rates[:k])/len(rates[:k]), 2))
                                yearAvgs.append(round(sum(rates[:k])/len(rates[:k]), 2))
                                years.append(HireDates[j])
                            else:
                                print("Average pay rate in", HireDates[j], "("+str(len(HireDates[:k]))+" employees): ",  
                                      round(sum(rates[:k])/len(rates[:k]), 2))
                                yearAvgs.append(round(sum(rates[:k])/len(rates[:k]), 2))
                                years.append(HireDates[j])
                    elif j == 0:
                        k += 1
                except IndexError:
                    print("\nCurrent average pay rate ("+str(len(HireDates[:k]))+" employees): ", 
                          round(sum(rates[:k])/len(rates[:k]), 2))
                    yearAvgs.append(round(sum(rates[:k])/len(rates[:k]), 2))
                    years.append(HireDates[j])
                k += 1 
        print("First year position was hired:", HireDates[0], "\n")
        print("Last year position was hired:", HireDates[-1], "\n")
        if(len(years)>1):
            yearAvgs = {'Year': years, 'Avg': yearAvgs}
            df  = pd.DataFrame(data=yearAvgs)
            df.head()
            plt.title("Pay Rate annual trends for "+ userJobChoice)
            plt.plot("Year", "Avg", data=df)
            plt.show()
        else:
            print("No other payrates to report")
    except IndexError:
        print("Job not found in Database")

jobChoice = input("\nWhat job would you like to see payment history on?\n")
payRateHistorybyPosition(jobChoice)


    