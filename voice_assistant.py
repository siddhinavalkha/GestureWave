import random
import webbrowser
import pyttsx3
import speech_recognition as sr
import keyboard
import pyautogui
from datetime import datetime
from googletrans import Translator, LANGUAGES
import wikipedia
import psutil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Initialize voice engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

# Initialize translator
translator = Translator()

# Function to speak text
def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# Function to listen and recognize speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("\n🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            
            print("🔍 Recognizing...")
            command = recognizer.recognize_google(audio).lower()
            print(f"✅ Recognized: {command}")
            return command
        
        except sr.UnknownValueError:
            print("⚠ Could not understand the audio")
            return None
        except sr.RequestError:
            print("⚠ Speech recognition service unavailable")
            return None
        except Exception as e:
            print(f"⚠ Microphone error: {e}")
            return None

# Function to list available languages for translation
def list_languages():
    speak("Here are the supported languages for translation:")
    for code, language in LANGUAGES.items():
        print(f"{language.capitalize()} ({code})")
    speak("Check the console for the full list of languages.")

# Function to translate and speak translation
def voice_translate():
    list_languages()  # List supported languages
    speak("Which language do you want to translate to?")
    target_language = listen()

    if not target_language:
        return

    # Get language code from the LANGUAGES dictionary
    lang_code = next((code for code, name in LANGUAGES.items() if name.lower() == target_language), None)

    if not lang_code:
        speak("Sorry, I couldn't find that language. Please try again.")
        return

    speak(f"Okay, translating to {target_language}. Please speak now.")

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak now:")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"🔊 You said: {text}")

            # Translate text
            translated_text = translator.translate(text, dest=lang_code)
            translated_output = translated_text.text
            print(f"🌐 Translated: {translated_output}")

            # Speak the translated text
            speak(f"The translation is: {translated_output}")

        except Exception as e:
            speak(f"An error occurred: {e}")

# Function to search Wikipedia
def search_wikipedia(query):
    speak(f"Searching Wikipedia for {query}...")
    try:
        result = wikipedia.summary(query, sentences=2)
        speak(f"According to Wikipedia, {result}")
        webbrowser.open(f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")
    except wikipedia.DisambiguationError as e:
        speak(f"The query is ambiguous. Did you mean: {', '.join(e.options[:3])}?")
    except wikipedia.PageError:
        speak("The page does not exist.")
    except Exception as e:
        speak(f"An error occurred: {e}")

# Function to open modes
def open_mode(mode_name, url):
    speak(f"Opening {mode_name}...")
    webbrowser.open(url)

# Function to tell a joke
def tell_joke():
    jokes = [
        "Why don't skeletons fight each other? They don't have the guts.",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!"
    ]
    speak(random.choice(jokes))

# Function to check battery status
def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        speak(f"The battery is currently at {battery.percent} percent.")
    else:
        speak("Battery information is not available.")

# Function to control system volume
def set_volume(level):
    try:
        level = max(0, min(level, 100))  # Ensure valid range
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        speak(f"Volume set to {level} percent.")
    except Exception:
        speak("Unable to adjust volume. Please check your audio settings.")

def play_youtube_video(query):
    speak(f"Searching YouTube for {query}")
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(search_url)

# YouTube video control functions
def play_pause_video():
    pyautogui.press('k')
    speak("Toggled play and pause.")

def next_10_sec():
    pyautogui.press('l')
    speak("Forwarded 10 seconds.")

def previous_10_sec():
    pyautogui.press('j')
    speak("Rewinded 10 seconds.")

def mute_video():
    pyautogui.press('m')
    speak("Muted or unmuted the video.")

def fullscreen_video():
    pyautogui.press('f')
    speak("Toggled fullscreen mode.")

def volume_up_video():
    pyautogui.press('up')
    speak("Increased volume.")

def volume_down_video():
    pyautogui.press('down')
    speak("Decreased volume.")

# Main function
def main():
    speak("Hello! How can I assist you today?")
    
    while True:
        if keyboard.is_pressed('q'):  # Press 'q' to quit
            speak("Goodbye! Have a great day.")
            break

        print("\n⏳ Waiting for a command...")
        command = listen()

        if command:
            print(f"🎯 Processing Command: {command}")  # Debugging output

            if "wikipedia" in command:
                search_wikipedia(command.replace("wikipedia", "").strip())
            elif "play" in command and "on youtube" in command:
                # Extract video name
                video_query = command.replace("play", "").replace("on youtube", "").strip()
                if video_query:
                    play_youtube_video(video_query)
                else:
                    speak("Please say the name of the video you want to play on YouTube.")
            elif "pause video" in command or "play video" in command:
                play_pause_video()
            elif "forward" in command or "next 10 seconds" in command:
                next_10_sec()
            elif "rewind" in command or "previous 10 seconds" in command:
                previous_10_sec()
            elif "mute" in command:
                mute_video()
            elif "fullscreen" in command:
                fullscreen_video()
            elif "increase volume" in command or "volume up" in command:
                volume_up_video()
            elif "decrease volume" in command or "volume down" in command:
                volume_down_video()
            elif "open presentation mode" in command:
                open_mode("Presentation Mode", "http://127.0.0.1:5000/presentation_mode")
            elif "open gaming mode" in command:
                open_mode("Gaming Mode", "http://127.0.0.1:5000/gaming_mode")
            elif "open basic mode" in command:
                open_mode("Basic Mode", "http://127.0.0.1:5000/basic_mode")
            elif "open virtual keyboard" in command:
                open_mode("Virtual Keyboard", "http://127.0.0.1:5000/virtual_keyboard")
            elif "translate" in command:  # Fixed 'query' to 'command'
                voice_translate()
            elif "time" in command:
                now = datetime.now().strftime("%I:%M %p")
                speak(f"The current time is {now}.")
            elif "date" in command:
                today = datetime.now().strftime("%A, %B %d, %Y")
                speak(f"Today's date is {today}.")
            elif "joke" in command:
                tell_joke()
            elif "battery" in command:
                get_battery_status()
            elif "volume" in command:
                digits = ''.join(filter(str.isdigit, command))  # Extract numbers
                if digits:
                    set_volume(int(digits))
                else:
                    speak("Please specify a volume level.")
            elif "exit" in command or "quit" in command:
                speak("Goodbye!")
                break
            else:
                speak("Sorry, I didn't understand that command.")

if __name__ == "__main__":
    main() 