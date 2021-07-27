today = date.today() 
yesterday = today - timedelta(days = 1) 

splitedDate = str(yesterday).split('-')
MergeSplitedDate = splitedDate[0] + splitedDate[1] + splitedDate[2]
print(today)
print(yesterday)
print(MergeSplitedDate)