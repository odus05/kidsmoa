import requests

def get_shop_list(query):
    answer = ''
    client_id = "hEZj5TyMNYcXk944fC_T"
    client_secret = "7G6RbwteeP"
    
    api_url = "https://openapi.naver.com/v1/search/shop.json?query={}&display=10&sort=sim".format(query)
    header_parms = {"X-Naver-Client-Id":client_id, "X-Naver-Client-Secret":client_secret}
    res = requests.get(api_url, headers=header_parms)
    
    if res.status_code == 200:
        data = res.json()
        return data['items']
      
    else:
        print ('Error : {}'.format(res.status_code))
        return '에러가 발생하였습니다.'
            