import speech_recognition as sr
from colorama import Fore, Style

class AudioManager:
    def __init__(self):
        """
        Initialize the recognizer. 
        We use the SpeechRecognition library which acts as a wrapper 
        around various audio processing APIs.
        """
        self.recognizer = sr.Recognizer()

    def listen_and_transcribe(self):
        """
        Listens to the microphone and returns the text.
        """
        try:
            # We use the default system microphone
            with sr.Microphone() as source:
                print(f"{Fore.YELLOW}Listening... (Speak now){Style.RESET_ALL}")
                
                # adjust_for_ambient_noise helps the model distinguish 
                # between your voice and background static.
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen to the audio input
                # timeout=15 means if no one speaks for 15 seconds, it stops waiting.
                audio = self.recognizer.listen(source, timeout=15)
                
                print(f"{Fore.CYAN}Processing audio...{Style.RESET_ALL}")

                # recognize_google uses Google's free web API to convert speech to text.
                # For production, you might use 'whisper' or a paid API.
                text = self.recognizer.recognize_google(audio)
                
                print(f"{Fore.GREEN}You said: {text}{Style.RESET_ALL}")
                return text

        except sr.WaitTimeoutError:
            print(f"{Fore.RED}No speech detected within timeout period.{Style.RESET_ALL}")
            return None
        except sr.UnknownValueError:
            print(f"{Fore.RED}Could not understand audio.{Style.RESET_ALL}")
            return None
        except sr.RequestError as e:
            print(f"{Fore.RED}Could not request results; {e}{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
            return None