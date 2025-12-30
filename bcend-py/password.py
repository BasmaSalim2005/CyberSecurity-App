import math
import string 
import google.generativeai as genai

# Configure Gemini API (use your API key)
genai.configure(api_key="AIzaSyD9OVS0FF3B8V__6XDI0BeayM3URb_iY6g")

def check_common_pw(password):
    try:
        with open("templates/assets/common_passwords.txt","r") as f :
            common = f.read().splitlines()
        if password in common:
            return True
    except FileNotFoundError:
        pass  # If file not found, assume not common
    return False

def calc_entropy(password):
    charset_size = 0
    if any(c in string.ascii_lowercase for c in password):
        charset_size += 26
    if any(c in string.ascii_uppercase for c in password):
        charset_size += 26
    if any(c in string.digits for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += 32
    if any(c.isspace for c in password):
        charset_size += 1

    return len(password) * math.log2(charset_size) if charset_size > 0 else 0

def check_pw_strength(password):
    if check_common_pw(password):
        return "Very Weak: Found in Common password List", 0
    
    if len(password) < 8:
        return "Weak", 0
    
    entropy = calc_entropy(password)
    if entropy < 28:
        strength = "Very Weak: Low entropy"
    elif entropy < 36:
        strength = "Weak: Low entropy"
    elif entropy < 60:
        strength = "Moderate: Moderate entropy"
    elif entropy < 80:
        strength = "Medium: Moderate entropy"
    else:
        strength = "Strong: High entropy"

    return strength, entropy

