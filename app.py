import subprocess
import os
import signal
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from chat_assistant import get_chat_response
import bcrypt
from pymongo import MongoClient
import cv2

#Flask App Configuration
app = Flask(__name__)
app.secret_key = "YourSecretKey" 

# MongoDB connection
MONGO_URL = 
client = MongoClient(MONGO_URL)
db = client['total_records']
records = db['register']

# Load the Haar cascade for frontal face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_face():
    """Accurately detect a face using OpenCV."""
    cap = cv2.VideoCapture(1)  # Use the default camera (index 0)
    detected = False

    while not detected:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to grayscale for better detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(80, 80))
        
        for (x, y, w, h) in faces:
            aspect_ratio = w / float(h)
            
            # Strict validation for face detection (reject body parts by checking typical face properties)
            if 0.75 < aspect_ratio < 1.3 and w > 80 and h > 80:
                detected = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, "Face Detected!", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        cv2.imshow("Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()
    return detected


@app.route("/", methods=["GET", "POST"])
def face_detection():
    """Initial page for face detection."""
    message = ""
    if request.method == "POST":
        if detect_face():
            return redirect(url_for("register"))
        else:
            message = "Face not detected. Please try again."
    return render_template("face_detection.html", message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page."""
    if "email" in session:
        return redirect(url_for("dashboard"))

    message = ""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if not name.strip():
            message = "Full name is required."
        elif password1 != password2:
            message = "Passwords must match."
        elif records.find_one({"email": email}):
            message = "Email already exists."
        else:
            hashed = bcrypt.hashpw(password2.encode("utf-8"), bcrypt.gensalt())
            records.insert_one({"name": name, "email": email, "password": hashed})
            session["email"] = email
            session["name"] = name
            return redirect(url_for("dashboard"))

    return render_template("register.html", message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if "email" in session:
        return redirect(url_for("dashboard"))

    message = ""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = records.find_one({"email": email})
        if email_found and bcrypt.checkpw(password.encode("utf-8"), email_found["password"]):
            session["email"] = email
            session["name"] = email_found.get("name", "User")
            return redirect(url_for("dashboard"))
        else:
            message = "Invalid credentials. Please try again."

    return render_template("login.html", message=message)


@app.route("/dashboard")
def dashboard():
    """Dashboard page."""
    if "email" in session:
        name = session.get("name", "User")
        return render_template("dashboard.html", name=name)
    return redirect(url_for("login"))


@app.route("/voice_assistant_base", methods=["GET","POST"])
def voice_assistant_base():
     """Launch the assistant features."""
     if "email" not in session:
         return redirect(url_for("login"))
     return render_template("voice_assistant_base.html")


process = None  # Global variable to track the subprocess
@app.route("/voice_assistant", methods=["GET", "POST"])
def voice_assistant():
    """Render Voice Assistant page and trigger/stop script on button click."""
    global process

    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if request.form.get("start") == "true":
            script_path = os.path.join(os.getcwd(), "voice_assistant.py")
            try:
                if process is None or process.poll() is not None:  # Ensure no duplicate processes
                    process = subprocess.Popen(["python", script_path])
                    flash("Voice Assistant launched successfully!", "success")
                else:
                    flash("Voice Assistant is already running.", "info")
            except Exception as e:
                flash(f"Failed to launch Voice Assistant: {str(e)}", "danger")

        elif request.form.get("stop") == "true":
            if process and process.poll() is None:  # Check if process is running
                os.kill(process.pid, signal.SIGTERM)  # Terminate the process
                process = None
                flash("Voice Assistant stopped.", "warning")
            else:
                flash("Voice Assistant is not running.", "info")

        return redirect(url_for("voice_assistant"))  # Prevent duplicate execution on refresh

    return render_template("voice_assistant.html")


# Route for chat assistant UI
@app.route("/chat_assistant")
def chat_assistant():
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template("chat_assistant.html")

# Route to handle chat messages
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response":"Please enter a message.","redirect":None})
    chat_response = get_chat_response(user_message)

    # If response has a redirect, return it
    return jsonify(chat_response)


@app.route("/virtual_mouse", methods=["GET"])
def virtual_mouse():
     """Launch the virtual mouse features."""
     if "email" not in session:
         return redirect(url_for("login"))
     return render_template("virtual_mouse.html")


@app.route("/presentation_mode", methods=["GET", "POST"])
def presentation_mode():
    """Handle Presentation Mode logic."""
    if "email" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        script_path = os.path.join(os.getcwd(), "presentation.py")
        try:
            subprocess.Popen(["python", script_path])
            message = "Presentation Mode Activated!"
        except Exception as e:
            message = f"Failed to activate Presentation Mode: {str(e)}"

    return render_template("presentation_mode.html", message=message)


@app.route("/gaming_mode", methods=["GET", "POST"])
def gaming_mode():
    """Handle Gaming Mode logic."""
    if "email" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        script_path = os.path.join(os.getcwd(), "game.py")
        try:
            # Launch the game script
            subprocess.Popen(["python", script_path])
            
            # Optional: Launch external game if needed
            game_path = r"C:\Users\kajol jewellers\OneDrive\Desktop\Subway Surf.lnk"
            subprocess.Popen([game_path], shell=True)

            message = "Gaming Mode Activated!"
        except Exception as e:
            message = f"Failed to activate Gaming Mode: {str(e)}"

    return render_template("gaming_mode.html", message=message)


@app.route("/basic_mode", methods=["GET", "POST"])
def basic_mode():
    """Render Basic Mode page and trigger basic.py on Start button."""
    if "email" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        script_path = os.path.join(os.getcwd(), "basic.py")
        try:
            subprocess.Popen(["python", script_path])
            message = "Basic Mode Activated!"
        except Exception as e:
            message = f"Failed to activate Basic Mode: {str(e)}"

    return render_template("basic_mode.html", message=message)


@app.route("/virtual_keyboard", methods=["GET", "POST"])
def virtual_keyboard():
    """Render Virtual Keyboard page and trigger script on Start button."""
    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("start") == "true":
        script_path = os.path.join(os.getcwd(), "virtual_keyboard.py")
        try:
            subprocess.Popen(["python", script_path])
            session["message"] = "Virtual Keyboard Activated!"
        except Exception as e:
            session["message"] = f"Failed to launch Virtual Keyboard: {str(e)}"
        return redirect(url_for("virtual_keyboard"))  # Redirect to prevent form resubmission

    message = session.pop("message", "")
    return render_template("virtual_keyboard.html", message=message)


@app.route("/logout")
def logout():
    """Logout and clear session."""
    session.pop("email", None)
    session.pop("name", None)
    return redirect(url_for("login"))

#Start the Flask App
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False) 
