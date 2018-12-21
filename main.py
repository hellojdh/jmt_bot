# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import random
from urllib import parse

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template
from time import sleep
###################################################################
from selenium import webdriver

app = Flask(__name__)

slack_token = "xoxb-505014660117-508577167127-ihpTOlmQCsr99i1HbPhCQcgT"
slack_client_id = "505014660117.506786567440"
slack_client_secret = "db81f21ec23e297e1a3599888364613f"
slack_verification = "QNPqdNdhznxTZhljh7WYac7w"
sc = SlackClient(slack_token)

num_game_img = "https://steemitimages.com/DQmf9iEQuQGLCvi4dUmePb9za3YcuSuoxQh12e62yjob3zH/%EC%97%85%EB%8B%A4%EC%9A%B4%EC%B5%9C%EC%A2%85%5D.jpg"
animal_game_img = "https://static-s.aa-cdn.net/img/gp/20600004650219/aEZEfui3Bsrs-JJkw6_cdA2GqsYD1VwmwE9VIGqoLFKjfY0NzwOg5ctn1U0GWdMvSMA=w300?v=1"

no_happy_img = ["https://static1.squarespace.com/static/5a0226406f4ca352ad5d7352/t/5a029fb553450a47e3005ba9/1518507181501/?format=1500w",
                "https://pbs.twimg.com/profile_images/764845649888092162/n4ezlCSa_400x400.jpg",
                "https://cdn-images-1.medium.com/max/1200/1*_QgWUfxBNsXTMN64C2F4hg.jpeg"]
happy_img = ["https://previews.123rf.com/images/moonshine/moonshine1201/moonshine120100008/11844033-%EC%B6%95%ED%95%98%ED%95%A9%EB%8B%88%EB%8B%A4-%EB%AA%AC%EC%8A%A4%ED%84%B0.jpg",
            "http://2runzzal.com/media/OW9OVVkrenY0NTN3NVpMVjNCY0c0UT09/thum.jpg",
            "http://upload2.inven.co.kr/upload/2017/09/07/bbs/i14656456632.gif",
            "http://cdn.sketchpan.com/member/d/dkdkk6/draw/1009819905622/0.png"]

########################### 동물 게임 ##############################
# 초성 리스트. 00 ~ 18
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
animal_name = ""
animal_img = ""
animal_chosung = ""
animal_chance = 5
status_animal_game = False
prev_url = "https://www.randomlists.com/"

# 동물의 정보를 가져오는 함수
def _get_animal_info(channel):
    global status_animal_game
    global animal_name
    global animal_chosung
    while True:
        url = prev_url+"random-animals?qty=1&show_images=on"
        driver = webdriver.Chrome("chromedriver.exe")
        driver.get(url)

        html = driver.page_source
        soup = BeautifulSoup(html,"html.parser")
        animal_name = soup.find('div',class_='Rand-stage').get_text()
        animal_img = prev_url+soup.find('img')['src']
        driver.close()
        _send_message(channel,"동물이름이 선택되었습니다!! 그림을 고르는 중입니다.")

        # 얻은 영어 동물이름을 바탕으로 한글로 바꾸기
        # tlid-translation translation
        url_trans = "https://www.google.com/search?q="+animal_name
        driver = webdriver.Chrome()
        driver.get(url_trans)
        html = driver.page_source
        driver.close()
        soup = BeautifulSoup(html,"html.parser")
        
        # 영어를 해석한 이름이 없을 경우 다시 이름 고르기
        try:
            animal_name = soup.find('div',class_="gsmt kno-ecr-pt kno-fb-ctx").get_text().split()[0]
            if animal_name=="":
                continue
            break
        except:
            _send_message(channel,"저의 천부적인 능력으로도 초성 이름을 맞출수 없어서 다시 고르는 중입니다.")
            pass
    # 동물 분류 없애기
    animal_name = re.sub("[류과아과목]","",animal_name)

    # 동물이름을 초성으로 변환
    chosung = ""
    print(animal_name)
    for word in animal_name:
        if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*',word) is not None:
            char_code = ord(word) - 44032
            char_chosung = int(char_code/588)
            chosung += CHOSUNG_LIST[char_chosung]
    animal_chosung = chosung
    _send_message(channel,"동물이름을 맞춰보세요!!",[{"title":chosung,"image_url":animal_img}])

    # 동물 게임 시작
    on_off_game(animal=True)
    # 이미지 앞단 주소 https://www.randomlists.com/

# 게임을 시작하는 함수
def _start_animal_game(channel,keywords):
    global animal_chance
    # 동물 게임을 한 적이 없다면 랜덤 동물을 가져온다.
    # status_animal_game = True로 바뀜
    # 사용자한테 보여준 상태
    if not status_animal_game:
        _send_message(channel,"게임을 시작합니다! 동물을 고르고 있습니다.",_make_image("동물 이름 맞추기",animal_game_img))
        _get_animal_info(channel)
    else:
        if animal_name==keywords[0]:
            _send_message(channel,"정답 입니다!!",_make_image("축하합니다~!",happy_img[random.randrange(0,4)]))
            _end_animal_game(channel)
            return make_response("App mention message has been sent", 200,{"X-Slack-No-Retry": 1})
        else:
            if animal_chance<2:
                _send_message(channel,"기회를 모두 소진했습니다. 게임이 종료됩니다.",_make_image("다음번엔 맞춰보세요!!",no_happy_img[random.randrange(0,3)]))
                _end_animal_game(channel)
            else :
                animal_chance-=1
                _send_message(channel,"틀렸습니다. 남은 기회 :: "+str(animal_chance))
                try:
                    if animal_chance==2:
                        if len(animal_name)!=1:
                            _send_message(channel,"힌트 :: "+animal_name[0]+animal_chosung[1:])
                    elif animal_chance==1:
                        if len(animal_name)!=2:
                            _send_message(channel,"힌트 :: "+animal_name[:2]+animal_chosung[2:])
                        elif len(animal_name)!=1:
                            _send_message(channel,"힌트 :: "+animal_name[0]+animal_chosung[1:])
                except:
                    pass
#[{"title":"Goat","image_url":image}]

def _end_animal_game(channel):
    global animal_chance
    global status_animal_game
    animal_chance=5
    status_animal_game = False
    _send_message(channel,"정답은 "+animal_name+" 입니다.")

# 챗봇이 메시지를 보내게하는 함수
def _send_message(channel,keywords,attachment=[]):
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=keywords,
        attachments = attachment
    )
# _send_message가 길어지지 않게 이미지 만들기 
def _make_image(title,image_url):
    result = [{"title":title,"image_url":image_url}]
    return result

###################################################################

# 게임이 시작되고 끝날 때 끄고 켜는 함수
def on_off_game(updown=False,animal=False,word=False):
    global status_animal_game
    global status_num_game
    global status_word_game
    global tmp_word
    global check
    tmp_word = ""
    check = 1

    status_num_game = updown
    status_animal_game = animal
    status_word_game = word


########################## 업다운 게임 #############################
# 업다운 게임 상태
status_num_game = False
# 게임 목표 숫자
num_game_target = 0
# 게임 기회
num_game_chance = 5

def _get_num_info(channel):
    global num_game_chance
    global num_game_target
    global status_num_game

    if not status_num_game:
        num_game_target = random.randrange(1,201)
        num_game_chance = 5
        on_off_game(updown=True)
        _send_message(channel,"숫자를 골랐습니다. 숫자를 입력해 맞춰보세요!")


up_img = ["https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Beijing_bouddhist_monk_2009_IMG_1486.JPG/1200px-Beijing_bouddhist_monk_2009_IMG_1486.JPG",
        "https://mediadc.brightspotcdn.com/dims4/default/78393fe/2147483647/strip/true/crop/3000x2000+0+0/resize/3000x2000!/quality/90/?url=https%3A%2F%2Fmediadc.brightspotcdn.com%2F4d%2Fe4%2Fb717d773363050a27353bf97930c%2F2564b2dc4b02bdd12d36e59bcf9f49ec.jpg",
        "https://resolveagency.com.au/wp-content/uploads/2017/06/thumbs-up-facebook.jpg"]

# up_img의 3번째 사진은 연속 따봉으로 2배이상 차이날 경우 알려주는 문구

down_img = ["https://www.pcper.com/files/imagecache/article_max_width/news/2018-04-12/simon%2Bthumbs-down.jpg",
            "https://media.istockphoto.com/photos/studio-shot-of-japanese-businessman-giving-thumb-down-picture-id669184194?k=6&m=669184194&s=612x612&w=0&h=M6g1QWn6g_a9an9tg1xKv4DjA-hcnEqdxVjgK7_ne7A=",
            "data:image/jpeg;base64,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"]
def _start_num_game(channel,keywords):
    global num_game_chance

    if not status_num_game:
        _send_message(channel,"게임을 시작합니다! 숫자를 고르겠습니다.(1~200)",_make_image("업다운 게임",num_game_img))
        _get_num_info(channel)
    else:
    # 게임 중 처리 구역
    # 숫자를 입력하지 않았을 경우 메시지 호출
        try:
            num = int(keywords)
        except:
            _send_message(channel,"숫자를 입력하셔야 합니다.")
        
        if num_game_chance < 2:
            on_off_game()
            _send_message(channel,"게임이 종료되었습니다.",_make_image("분발하세요!",no_happy_img[random.randrange(0,3)]))
        elif num == num_game_target:
            on_off_game()
            _send_message(channel,"축하 합니다!!!",_make_image("정답입니다~!",happy_img[random.randrange(0,4)]))
        elif num < num_game_target:
            num_game_chance -=1
            if num*2 < num_game_target:
                _send_message(channel,"더블업!! UP!! 두배이상 올려보세요!!"+"남은 기회: "+str(num_game_chance),_make_image("UP",up_img[2]))
            else:
                _send_message(channel,"UP!!  "+"남은 기회: "+str(num_game_chance),_make_image("UP",up_img[random.randrange(0,2)]))
        elif num > num_game_target:
            num_game_chance -=1
            _send_message(channel,"DOWN!!  "+"남은 기회: "+str(num_game_chance),_make_image("DOWN",down_img[random.randrange(0,3)]))
###############################################################

########################## 끝말 잇기 ###########################
# 끝말잇기 게임 중인걸 판다하는 변수
status_word_game = False
tmp_word = ""
check = 1

def _game3(channel,text): 
    global tmp_word
    global check
    
    # 유저 인풋
    word=text

    #잘못 입력하면 겜끝 
    print("컴퓨터 "+tmp_word + " " + "나: "+word[0])
    if tmp_word != word[0] and tmp_word != "":
        _send_message(channel,"틀렸습니다 ㅠㅠ",_make_image("1","https://static1.squarespace.com/static/5a0226406f4ca352ad5d7352/t/5a029fb553450a47e3005ba9/1518507181501/?format=1500w"))
        on_off_game()
        return
    try:
        tmp = word[len(word)-1:]
        url = "https://www.wordrow.kr/%EC%8B%9C%EC%9E%91%ED%95%98%EB%8A%94-%EB%A7%90/" + parse.quote(str(tmp))

        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html,'html.parser')
        word_list= [] #단어들 저장
    

        for each in soup.find_all("h3",class_="card-caption")[:20]: #모든 글자
            word = each.find("a")["href"][4:]
            if " " not in word:
                if len(word)>1: #1자리수 버려
                    word_list.append(re.sub("[하다]","",word))
    except:
        on_off_game()
        _send_message(channel,"승리하셨습니다!!!",_make_image("축하합니다!!!",happy_img[random.randrange(0,4)]))
        return
    
    if len(word_list) == 0:
        on_off_game()
        _send_message(channel,"승리하셨습니다!!!",_make_image("축하합니다!!!",happy_img[random.randrange(0,5)]))
        return

            
    print("::::  "+str(word_list))
    choice_word = word_list[random.randrange(0,len(word_list))]
    print("choice_word : "+ choice_word)
    tmp_word = choice_word[-1:] #사용자가 잘 입력하는지 검사하기 위해  
    _send_message(channel,choice_word,_make_image("제법이시네요!","http://cdn.sketchpan.com/member/d/dkdkk6/draw/1009819905622/0.png"))

one_time = False
def _start_word_game(channel,text):
    global tmp_word
    global one_time
    
    if tmp_word=="":
        _send_message(channel,"시작합니다!! 먼저 말씀하세요!",_make_image("","https://i.ytimg.com/vi/a7su5_SnSqE/maxresdefault.jpg"))
        on_off_game(word="True")
        tmp_word = text
        one_time = True
    else:
        if one_time:
            tmp_word = text[0]
            one_time = False
        _game3(channel,text)


################################################################
# 이벤트 핸들하는 함수
time = set()

def _event_handler(event_type, slack_event):
    # set type인 time을 통해 중복으로 메시지가 전달되는 것을 막는다.
    global time
    message_time = slack_event["event"]["ts"]
    if message_time in time:
        return make_response("App mention message has been sent", 200,{"X-Slack-No-Retry": 1})
    time.add(message_time)

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        # 유저명을 제외한 메시지 내용 뽑아오기
        keywords = text.split()[1:]
        print(keywords)
        print(status_animal_game)
        print(status_num_game)
        print(status_word_game)
        if keywords[0] == "종료":
            on_off_game()
            _send_message(channel,"게임이 종료되었습니다")
            return make_response("App mention message has been sent", 200,{"X-Slack-No-Retry": 1})

        # 게임 진행
        if status_animal_game:
            _start_animal_game(channel,keywords)
            return make_response("App mention message has been sent", 200,{"X-Slack-No-Retry": 1})
        elif status_num_game:
            _start_num_game(channel,keywords[0])
            return make_response("App mention message has been sent", 200,{"X-Slack-No-Retry": 1})
        elif status_word_game:
            _start_word_game(channel,keywords[0])
            return make_response("App mention message has been sent", 200,{"X-Slack-No-Retry": 1})
        
        # 게임 결정
        for data in keywords:
            if "동물" in data:
                _start_animal_game(channel,keywords)
            elif "2" in data:
                _start_animal_game(channel,keywords)
            elif "업다운" in data:
                _start_num_game(channel,keywords[0])
            elif "숫자" in data:
                _start_num_game(channel,keywords[0])
            elif "1" in data:
                _start_num_game(channel,keywords[0])
            elif "3" in data:
                _start_word_game(channel,keywords[0])
            elif "끝말잇기" in data:
                _start_word_game(channel,keywords[0])
            else:
                _send_message(channel,"1번 게임 keyword : 업다운,숫자,1")
                _send_message(channel,"2번 게임 keyword : 동물,2")
                _send_message(channel,"3번 게임 keyword : 끝말잇기,3")

        return make_response("App mention message has been sent", 200,{"X-Slack-No-Retry": 1})

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)