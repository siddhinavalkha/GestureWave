import webbrowser
import wikipedia
import datetime
import pywhatkit
from fuzzywuzzy import process  #for matching user messages with known commands.
import screen_brightness_control as sbc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Predefined chatbot responses and system commands
commands = {
    "hello": "Hi there! How can I assist you? 😊",
    "how are you": "I'm just a chatbot, but I'm doing great! 🚀",
    "your name": "I'm GestureWave Chat Assistant!",
    "bye": "Goodbye! Have a great day! 👋",
    "help": "Sure! You can ask me anything about GestureWave.",

    # GestureWave Info
    "what is gesturewave": "GestureWave is an AI-powered gesture control app that allows users to control their system using hand gestures and voice commands.",
    "features": "GestureWave includes Virtual Mouse, Virtual Keyboard, Voice Assistant, Gesture-based Presentation Mode, and Gaming Mode.",
    "supported platforms": "GestureWave currently supports Windows and macOS.",
    "requirements": "You need a webcam for hand gesture recognition and a microphone for voice commands.",

    # Direct Navigation to Virtual Modes
    "open basic mode": "/basic_mode",
    "open virtual keyboard": "/virtual_keyboard",
    "open presentation mode": "/presentation_mode",
    "open gaming mode": "/gaming_mode",
    "open voice assistant": "/voice_assistant",
}

# Gesture List
gestures_info = {
    "Virtual Keyboard Mode": [
        "Select a key – Pinch index finger and thumb.",
        "Move cursor – Use index finger to move."
    ],
    "Virtual Mouse Mode (Presentation)": [
        "Move forward (next slide) – Pinky finger up.",
        "Move backward (previous slide) – Thumb out.",
        "Pointer – Index and middle finger up.",
        "Annotation Mode – Index finger up.",
        "Clear annotations – Three fingers up."
    ],
    "Virtual Mouse Mode (Gaming)": [
        "Jump – Index finger up.",
        "Crouch – Fist.",
        "Move Left – Raise left hand.",
        "Move Right – Raise right hand."
    ],
    "Virtual Mouse Mode (Basic)": [
        "Move Cursor – Index and middle finger up.",
        "Stop Cursor – Index, middle finger, and thumb up.",
        "Right Click – Fold index finger, keep middle finger up.",
        "Left Click – Index finger up, middle finger folded.",
        "Take Screenshot – Fist.",
        "Double Click – Index, middle finger, and thumb closed."
    ]
}

def send_email(subject, body, to_email):
    from_email = "snavalkha25@gmail.com"       # Replace with your email
    from_password = "lxhx qane nqhd kbws"    # Use an app password for security

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # For Gmail
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

#main logic
def get_chat_response(user_message):
    """
    Get chatbot response and handle system commands with fuzzy matching.

    :param user_message: str - The message from the user
    :return: dict - {"response": str, "redirect": str or None}
    """
    user_message = user_message.lower().strip()

    # ✅ Control Brightness
    if "increase brightness" in user_message:
        try:
            current_brightness = sbc.get_brightness()[0]
            new_brightness = min(100, current_brightness + 10)
            sbc.set_brightness(new_brightness)
            return {"response": f"Increasing brightness to {new_brightness}%...", "redirect": None}
        except:
            return {"response": "Brightness control is not supported on your device.", "redirect": None}

    if "decrease brightness" in user_message:
        try:
            current_brightness = sbc.get_brightness()[0]
            new_brightness = max(0, current_brightness - 10)
            sbc.set_brightness(new_brightness)
            return {"response": f"Decreasing brightness to {new_brightness}%...", "redirect": None}
        except:
            return {"response": "Brightness control is not supported on your device.", "redirect": None}

    # Check for gesture-related queries
    if "gesture list" in user_message or "gestures" in user_message:
        response = "**Here are the gestures you can use in different modes:**\n"
        for mode, gestures in gestures_info.items():
            response += f"\n**{mode}:**\n" + "\n".join(f"- {gesture}" for gesture in gestures) + "\n"
        return {"response": response, "redirect": None}

    # Special Commands
    if "time" in user_message:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return {"response": f"The current time is {current_time}.", "redirect": None}

    if "wikipedia" in user_message:
        search_query = user_message.replace("search wikipedia", "").strip()
        if search_query:
            try:
                summary = wikipedia.summary(search_query, sentences=2)
                return {"response": f"According to Wikipedia: {summary}", "redirect": None}
            except wikipedia.exceptions.DisambiguationError as e:
                return {"response": f"Multiple results found. Be more specific: {e.options[:5]}", "redirect": None}
            except wikipedia.exceptions.PageError:
                return {"response": "No matching Wikipedia page found.", "redirect": None}
        return {"response": "Please specify what you want to search on Wikipedia.", "redirect": None}

    if "google" in user_message:
        search_query = user_message.replace("search google", "").strip()
        if search_query:
            url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            webbrowser.open(url)
            return {"response": f"Searching Google for '{search_query}'...", "redirect": None}
        return {"response": "Please specify what you want to search on Google.", "redirect": None}

    if "youtube" in user_message:
        if "play" in user_message:
            video_query = user_message.replace("play on youtube", "").strip()
            if video_query:
                pywhatkit.playonyt(video_query)
                return {"response": f"Playing '{video_query}' on YouTube...", "redirect": None}
            return {"response": "Please specify the song or video you want to play on YouTube.", "redirect": None}
        webbrowser.open("https://www.youtube.com")
        return {"response": "Opening YouTube...", "redirect": None}

    if "send email" in user_message:
        try:
            subject = "GestureWave Notification"
            body = "This is a test email sent from GestureWave Chat Assistant."
            recipient = "recipient@example.com"

            success = send_email(subject, body, recipient)
            if success:
                return {"response": "Email sent successfully! 📧", "redirect": None}
            else:
                return {"response": "Failed to send email. ❌", "redirect": None}
        except Exception as e:
            return {"response": f"An error occurred while sending email: {str(e)}", "redirect": None}

    # Find the best match for user input
    best_match, confidence = process.extractOne(user_message, commands.keys())

    if confidence > 70:
        return {"response": commands[best_match], "redirect": commands.get(best_match, None)}

    return {"response": "I'm not sure about that. Can you rephrase?", "redirect": None}
