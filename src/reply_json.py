def simpleText(text):
    answer = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": text
                            }
                        }
                    ]
                }
            }
    return answer

def commerceCard(title, brand, maker, price, link, image):
    new_title = title.replace('<b>','').replace('</b>','')
    if maker!='':
        nickname = f'{brand} ({maker})'
    else:
        nickname = f'{brand}'
        
    answer = {
              'description': new_title,
              'price': price,
              # 'discount': 1000,
              'currency': 'won',
              'thumbnails': [
                  {'imageUrl': image,
                   'link': {'web': link}}],
              'profile': {'imageUrl': image,
              'nickname': nickname},
              'buttons': [
                  {'label': '💳 구매하기',
                   'action': 'webLink',
                   'webLinkUrl': link},
               # {'label': '전화하기', 'action': 'phone', 'phoneNumber': '354-86-00070'},
                  {'label': '📤 공유하기', 'action': 'share'}]
            }
    return answer





# title, introduce, place, open_time, phone_num, image_link

def basicCard_kidszone(title, category, introduce, place, open_time, phone_num, image_link):
    map_place = place.split('(')[0].strip()
    open_time_list = (open_time.split('\n'))
    open_time = '\n'.join(['⏰ ' + open_time for open_time in open_time_list if open_time !=''])
    if introduce!='':
        introduce = '👶 ' + introduce
    answer = {
              "title": "{} ({})".format(title, category),
              "description": "➡ {}\n{}\n{}".format(place, open_time,introduce),
              "thumbnail": {
                "imageUrl": image_link
              },
              "buttons": [
                {
                  "action":  "webLink",
                  "label": "🗺 지도보기",
                  "webLinkUrl": "https://m.map.naver.com/search2/search.naver?query={}#/map".format(map_place)
                },
                {
                  "action": "phone",
                  "label": "📱 전화하기",
                  "phoneNumber": phone_num
                },
                {
                  "action": "share",
                  "label": "📤 공유하기"
                }
              ]
            }
    return answer




# "https://www.google.co.kr/maps/place/{}".format(map_place) # 구글지도
# "https://m.map.naver.com/search2/search.naver?query={}#/map".format(map_place) # 네이버 지도
# "https://map.naver.com/v5/search/{}".format(map_place)
       



def listItem_hospital(title, category, phone_num, place, open_time, saturday_time, sunday_time, holiday_time, url):
    
    map_place = place.split('(')[0].strip()
    if saturday_time == '-':
        saturday_time = '쉬는 날'
    if sunday_time == '-':
        sunday_time = '쉬는 날'
    if holiday_time == '-':
        holiday_time = '쉬는 날'
        
        
    if url != '-':
        answer = {
                  "title": "{}({})".format(title,category),
                  "description": "➡ {}\n⏰ (평일)   {}\n⏰ (토요일) {}\n⏰ (일요일) {}\n⏰ (공휴일) {}".format(place, open_time, saturday_time, sunday_time, holiday_time),
                  "buttons": [
                    {
                      "action":  "webLink",
                      "label": "🌍 홈페이지",
                      "webLinkUrl": url
                    },
                    {
                      "action": "phone",
                      "label": "📱 전화하기",
                      "phoneNumber": phone_num
                    },
                    {
                      "action": "share",
                      "label": "📤 공유하기"
                    }
                  ]
                }
    else:
        map_place = ' '.join(place.split(' ')[:4])
        answer = {
          "title": "{}({})".format(title,category),
          "description": "➡ {}\n⏰ (평일)   {}\n⏰ (토요일) {}\n⏰ (일요일) {}\n⏰ (공휴일) {}".format(place, open_time, saturday_time, sunday_time, holiday_time),
          "buttons": [
            {
              "action":  "webLink",
              "label": "🗺 지도보기",
              "webLinkUrl": "https://m.map.naver.com/search2/search.naver?query={}#/map".format(map_place)
            },
            {
              "action": "phone",
              "label": "📱 전화하기",
              "phoneNumber": phone_num
            },
            {
              "action": "share",
              "label": "📤 공유하기"
            }
          ]
        }
        
    return answer



def listItem_kindergarden(title, category, phone_num, place, class_room, playground, teacher, full_child_num, now_child_num, bus_yn, url):
    if url != '':
        answer = {
                  "title": "{}({})".format(title, category),
                  "description": 
                  "➡ {}\n🏘 (보육실수) {}개\n👫 (현원수/정원수) {}/{}명\n🙎‍♀️ (보육교직원수) {}명\n⚽ (놀이터수) {}개\n🚌 (통학차량운영여부) {}".format(place, class_room, now_child_num, full_child_num, teacher, playground, bus_yn),
                  "buttons": [
                    {
                      "action":  "webLink",
                      "label": "🌍 홈페이지",
                      "webLinkUrl": url
                    },
                    {
                      "action": "phone",
                      "label": "📱 전화하기",
                      "phoneNumber": phone_num
                    },
                    {
                      "action": "share",
                      "label": "📤 공유하기"
                    }
                  ]
                }
    else:
        map_place = ' '.join(place.split(' ')[:4])
        answer = {
                  "title": "{}({})".format(title, category),
                  "description": 
                  "➡ {}\n🏘 (보육실수) {}개\n👫 (현원수/정원수) {}/{}명\n🙎‍♀️ (보육교직원수) {}명\n⚽ (놀이터수) {}개\n🚌 (통학차량운영여부) {}".format(place, class_room, now_child_num, full_child_num, teacher, playground, bus_yn),
                  "buttons": [
                    {
                      "action":  "webLink",
                      "label": "🗺 지도보기",
                      "webLinkUrl": "https://m.map.naver.com/search2/search.naver?query={}#/map".format(map_place)
                    },
                    {
                      "action": "phone",
                      "label": "📱 전화하기",
                      "phoneNumber": phone_num
                    },
                    {
                      "action": "share",
                      "label": "📤 공유하기"
                    }
                  ]
                }
        
    return answer





def listItem_pharmacy(title, phone_num, place, open_time, saturday_time, sunday_time, holiday_time):
    map_place = place.split('(')[0].strip()
    if saturday_time == '-':
        saturday_time = '쉬는 날'
    if sunday_time == '-':
        sunday_time = '쉬는 날'
    if holiday_time == '-':
        holiday_time = '쉬는 날'
        
        
    answer = {
              "title": title,
              "description": "➡ {}\n⏰ (평일)   {}\n⏰ (토요일) {}\n⏰ (일요일) {}\n⏰ (공휴일) {}".format(place, open_time, saturday_time, sunday_time, holiday_time),
              "buttons": [
                {
                  "action":  "webLink",
                  "label": "🗺 지도보기",
                  "webLinkUrl": "https://m.map.naver.com/search2/search.naver?query={}#/map".format(map_place)
                },
                {
                  "action": "phone",
                  "label": "📱 전화하기",
                  "phoneNumber": phone_num
                },
                {
                  "action": "share",
                  "label": "📤 공유하기"
                }
              ]
            }
    return answer


def listItem_childCare(title, place, url):
    map_place = place.split('(')[0].strip()
    answer = {
              "title": title,
              "description": "➡ "+place,
              "buttons": [
                {
                  "action":  "webLink",
                  "label": "🌍 홈페이지",
                  "webLinkUrl": url
                },
                {
                  "action":  "webLink",
                  "label": "🗺 지도보기",
                  "webLinkUrl": "https://m.map.naver.com/search2/search.naver?query={}#/map".format(map_place)
                },
                {
                  "action": "share",
                  "label": "📤 공유하기"
                }
              ]
            }
    return answer





def listCard_search(title, description, imageUrl):
    answer = {
              "title": title,
              "description": description,
              "imageUrl": imageUrl,
              "link": {
                "web": imageUrl
              }
    }
    return answer
  
    
    
def return_listCard(title, items_list, webLinkUrl):
    res = {'version': '2.0','template': {'outputs': [{'listCard': {'header': {'title': title}}}]}}
    res['template']['outputs'][0]['listCard']['items'] = items_list
    res['template']['outputs'][0]['listCard']['buttons'] = [{'label': '구경가기', \
                                                             'action': 'webLink', \
                                                             'webLinkUrl': webLinkUrl}]
    return res

def return_res(card_type, items_list):
    res = {'version': '2.0','template': {'outputs': [{'carousel': {'type': card_type}}]}}
    res['template']['outputs'][0]['carousel']['items'] = items_list
    return res




