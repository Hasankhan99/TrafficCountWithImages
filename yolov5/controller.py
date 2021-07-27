
from datetime import datetime
import schedule
from AiProd_1_API import logic
# Global variables

apitm = False

# Function defination
def check_time():
    current_time = datetime.now().strftime("%H:%M:%S").split(':')[0]
    times = ['21','22','23']
    if current_time in times:
        return True
    else:
        return False

def timing():
    global apitm
    apitm = True
    print("apitm : ",apitm)


if __name__ == "__main__":
    apitm = check_time()
    schedule.every().day.at("21:35").do(timing)
    while True:
        if apitm:
            print("Call Function Here")
            logic()
            apitm = False
            print(apitm)
        schedule.run_pending()
    pass


