from datetime import datetime, date, timedelta

def get_days(date1, date2):
    dt1 = datetime.strptime(date1, '%d/%m/%y')
    dt2 = datetime.strptime(date2, '%d/%m/%y')
    
    diff = abs((dt2-dt1).days)

    return diff

def get_days_from_now(date1):
    dt1 = datetime.strptime(date1, '%d/%m/%Y')
    dt2 = datetime.now()

    if dt1 <= dt2:
        return -1

    diff = abs((dt2-dt1).days)
    return diff

