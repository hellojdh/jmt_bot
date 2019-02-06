## jmt_bot
Chatbot with slackclient(Made with [skdlzlabc](https://github.com/skdlzlabc/jmt_bot-1))

## jmt_bot 기능
jmt_bot은 다음과 같은 미니 게임을 할 수 있습니다.
1) 업다운 게임
2) 동물 초성 맞추기 게임
3) 끝말잇기

### 1) 업다운 게임
[Keywrod :: 업다운, 숫자, 1] 를 통해 동작을 하게됩니다.

해당 숫자의 Up, Down에 따라서 재미있는 이미지를 랜덤하게 보여줍니다.

![image](https://user-images.githubusercontent.com/39071991/52344258-a3cda800-2a5d-11e9-893f-bab49a46822b.png)

### 2) 동물 초성 맞추기 게임
[Keywrod :: 동물, 2] 를 통해 동작을 하게됩니다.

동물게임은 [랜덤 동물 싸이트](https://www.randomlists.com/random-animals) 에서 동물을 랜덤하게 뽑습니다.

js를 이용한 랜덤 뽑기를 가져오기위해 selenium을 다음과 같이 사용하였습니다.

```python
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
```

랜덤 동물 사진과 이름을 가져온 후 검색을 통한 구글 번역을 이용하여 영어로된 동물 이름을 한글로 번역한 뒤, 정규 표현식을 사용하여 변역을 통한 동물 이름에 들어가는 [목,과,류,아과] 같은 대 분류를 제거하였습니다. 그 후, 얻어온 동물의 한글 이름에서 정규 표현식을 통해 초성을 뽑아내주었습니다.

![image](https://user-images.githubusercontent.com/39071991/52344531-57cf3300-2a5e-11e9-9215-87e083171cf7.png)

### 3) 끝말잇기
[Keywrod :: 끝말잇기, 3] 를 통해 동작을 하게됩니다.

끝말잇기는 [단어 검색 싸이트](https://www.wordrow.kr/) 를 통해서 유저의 입력 단어에대한 검색 결과를 크롤링하여 그 중 랜덤으로 출력하도록 하였습니다. 검색 결과가 없을시 유저의 승리가 됩니다.

![image](https://user-images.githubusercontent.com/39071991/52344560-69b0d600-2a5e-11e9-94cf-0810c6aafd2c.png)

## 그 외 기능
1) Bot에 메시지를 보내기 위한 함수를 하나로 통합하여 하나의 함수 호출로 텍스트와 이미지를 Bot이 응답할 수 있도록 함.

```python
# 챗봇이 메시지를 보내게하는 함수
def _send_message(channel,keywords,attachment=[]):
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=keywords,
        attachments = attachment
    )
# 이미지 만들기 
def _make_image(title,image_url):
    result = [{"title":title,"image_url":image_url}]
    return result
```

2) 여러 게임들이 있기 때문에 다중으로 게임이 실행되지 않도록 게임 on_off 함수를 만들어 관리를 함.

```python
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
```

## Framework
1) Flask

## Library
1) json(json 형태 변환)
2) re(정규식 사용)
3) urllib(html 요청)
4) random(랜덤 숫자 적용)
5) bs4(BeautifulSoup, html 분석)
6) slackclient(Slack Bot API)
7) selenium(특정 사이트 크롤링)
