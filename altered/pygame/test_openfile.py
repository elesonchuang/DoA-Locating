'''
import tkinter as tk
from tkinter import filedialog

root=tk.Tk()
root.withdraw()

file_path=filedialog.askopenfile()
print(file_path)
input("exit:")
'''
try:
    if 1==1:
        print("fffff")
        pass
    print("lllll")
except:
    pass