

__version__ = '1.10.0'
""" 
Date: 28 Jan 2023
"""
import requests
from ratfin import *
import json

## In house variable 
tts_url = 'http://localhost:5003/tts'

import json
class Response:
    """Response for the NLP-pipeline. 
    Possible Entities: [object, furniture, storage, adj_object, people, people_action, placement, position, demonstrative, rpos, p_door, room]
    
    Text from ASR
    Intent from NLU Rasa
    
    Example of how to use Response for NLP Robocup ::

        >>> x = Response()
        >>> print(x)
        Response(
            status_code=0
            text=''
            intent=''
            confidence=0.0
            object=''
            people=''
        )
        >>> x.join_json("{
            \"intent\": \"restaurant_order\", 
            \"object\": \"coca-cola\", 
            \"people\": \"me\",
            \"place\": \"your mum\"
            }")
        >>> print(x)
        Response(
            status_code=0
            text=''
            intent='restaurant_order'
            confidence=0.0
            object='coca-cola'
            people='me'
            place='your mum'
        )
        >>> x.your_mum = "fat"
        >>> print(x)
        Response(
            status_code=0
            text=''
            intent='restaurant_order'
            confidence=0.0
            object='coca-cola'
            people='me'
            place='your mum'
            your_mum = "fat" <--
        )

    """

    def __init__(
        self,
        status: str = "",
        status_code: int = 0,
        text: str = "",
        intent: str = "",
        confidence: float = 0.00,
        object: str = "",
        people: str = "",
        **kwargs  # To handle future attributes
    ):
        self.status_code = status_code
        self.text = text
        self.intent = intent
        self.confidence = confidence
        self.object = object
        self.people = people

        # Store any additional attributes as instance variables
        for key, value in kwargs.items():
            setattr(self, key, value)

    def join_json(self, text: str, verbose = False):
        json_dict = json.loads(text)
        for key, value in json_dict.items():
            setattr(self, key, value)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __str__(self):
        attributes = [
            f'{attr}={getattr(self, attr)!r}'
            for attr in vars(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        ]
        output = '\n\t'.join(attributes)
        return f'''Response(\n\t{output}\n)'''


def speak(text: str = "Hi my name is Walkie",
          voice: str = "en-US-JaneNeural",
          style: str = "normal",
          profanity: str = "2"):
    """Speak text using TTS server. Use sync = False to return immediately."""

    try:
        printclr("synthesizing...","blue")
        
        #* Requesting TTS server  
        x = requests.post(tts_url,
                          json={
                              'text': text,
                              'voice': voice,
                              'style': style,
                              'profanity': profanity
                          })
        return x.json()

    except Exception as e:
        printclr(e, "red")
        return


def ww_listen(intent=True):  # go to ASR server, By-pass wakeword
    try:
        res_json = requests.get("http://localhost:5100/").json()  # asr get
        # print(f"{res_json=}")
        if intent:
            if res_json["status_code"] == 500:
                printclr("Error: Rasa is not ready yet", "red")
                
            else:
                while res_json["confidence"] < 0.62:
                    try:
                        speak("Sorry I didn't get that, could you speak louder or rephrase the sentence?")
                    except:
                        printclr("ERROR: TTS Ofline, Confidence of the response is low","red")
                    res_json = requests.get("http://localhost:5101/").json()  # asr get
        res = Response()
        res.join_json(res_json)
        return res
    except Exception as e:
        printclr(e, "red")


def listen(intent=True):  # go to ASR server, By-pass wakeword
    try:
        res_json = requests.get("http://localhost:5101/").json()  # asr get
        # print(f"{res_json=}")
        if intent:
            if res_json["status_code"] == 500:
                printclr("Error: Rasa is not ready yet", "red")
                
            else:
                while res_json["confidence"] < 0.62:
                    try:
                        speak("Sorry I didn't get that, could you speak louder or rephrase the sentence?")
                    except:
                        printclr("ERROR: TTS Ofline, Confidence of the response is low","red")
                    res_json = requests.get("http://localhost:5101/").json()  # asr get
        res = Response()
        res.join_json(res_json)
        return res
    except Exception as e:
        printclr(e, "red")


def get_intent(predicted_text):
    response = {"recipient_id": "bot", "body": predicted_text}

    #TODO try and except UGLY.......
    #* Get intent
    r = requests.post(url="http://localhost:5005/webhooks/rest/webhook",
                      json={
                          "sender": "bot",
                          "message": predicted_text
                      })
    # printclr(r.json(),"cyan")
    if r.json() == []:  #TODO FIX THIS BULLSHIT
        print("Low confidence level")
        response.update({"confidence": 0})
    else:
        rasa_json = r.json()[0]['text']
        rasa_json = json.loads(rasa_json)
        # printclr(rasa_json,"red")
        # printclr(response,"red")
        response.update(rasa_json)
        # printclr(json.dumps(response, indent=4),"blue")
    # print(response)
    printclr(f"\t{json.dumps(response, indent=4)}", "blue")
    printclr(f"\tlisten() sending back...", "green")
    return response


class EmerStop():

    def __init__(self, name):
        self.name = name
        self.confidence = None
        self.intent = None

    def run(self):
        while True:
            try:
                x = requests.get("http://localhost:5101/").json()
                # print("checking if intent in x")
                # print(repr(x))
                if "intent" in x:
                    # print("in")
                    if x["intent"] == "stop" and x["confidence"] > 0.62:
                        printclr("STOPPINGGGG........", "red")
                        self.confidence = x["confidence"]
                        self.intent = x["intent"]
            except:
                pass

    def clear_status(self):
        self.confidence = None
        self.intent = None


def main():
    # clearterm()
    # import threading, time
    # hi = EmerStop("nlp")
    # t = threading.Thread(target=hi.run, name="EmerStopFlask")
    # t.start()
    # while True:
    #     time.sleep(4)
    #     print(hi.intent, hi.confidence)

    #check

    # for i in range(10):
    #     speak(
    #         text = "WAKE THE FUCK UP",
    #         voice = "en-US-JaneNeural" ,
    #         style = "shouting" # can be shouting, normal

    #     )
    # print("this is speak")
    # print(speak("say stop motherfucker"))
    # print(speak("say "))
    # print(listen())
    # while True:
    # x = dict(ww_listen())
    # print(ww_listen())
    # print(json.dumps(listen(), indent=4))
    # print(json.dumps(ww_listen(), indent=4))
    # if x['intent'] == "stop":
    #     printclr("STOPPINGGGG........","red")
    #     speak("stop")
    pass


main()
# print(ww_listen())
# print(speak("hi there this is a test for speak"))
