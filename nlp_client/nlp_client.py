import requests
from ratfin import *

def speak(text: str) :
    try :
        url = 'http://localhost:5003/tts'
        x = requests.post(url, json={'text':text})
        # printclr(e,"red")
        return x.json()
        # return "Syntizied"

    except Exception as e:
        printclr(e,"red")


def ww_listen(): # go to Wakeword server
    try:
        response = requests.get("http://localhost:5100/").json() # wakeword get
        while response["confidence"] < 0.62:
            speak("Sorry I didn't get that, could you speak louder or rephrase the sentence?")
            response = requests.get("http://localhost:5101/").json() # asr get
        return response
    except Exception as e:
        printclr(e,"red")

def listen(return_json=False): # go to ASR server, By-pass wakeword
    try:
        response = requests.get("http://localhost:5101/").json() # asr get
        while response["confidence"] < 0.62:
            speak("Sorry I didn't get that, could you speak louder or rephrase the sentence?")
            response = requests.get("http://localhost:5101/").json() # asr get
        return response
    except Exception as e:
        printclr(e,"red")

# import time
# import json 
# start = time.time()
# time.sleep(1)

# print(time.time() - start)
def main():
    clearterm() 

    # print("this is speak")
    # print(speak("say stop motherfucker"))
    print(speak("say "))
    # print(listen())
    # while True:
        # x = dict(ww_listen())
    # print(ww_listen())
    print(json.dumps(listen(), indent=4))
    print(json.dumps(ww_listen(), indent=4))
        # if x['intent'] == "stop":
        #     printclr("STOPPINGGGG........","red")
        #     speak("stop")

main()
    # print(ww_listen())
# print(speak("hi there this is a test for speak"))
