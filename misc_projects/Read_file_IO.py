# import pandas as pd
# file_path = r"C:\Users\PrashantKumar\OneDrive - Pepper India Resolution Private Limited\Desktop\Final_Allocation.xlsx"
# df = pd.read_excel(file_path, engine="openpyxl")
# print(df.head())
# print(df.values)

filepath2 = r"C:\Users\PrashantKumar\OneDrive - Pepper India Resolution Private Limited\Desktop\Addresses3.txt"
# myfile = open(filepath2)
# content = myfile.read()
# print(content)
# myfile.seek(0)
# content_list = myfile.readlines()
# print(content_list)
# myfile.close()
try:
    with open(filepath2, mode = 'r') as my_file:
        print(my_file.read())

except FileNotFoundError:
    print("the file doesnt exist")
