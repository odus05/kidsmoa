import time
import pandas as pd
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

from src.reply_json import *
from src.shopping_api import get_shop_list
from src.auxiliary_func import get_location, dayOfWeek

#flask server
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = Api(app)

# 현재 시간
today = datetime.now() + timedelta(hours=9)
current_time = datetime.strftime(today, '%H:%M')
print(' * Current time : {}'.format(current_time))
# 현재 날짜(요일)
weekday_dict = dayOfWeek()
weekday = weekday_dict[today.weekday()]
print(' * weekday : {}'.format(weekday))



#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# 풀백 블록
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
class FULLBACK_PREPROC_DF_IF(Resource):
    def __init__(self):
        self.req = request.get_json()
        print(self.req)
    def post(self):
        start_time = time.time()
        utterance = self.req['userRequest']['utterance']
        answer_text = requests.post('https://mrc-api.nexr.kr/get_chat', json={
									"utterance": utterance}, timeout=30, headers={'Content-Type': 'application/json'}).json()
        print(f"user:{utterance} -> chatbot:{answer_text['result']}")
        res = simpleText(answer_text['result'])
        print('걸린 시간:{:.3f}'.format(time.time()-start_time))
        return jsonify(res)




#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# 병원 검색!
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
class HOSPITAL_PREPROC_DF_IF(Resource):

	def __init__(self, root_path='./rsc/data'):
		self.req = request.get_json()
		#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
		# 데이터(CSV) 정보 불러오기!
		#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
		# 병원 / 응급실
		self.hospital_df = pd.read_csv(f'{root_path}/hospital.csv')
		self.emergency_df = pd.read_csv(f'{root_path}/emergency.csv')


	def post(self):
		try:
			hospital_target = self.req["action"]["detailParams"]["hospital"]["value"]
		except:
			print('a'*100)
			pass
		
		try:
			# 병원, 종합병원, 상급종합병원, 요양병원, 의원, -> 병원
			if ((hospital_target == '병원') | (hospital_target == '종합병원') | (hospital_target == '상급종합병원') | (hospital_target == '요양병원')| (hospital_target == '의원')):
				utterance_df = self.hospital_df[((self.hospital_df['업무구분2'] == '병원') | (self.hospital_df['업무구분2'] == '종합병원') | (self.hospital_df['업무구분2'] == '상급종합병원') | (self.hospital_df['업무구분2'] == '요양병원') | (self.hospital_df['업무구분2'] == '의원'))]
			# 보건소, 보건지소, 보건진료소, 보건의료원 - > 보건소
			elif ((hospital_target == '보건의료원') | (hospital_target == '보건진료소') | (hospital_target == '보건지소') | (hospital_target == '보건소')):
				utterance_df = self.hospital_df[(self.hospital_df['업무구분2'] == '보건의료원') | (self.hospital_df['업무구분2'] == '보건진료소') | (self.hospital_df['업무구분2'] == '보건지소') | (self.hospital_df['업무구분2'] == '보건소')]
			# 응급실 - > 응급실
			elif hospital_target == '응급실':
				utterance_df = self.emergency_df
			# 치과, 치과의원, 치과병원 -> 치과
			elif ((hospital_target == '치과') | (hospital_target == '치과의원') | (hospital_target == '치과병원')):
				utterance_df = self.hospital_df[(self.hospital_df['업무구분2'] == '치과의원') | (self.hospital_df['업무구분2'] == '치과병원')]
			# 한방, 한의원, 한방병원 -> 한의원
			elif ((hospital_target == '한방') | (hospital_target == '한의원') | (hospital_target == '한방병원')):
				utterance_df = self.hospital_df[(self.hospital_df['업무구분2'] == '한의원') | (self.hospital_df['업무구분2'] == '한방병원')]

			# 타겟 도로명 주소
			sys_location = get_location()
			target_df = utterance_df[utterance_df['주소'].str.contains(sys_location)]
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
			reply_text = """
                        검색 결과를 찾지 못하였습니다.\
                        아래의 카테고리 안에서 선택해주세요.\
                        ============================\
                        병원, 종합병원, 상급종합병원, 요양병원, 의원,\
                        보건소, 보건지소, 보건진료소, 보건의료원,\
                        응급실,\
                        치과의원, 치과병원,\
                        한의원, 한방병원\
                        ============================
                        """
            
			res = simpleText(reply_text)
			return jsonify(res)



#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# 약국 검색!
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
class PHARMACY_PREPROC_DF_IF(Resource):
	
	def __init__(self, root_path='./rsc/data'):
		#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
		# 데이터(CSV) 정보 불러오기!
		#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
		# 약국
		self.pharmacy_df = pd.read_csv(f'{root_path}/pharmacy.csv')
		self.pharmacy_df.fillna('', inplace=True)

	def post(self):
		# 타겟 도로명 주소
		sys_location = get_location()
		# 도로명 주소 조건!
		utterance_df = self.pharmacy_df[self.pharmacy_df['도로명주소'].str.contains(sys_location)]
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



#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# 쇼핑 검색!
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
class SHOPPING_PREPROC_DF_IF(Resource):
    
	def __init__(self):
		self.req = request.get_json()

	def post(self):
		# 쇼핑 품목!
		shop_target = self.req["action"]["detailParams"]["baby_shopping"]["value"]
		shop_items = get_shop_list(shop_target)
		items_list = []
		for item in shop_items:
			commerce_items = commerceCard(
				item['title'], item['brand'], item['maker'], item['lprice'], item['link'], item['image'])
			items_list.append(commerce_items)
		res = return_res('commerceCard', items_list)
		return jsonify(res)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# 키즈존 검색!
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
class KIDSZONE_PREPROC_DF_IF(Resource):
	
	def __init__(self, root_path='./rsc/data'):
		self.kids_zone_df = pd.read_csv(f'{root_path}/kidszone.csv')
		self.kids_zone_df.fillna('', inplace=True)
		# self.kids_zone_df = self.kids_zone_df[self.kids_zone_df['image_link'] != '']

	def post(self):
		# 타겟 도로명 주소
		sys_location = get_location()
		answer_df = self.kids_zone_df[self.kids_zone_df['place_detail'].str.contains(sys_location)][:20]

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

	
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# 유치원(어린이집) 검색!
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
class KINDERGARTEN_PREPROC_DF_IF(Resource):
	
	def __init__(self, root_path='./rsc/data'):
		self.kindergarten_df = pd.read_csv(f'{root_path}/kindergarten.csv')
		self.kindergarten_df.fillna('', inplace=True)
	def post(self):
		# 타겟 도로명 주소
		sys_location = get_location()
		answer_df = self.kindergarten_df[self.kindergarten_df['주소'].str.contains(sys_location)][:20]

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


#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# 네이버 지식iN 검색!
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
class QUERY_SEARCH_PREPROC_DB_IF(Resource):
	
	def __init__(self):
		self.req = request.get_json()
	def post(self):
		# 요청 질의!
		question = self.req["action"]["params"]["question"]
		print(question)
		data = {"question": question}
		res = requests.post('https://mrc-api.nexr.kr/get_NaverInfo', json=data,
							timeout=30, headers={'Content-Type': 'application/json'})
		return res.json()



#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# 육아종합지원센터 (시도별)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
class CHILDCARE_SIDO_PREPROC_DB_IF(Resource):
	
	def __init__(self, root_path='./rsc/data'):
		self.childcare_sido_df = pd.read_csv(f'{root_path}/childcare_sido.csv')
		self.childcare_sido_df.fillna('', inplace=True)
	def post(self):
		# 타겟 도로명 주소
		sys_location = get_location()
		answer_df = self.childcare_sido_df[self.childcare_sido_df['소재지'].str.contains(sys_location)]

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


#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# 육아종합지원센터 (시군구별)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
class CHILDCARE_SIGUNGU_PREPROC_DB_IF(Resource):
	
	def __init__(self, root_path='./rsc/data'):
		self.childcare_sigungu_df = pd.read_csv(f'{root_path}/childcare_sigungu.csv')
		self.childcare_sigungu_df.fillna('', inplace=True)
	def post(self):
    	# 타겟 도로명 주소
		sys_location = get_location()
		answer_df = self.childcare_sigungu_df[self.childcare_sigungu_df['소재지'].str.contains(sys_location)]

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



api.add_resource(FULLBACK_PREPROC_DF_IF, '/fullback') # Fullback Block API
api.add_resource(HOSPITAL_PREPROC_DF_IF, '/hospital') # 병원/응급실 검색 API
api.add_resource(PHARMACY_PREPROC_DF_IF, '/pharmacy') # 약국 검색 API
api.add_resource(SHOPPING_PREPROC_DF_IF, '/shopping') # 쇼핑 검색 API
api.add_resource(KIDSZONE_PREPROC_DF_IF, '/kidszone') # 키즈존 검색 API
api.add_resource(KINDERGARTEN_PREPROC_DF_IF, '/kindergarden') # 유치원(어린이집) API
api.add_resource(QUERY_SEARCH_PREPROC_DB_IF, '/search') # 네이버 지식iN 검색 API
api.add_resource(CHILDCARE_SIDO_PREPROC_DB_IF, '/childcare_sido') # 육아종합지원센터(시도) 검색 API
api.add_resource(CHILDCARE_SIGUNGU_PREPROC_DB_IF, '/childcare_sigungu') # 육아종합지원센터(시군구) 검색 API




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)


