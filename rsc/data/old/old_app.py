import json
import time
import pandas as pd
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

from src.shopping_api import *
from src.return_json import *
from src.main_func import *

ERROR_MESSAGE = '네트워크 접속에 문제가 발생하였습니다. 잠시 후 다시 시도해주세요.'
blank = '='*200

# 키즈존
kids_zone_df = pd.read_csv('./rsc/data/kidszone.csv')
kids_zone_df.fillna('', inplace=True)
kids_zone_df = kids_zone_df[kids_zone_df['image_link'] != '']

# 약국
pharmacy_df = pd.read_csv('./rsc/data/pharmacy.csv')
pharmacy_df.fillna('', inplace=True)

# 병원 / 응급실
hospital_df = pd.read_csv('./rsc/data/hospital_real.csv')
emergency_df = pd.read_csv('./rsc/data/emergency_real.csv')


# 육아종합지원센터
childcare_sido_df = pd.read_csv('./rsc/data/childcare_sido.csv')
childcare_sido_df.fillna('', inplace=True)

childcare_sigungu_df = pd.read_csv('./rsc/data/childcare_sigungu.csv')
childcare_sigungu_df.fillna('', inplace=True)

# 유치원
kindergarden_df = pd.read_csv('./rsc/data/kindergarden.csv')
kindergarden_df.fillna('', inplace=True)


today = datetime.now() + timedelta(hours=9)
current_time = datetime.strftime(today, '%H:%M')
print(' * Current time : {}'.format(current_time))

weekday_dict = dayOfWeek()
weekday = weekday_dict[today.weekday()]
print(' * weekday : {}'.format(weekday))


app = Flask(__name__)


# 풀백 블록
@app.route('/fullback', methods=['POST'])
def fullback():
    start_time = time.time()
    utterance = request.get_json()['userRequest']['utterance']
    answer_text = requests.post('https://mrc-api.nexr.kr/get_chat', json={
                                "utterance": utterance}, timeout=30, headers={'Content-Type': 'application/json'}).json()
    print(f"user:{utterance} -> chatbot:{answer_text['result']}")
    res = simpleText(answer_text['result'])
    print('걸린 시간:{:.3f}'.format(time.time()-start_time))
    return jsonify(res)


@app.route('/childcare_sido', methods=['POST'])
def childcare_sido_search():
    sys_location = get_location()
    answer_df = childcare_sido_df[childcare_sido_df['소재지'].str.contains(
        sys_location.strip())]

    if len(answer_df) == 0:
        res = simpleText('정확한 시도명을 입력해주세요.')
    else:
        items_list = []
        for index in answer_df.index:
            list_items = listItem_childCare(
                answer_df.loc[index, '센터명'] + ' 육아종합지원센터', answer_df.loc[index, '소재지'], answer_df.loc[index, '홈페이지'])
            items_list.append(list_items)
        res = return_res('basicCard', items_list)
    return jsonify(res)


@app.route('/childcare_sigungu', methods=['POST'])
def childcare_sigungu_search():
    sys_location = get_location()
    answer_df = childcare_sigungu_df[childcare_sigungu_df['소재지'].str.contains(
        sys_location.strip())]

    if len(answer_df) == 0:
        res = simpleText('정확한 시군구명을 입력해주세요.')
    else:
        items_list = []
        for index in answer_df.index:
            list_items = listItem_childCare(
                answer_df.loc[index, '센터명'] + ' 육아종합지원센터', answer_df.loc[index, '소재지'], answer_df.loc[index, '홈페이지'])
            items_list.append(list_items)
        res = return_res('basicCard', items_list)
    return jsonify(res)


@app.route('/kindergarden', methods=['POST'])
def kindergarden_search():
    sys_location = get_location()
    answer_df = kindergarden_df[kindergarden_df['주소'].str.contains(
        sys_location.strip())][:20]

    if len(answer_df) == 0:
        res = simpleText('해당 주변 지역의 유치원을 찾지 못하였습니다.')

    else:
        items_list = []
        for index in answer_df.index:
            list_items = listItem_kindergarden(answer_df.loc[index, '어린이집명'], answer_df.loc[index, '어린이집유형구분'], answer_df.loc[index, '어린이집전화번호'], answer_df.loc[index, '주소'], answer_df.loc[index, '보육실수'],
                                               answer_df.loc[index, '놀이터수'], answer_df.loc[index, '보육교직원수'], answer_df.loc[index, '정원수'], answer_df.loc[index, '현원수'], answer_df.loc[index, '통학차량운영여부'], answer_df.loc[index, '홈페이지주소'])
            items_list.append(list_items)
        res = return_res('basicCard', items_list)
    return jsonify(res)


@app.route('/kidszone', methods=['POST'])
def kidszone_search():
    sys_location = get_location()
    answer_df = kids_zone_df[kids_zone_df['place_detail'].str.contains(
        sys_location.strip())][:20]

    if len(answer_df) == 0:
        res = simpleText('해당 주변 지역의 키즈존을 찾지 못하였습니다.')
    else:
        items_list = []
        for index in answer_df.index:
            basic_items = basicCard_kidszone(answer_df.loc[index, 'title'], answer_df.loc[index, 'category'], answer_df.loc[index, 'introduce'],
                                             answer_df.loc[index, 'place_detail'], answer_df.loc[index, 'open_time'], answer_df.loc[index, 'phone_num'], answer_df.loc[index, 'image_link'])
            items_list.append(basic_items)
        res = return_res('basicCard', items_list)
    return jsonify(res)


@app.route('/hospital', methods=['POST'])
def hospital_search():
    req = request.get_json()
    print(f"{blank}\n{req}\n{blank}")

    # 타겟 병원 카테고리
    try:
        hospital_target = req["action"]["detailParams"]["hospital"]["value"]
        print(f"{blank}\nhospital_target1 : {hospital_target}\n{blank}")

    except:
        # pass
        hospital_target = req['userRequest']['utterance']
        print(f"{blank}\nhospital_target2 : {hospital_target}\n{blank}")

    try:
        if ((hospital_target == '병원') | (hospital_target == '종합병원') | (hospital_target == '상급종합병원') | (hospital_target == '의원')):
            utterance_df = hospital_df[((hospital_df['업무구분2'] == '병원') | (hospital_df['업무구분2'] == '종합병원') | (
                hospital_df['업무구분2'] == '상급종합병원') | (hospital_df['업무구분2'] == '의원'))]
        elif ((hospital_target == '보건진료소') | (hospital_target == '보건지소') | (hospital_target == '보건소')):
            utterance_df = hospital_df[(hospital_df['업무구분2'] == '보건진료소') | (
                hospital_df['업무구분2'] == '보건지소') | (hospital_df['업무구분2'] == '보건소')]
        elif hospital_target == '응급실':
            utterance_df = emergency_df
        elif ((hospital_target == '치과') | (hospital_target == '치과의원') | (hospital_target == '치과병원')):
            utterance_df = hospital_df[(hospital_df['업무구분2'] == '치과의원') | (
                hospital_df['업무구분2'] == '치과병원')]
        elif ((hospital_target == '한방') | (hospital_target == '한의원') | (hospital_target == '한방병원')):
            utterance_df = hospital_df[(hospital_df['업무구분2'] == '한의원') | (
                hospital_df['업무구분2'] == '한방병원')]

        # 타겟 도로명 주소
        sys_location = get_location()

        target_df = utterance_df[utterance_df['주소'].str.contains(
            sys_location.strip())]
        target_df = target_df[target_df[weekday+' 진료'] != '-']
        print(target_df.head())

        # 오픈 시간 조건!
        condition_open = target_df[weekday+' 진료'].str[:5] <= current_time
        condition_close = target_df[weekday+' 진료'].str[-5:] > current_time
        answer_df = target_df[((condition_open) & (condition_close))][:20]

        if len(answer_df) == 0:
            res = simpleText('해당 주변 지역의 병원을 찾지 못하였습니다.')
        else:
            print(answer_df.head())
            items_list = []
            for index in answer_df.index:
                list_items = listItem_hospital(answer_df.loc[index, '병원명'], answer_df.loc[index, '업무구분2'], answer_df.loc[index, '대표전화'], answer_df.loc[index, '주소'],
                                               answer_df.loc[index, weekday+' 진료'], answer_df.loc[index, '토요일 진료'], answer_df.loc[index, '일요일 진료'], answer_df.loc[index, '공휴일 진료'], answer_df.loc[index, '홈페이지'])
                items_list.append(list_items)
            res = return_res('basicCard', items_list)
        return jsonify(res)

    except Exception as e:
        res = simpleText("""검색 결과를 찾지 못하였습니다. 
아래의 카테고리 안에서 선택하여 주세요.
============================
병원, 종합병원, 상급종합병원, 의원\n보건진료소, 보건지소, 보건소
응급실 
치과, 치과의원, 치과병원, 
한방, 한의원, 한방병원
============================""")
        return jsonify(res)
    


@app.route('/pharmacy', methods=['POST'])
def pharmacy_search():
    sys_location = get_location()

    # 도로명 주소 조건!
    utterance_df = pharmacy_df[pharmacy_df['도로명주소'].str.contains(
        sys_location.strip())]

    # Null값 제외!
    utterance_df = utterance_df[utterance_df[weekday] != '-']

    # 오픈 시간 조건!
    condition_open = utterance_df[weekday].str[:5] <= current_time
    condition_close = utterance_df[weekday].str[-5:] > current_time

    answer_df = utterance_df[((condition_open) & (condition_close))][:20]

    if len(answer_df) == 0:
        res = simpleText('해당 주변 지역의 약국을 찾지 못하였습니다.')

    else:
        items_list = []
        for index in answer_df.index:
            list_items = listItem_pharmacy(answer_df.loc[index, '약국명'], answer_df.loc[index, '대표전화'], answer_df.loc[index, '도로명주소'],
                                           answer_df.loc[index, weekday], answer_df.loc[index, '토요일'], answer_df.loc[index, '일요일'], answer_df.loc[index, '공휴일'])
            items_list.append(list_items)
        res = return_res('basicCard', items_list)

    return jsonify(res)


@app.route('/shopping', methods=['POST'])
def shopping_search():
    req = request.get_json()
    # user_id = req['userRequest']['user']['properties']['plusfriendUserKey']

    shop_target = req["action"]["detailParams"]["baby_shopping"]["value"]

    block_id = req["userRequest"]["block"]["id"]
    print('block_id', block_id)

    shop_items = get_shop_list(shop_target)
    items_list = []
    for item in shop_items:
        commerce_items = commerceCard(
            item['title'], item['brand'], item['maker'], item['lprice'], item['link'], item['image'])
        items_list.append(commerce_items)
    res = return_res('commerceCard', items_list)
    return jsonify(res)


@app.route('/search', methods=['POST'])
def query_search():
    req = request.get_json()
    # print(req)
    question = req["action"]["params"]["question"]
    print(question)
    data = {"question": question}
    # r = requests.post('http://192.168.150.103:8002/get_NaverInfo', json=data)
    res = requests.post('https://mrc-api.nexr.kr/get_NaverInfo', json=data,
                        timeout=30, headers={'Content-Type': 'application/json'})
    # print(r.json()['version'])
    return res.json()


# 메인 함수
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
