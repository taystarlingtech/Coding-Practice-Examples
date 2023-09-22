from asyncio.windows_events import NULL
from cmath import nan
import numpy as np
import pandas as pd

#-----Reads Excel file-----
Data = pd.read_excel (r'C:\Users\tstarling\Downloads\Infinium Audit\estimated review items.xlsx')
#-----Puts needed Columns into variable-----
EstimatedItems = pd.DataFrame(Data, columns= ['Permission Name','Position Number'])
#print(Permission)

#-----Reads Excel file-----
Data2  = pd.read_excel (r'C:\Users\tstarling\Downloads\Infinium Audit\SECURITY REPORT PE.xlsx')
#-----Puts needed Columns into variable-----
UserName= pd.DataFrame(Data2, columns= ['User ID', 'User Name', 'Infinium Report Title'])
#print(UserName)

#-----Reads Excel file-----
Data3  = pd.read_excel (r'C:\Users\tstarling\Downloads\Infinium Audit\User ID for Infinium Audit.xlsx')
#-----Puts needed Columns into variable-----
Titles_Names = pd.DataFrame(Data3, columns= ['User ID', 'Title', 'Position Number'])
#print(Titles_Names)

#-----Gets Infinium Usernames FROM report and adds employee info from user id for infinium audit-----
IDMatch = pd.merge(UserName,Titles_Names, on = 'User ID', how= 'left')

#Matches Postion numbers in estimated review itesms with numbers in infinium audit
NoPosNum = pd.merge(IDMatch, EstimatedItems, on  = 'Position Number', how = 'left')
#print(NoPosNum)
#I had to hand highlight the rows in excel via 
NoPosNum.to_excel("Authorized Infinium Users2.xlsx")




