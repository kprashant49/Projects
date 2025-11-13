import pandas as pd
import numpy as np

# myindex = ['USA','Canada','Mexico']
# mydata = [1776, 1867,1821]
# myser = pd.Series(data = mydata,index=myindex)
# print(myser)
# print(myser['USA'])
#
# ages = {'Same':5,'Frank':10,'Spike':7}
# pd.Series(ages)
# print(ages)

# Imaginary Sales Data for 1st and 2nd Quarters for Global Company
# q1 = {'Japan': 80, 'China': 450, 'India': 200, 'USA': 250}
# q2 = {'Brazil': 100,'China': 500, 'India': 210,'USA': 260}
#
# sales_q1 = pd.Series(data=q1)
# sales_q2 = pd.Series(data=q2)
# print(sales_q1.keys())
# print(sales_q1/100)
# print(sales_q1.add(sales_q2,fill_value=0))
#
# np.random.seed(101)
# mydata = np.random.randint(0,101,(4,3))
# # print(mydata)
# myindex = ['CA','NY','AZ','TX']
# mycolumns = ['Jan','Feb','Mar']
# df = pd.DataFrame(data=mydata,index=myindex,columns=mycolumns)
# print(df)
df=pd.read_csv("D:\\Projects\\pierian_jose\\03-Pandas\\tips.csv")
# print(df.head())
df['tip%'] = np.round((df['tip']*100)/df['total_bill'],2)
# print(df.head())
df = df.set_index("Payment ID")
# print(df.loc['Sun2959'])
# print(df.iloc[0:4])
# one_row = df.iloc[0]
# df=df.append(one_row)
# print(df)
# df.rename(index={'Sun2959': 'Mon2959'}, inplace=True)
# print(df)
# bool_series = df['total_bill']>40
# print(df[bool_series])
# print(df[df['sex']=="Male"])
# print(df[df['size']>5])

# df=df[(df['sex']=="Male") | (df['size']>5)]
#
# df=df[df['day'].isin(['Sat','Sun'])]
# print(df.to_markdown())
print(str(12345675654)[-4:0])