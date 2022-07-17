from flask import request

    
def get_location():
    req = request.get_json()
    print(req)
    try:
        sys_location = req["action"]["params"]["sys_location"] + ' ' + req["action"]["params"]["sys_location1"]
        print('sys_location1', sys_location)
    except:
        sys_location = req["action"]["detailParams"]['sys_location']['origin']
        print('sys_location2', sys_location)
    return sys_location.strip()



def dayOfWeek():
    weekday=dict()
    weekday[0] = '월요일'
    weekday[1] = '화요일'
    weekday[2] = '수요일'
    weekday[3] = '목요일'
    weekday[4] = '금요일'
    weekday[5] = '토요일'
    weekday[6] = '일요일'
    return weekday


