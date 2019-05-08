import time

import speech_recognition as sr





class SpeechRecognizer5000():

    def __init__(self,  trigger_function, *args):
        self.r = sr.Recognizer()
        self.m = sr.Microphone()
        self.stopListeningFunc = None
        self.trigger_function = trigger_function
        self.trigger_args = args


    def startListening(self):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

        self.stopListeningFunc = self.r.listen_in_background(self.m, self.callback)
        print("Started listening")


    def stopListening(self):

        if self.stopListeningFunc == None:
            print("Error: startListening must be called before stopListening")
            return

        self.stopListeningFunc(wait_for_stop=False)
        print("Stopped listening")


    # this is called from the background thread
    def callback(self, recognizer, audio):
        # received audio data, now we'll recognize it using Google Speech Recognition
        print("CB")
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            phrase = recognizer.recognize_google(audio)
            print("Google Speech Recognition thinks you said " + phrase)
            self.run_trigger(phrase)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


    def run_trigger(self, phrase):

        #todo: purkka
        str = "self.trigger_function(phrase, "
        if len(self.trigger_args) != 0:
            for i in range(len(self.trigger_args)):
                str += "self.trigger_args[{}]".format(i) + ","
                #print(i)

            str = str[:-1]

        str += ")"
        try:
            eval(str)
        except TypeError:
            print("Error: Too many arguments given for trigger_function in constructor")





if __name__ == '__main__':


    s = SpeechRecognizer5000()
    s.startListening()

    while True:
        print("Main loop")
        time.sleep(3)
