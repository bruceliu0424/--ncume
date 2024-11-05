# -*- coding: utf-8 -*-
import speech_recognition as sr

def recognize_speech():
    mic_index = 1  # 替換為指定麥克風索引
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=mic_index) as source:
        print("請說話...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="zh-TW")
        print(f"你說的是: {text}")
        return text
    except sr.UnknownValueError:
        print("無法識別語音")
    except sr.RequestError:
        print("無法連接到語音服務")

def search_keywords(text, keywords):
    for keyword in keywords:
        if keyword in text:
            print(f"找到關鍵字: {keyword}")
            return keyword
    return None

def run_code_by_keyword(keyword):
    if keyword == "開燈":
        print("執行開燈程式")
        # 實際開燈程式碼
    elif keyword == "關燈":
        print("執行關燈程式")
        # 實際關燈程式碼
    else:
        print(f"未知的關鍵字: {keyword}")

keywords = ["開燈", "關燈"]

# 語音轉文字
text = recognize_speech()

# 搜尋關鍵字
found_keyword = search_keywords(text, keywords)

# 如果有關鍵字，執行對應程式碼
if found_keyword:
    run_code_by_keyword(found_keyword)