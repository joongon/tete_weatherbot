# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import re
import dotenv
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

os.system('clear')
dotenv.load_dotenv()
TOKEN = os.getenv('TOKEN') #환경설정 파일(.env)에 텔레그램 토큰 변수를 설정한다.

def get_weather(where):

    try :
        weather = " "
        url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={}+날씨".format(where)
        
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        weather_info = bs.find_all("div", attrs={"class":"temperature_text"}) # 기온 정보
        weather_info2 = bs.find_all("div", attrs={"class":"temperature_info"}) # 날씨 상태
        weather_info3 = bs.find_all("ul", attrs={"class":"today_chart_list"}) # 미세먼지 추출
        weather_info4 = bs.find_all("span", attrs={"class":"temperature_inner"}) # 주간예보 중 금일
        weather_rainfall = bs.find_all("span", attrs={"class": "rainfall"}) #강수확률

        if len(weather_rainfall) > 0:
            rainfall_status = []
            for item in weather_rainfall:
                rainfall_status.append(item.get_text())
            print(rainfall_status, "--------> rainfall_status")
            print("오늘 오전 강수확율 : ", rainfall_status[0])
            print("오늘 오후 강수확율 : ", rainfall_status[1])
            print("내일 오전 강수확율 : ", rainfall_status[2])
            print("내일 오후 강수확율 : ", rainfall_status[3])
            rain_fall_forcast = f"강수율 : 오전 {rainfall_status[0]}, 오후 {rainfall_status[1]}\n"
            rain_fall_forcast2 = f"강수율 : 오전 {rainfall_status[2]}, 오후 {rainfall_status[3]}\n"

        if len(weather_info2) > 0:
            status_array = []
            status_aux_array = []
            for item2 in weather_info2:
                status = item2.find("p", attrs={"class":"summary"}).get_text()
                status_aux = item2.find("dl", attrs={"class":"summary_list"}).get_text()
                status_aux_array.append(status_aux)
                status_array.append(status)
            print(status_array, "---------> status_array")
            
            status1_temp = status_array[0].split('°')[0] + '°' #오늘 날씨 현황 ex) 어제 보다 4도 낮아요, 등
            status1_temp2 = status_array[0].split('°')[1].split()[0]
            if status1_temp2 == '높아요':
                status1 = status1_temp + " 높음"
            elif status1_temp2 == '낮아요':
                status1 = status1_temp + " 낮음"
            else:
                status1 = status1_temp
            status2 = status_array[0].split()[-1] #오늘 날씨 상태 ex)맑은, 흐림, 비 등
            print(status_array, "\n")
            print(status1_temp, '------> status1_temp')
            print(status1_temp2, '------> status1_temp2')
            print(status1, '------> status1')
            print(status2, '------> status2')
            tomm_status1 = status_array[1] #내일 오전 날씨 상태
            tomm_status2 = status_array[2] #내일 오후 날씨 상태
            status_auxx = status_aux_array[0]
            status_auxx = status_auxx.lstrip()

            location = f"*[ {where} / 현재 ]*" + "\n"

        if len(weather_info) > 0:

            temp_array = []

            for item in weather_info:
                temp = item.find("strong").get_text()
                
                t1 = temp[0:5]
                t2 = temp[5:]
                t3 = t1 + " " + t2
                
                temp_array.append(t3)
            temp_pr = temp_array[0]
            print(temp_pr, '---------> temp_pr')
            temp_tom_am = temp_array[1][3:]
            temp_tom_pm = temp_array[2][3:]
            print(temp_tom_am)
            print(temp_tom_pm)
                    
            temperature = "오전 " + temp_tom_am + ", 오후 " + temp_tom_pm

            p = re.compile('(-|)([0-9]|[1-9][0-9])[.][0-9]')
            extracted = p.search(temp_array[0])
            result = extracted.group()
            print(result, '---------> result')
            temp_prr = float(result) #온도 숫자만 추출하여 비교하기 위함
            print(temp_prr, '--------> temp_prr')

        if len(weather_info4) > 0:
            low_temp_arr = []
            high_temp_arr = []

            for item in weather_info4:
                low_temp_item = item.find("span", attrs={"class":"lowest"}).get_text()[4:]
                high_temp_item = item.find("span", attrs={"class":"highest"}).get_text()[4:]
                
                low_temp_arr.append(low_temp_item)
                high_temp_arr.append(high_temp_item)

            low_temp = low_temp_arr[0]
            high_temp = high_temp_arr[0]

            print(low_temp)
            print(high_temp)

    ############################### 미세먼지 추출 ###############################################################
        
        if len(weather_info3) > 0:
            pm_array = []
            upm_array = []
            pm_status_array = []
            
            for item3 in weather_info3:
            
                # pm = item3.select("li > a > strong")[0].text
                pm = item3.select("li > a > strong")
                pm_array.append(pm)
                pm_status = item3.select("li > a > span") # [미세먼지, 초미세먼지, 자외선, 일몰] 관련 태그 list
                pm_status_array.append(pm_status) # 상태값 금일[미세먼지, 초미세먼지, 자외선, 일몰] 태그 list, 내일[미세먼지, 초미세먼지]

            today_pm_tag = pm_array[0] #금일 미세먼지 등(미세먼지, 초미세먼지, 자외선, 일몰시간) 관련 태그 List          
            tom_pm_tag = pm_array[1] #내일 미세먼지/초미세먼지 관련 태그 List
            today_pm_value_tag = pm_status_array[0] #금일 미세먼지 등 관련 상태값 태그 List
            tom_pm_value_tag = pm_status_array[1] #내일 미세먼지/초미세먼지 상태값 태그 List

            today_pm = today_pm_tag[0].text + ': ' + today_pm_value_tag[0].text #금일 미세먼지 상태
            today_upm = today_pm_tag[1].text + ': ' + today_pm_value_tag[1].text #금일 초미세먼지 상태
            today_uv = today_pm_tag[2].text + ': ' + today_pm_value_tag[2].text #금일 자외선 상태
            today_sunset = today_pm_tag[3].text + '시간' + ': ' + today_pm_value_tag[3].text #금일 일몰시간

            tom_pm = tom_pm_tag[0].text + ': ' + tom_pm_value_tag[0].text #내일 미세먼지 상태
            tom_upm = tom_pm_tag[1].text + ': ' + tom_pm_value_tag[1].text #내일 초미세먼지 상태

    #############################################################################################################            
        if temp_prr > 15 and temp_prr < 20:
            comment = "따뜻한 편이예요."
        elif temp_prr >= 20 and temp_prr < 25:
            comment = "오 따땃하네요~ ^^"
        elif temp_prr >= 25 and temp_prr < 30:
            comment = "조금 더워요;"
        elif temp_prr >= 30 and temp_prr < 35:
            comment = "더워요~~ ㅡㅡ^"
        elif temp_prr >= 35:
            comment = "쩌죽어요 >.<"
        elif temp_prr > 5 and temp_prr <= 11:
            comment = "쌀쌀해요 ~~"
        elif temp_prr > 11 and temp_prr <= 15:
            comment = "봄이네요 ^0^"
        elif temp_prr > 1 and temp_prr <= 5:
            comment = "추워요 ㅡㅡ;."
        elif temp_prr <= 1 and temp_prr >= 0:
            comment = "오우 추워 ~~ "
        elif temp_prr < 0 and temp_prr > -4:
            comment = "정말 추워 ㄷ ㄷ ㄷ "
        elif temp_prr <= -4 and temp_prr > -8:
            comment = "으~~~~~ 추워 >.<  ㄷ ㄷ ㄷ "
        elif temp_prr <= -8:
            comment = "얼어 죽어요~~ >.<  ㄷ ㄷ ㄷ "

        sub_weather1 = location + temp_pr + "(" + status1 + ")" + ", " + status2  + "\n"
        print(sub_weather1, '-------> sub_weather1')
        sub_weather11 = "최저 온도 " + low_temp + " / 최고 온도 " + high_temp + "\n" 
        sub_weather2 = status_auxx + "\n"
        
        sub_title = f"*[ {where} / 내일 ]*" + "\n"
        sub_weather4 = temperature + "\n"
        sub_weather5 = "오전: " + tomm_status1 + ", 오후: " + tomm_status2 + "\n"
        
        sub_weather8 = "##### " + comment + " #####"
        # try:

        sub_weather3 = today_pm + ", " + today_upm + "\n" #금일 미세먼지/초미세먼지 상태
        sub_weather6 = tom_pm + ", " + tom_upm + "\n" #내일 미세먼지/초미세먼지 상태
        sub_weather7 = today_uv + ", " + today_sunset + "\n" #금일 자외선 수치 및 일몰시간

        weather = sub_weather1 + sub_weather11 + sub_weather2 + rain_fall_forcast + sub_weather3\
             + sub_weather7 + "\n" + sub_weather8 + "\n\n" + sub_title + sub_weather4\
                 + sub_weather5 + rain_fall_forcast2 + sub_weather6

        return weather
   
    except Exception as e:
        print(e)
        weather =  "Error가 발생하였습니다. 관리자에게 문의해 주세요~"

        return weather
    
##############################################################################################

async def weather_reply(update, context):
    user = update.effective_user
    user_message = update.message.text
    await update.message.reply_html(
        get_weather(user_message),
        # reply_markup=ForceReply(selective=True),
    )


async def weather_searcher(update, context):
    user = update.effective_user
    user_text_temp = update.message.text.split()
    if user_text_temp[0] == "ㅉ":
        user_text = "덕양구 화정동"
    elif user_text_temp[0] == "ㅉㅈ":
        user_text = "연수구 송도동"
    else:
        print(user_text_temp)
        user_text = ""
        for i in range(1, len(user_text_temp)):
            user_text += user_text_temp[i] + " "
    
    await update.message.reply_markdown(
        get_weather(user_text)  
    )

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build() 
    application.add_handler(MessageHandler(filters.Regex(r'/날씨|/w|ㅉ|ㅉㅈ|/W'), weather_searcher)) #어떤 문자라도 echo 메쏘드로 연결(명령빼고)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()