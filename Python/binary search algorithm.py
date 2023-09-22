from tkinter import *
import tkinter as tk
# Create an instance of tkinter frame or windowdow
window=Tk()
# Set the size of the tkinter windowdow
window.geometry("700x350")
window.title("PythonGeeks")#give title to the window
head=Label(window, text="Let's perform Binary Search", font=('Calibri 15'))# a label
head.pack(pady=20)
Label(window, text="Enter a Sorted List", font=('Calibri')).pack()# a label 

#l=[1,2,3,4,5,6,7,8,9,10]
n=tk.IntVar()
e=tk.StringVar()
def binary_search():
    l=e.get().split(" ")
    for i in range(0, len(l)):
        l[i] = int(l[i])
    
    num=(n.get())
    first = 0
    last = len(l)-1
    found = False
    while( first<=last and not found):
        mid = (first + last)//2
        if (l[mid] == num) :
                found = True
        else:
            if num < l[mid]:
                last = mid - 1
            else:
                first = mid + 1	
    if found == True:
        Label(window, text="Number found in the list", font=('Calibri')).place(x=280,y=180)
    else:
        Label(window, text="Number NOT found in the list", font=('Calibri')).place(x=240,y=210)

Entry(window,textvariable=e).pack()
Label(window,text='Enter number you want to search').pack()
Entry(window,textvariable=n).pack()#enter a number here
#create a button
Button(window, text="Search", command=binary_search).pack()
window.mainloop()#main command
