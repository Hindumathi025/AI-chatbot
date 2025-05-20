from flask import Flask, render_template, request, jsonify, redirect, url_for
import re
import os
from datetime import datetime

app = Flask(__name__)

# Create directory for storing user data
os.makedirs('user_data', exist_ok=True)

# Validation functions
def validate_mobile_number(mobile):
    # Check if it's exactly 10 digits and contains only numbers
    if re.match(r'^\d{10}$', mobile):
        return True
    return False

def validate_email(email):
    # Basic email validation pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email):
        return True
    return False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    current_step = request.json.get('currentStep', 'greeting')
    user_data = request.json.get('userData', {})
    
    response = process_chat(user_message, current_step, user_data)
    
    # Save completed inquiries
    if response.get('next_step') == 'complete' and user_data:
        save_user_data(user_data)
    
    return jsonify(response)

def save_user_data(user_data):
    # Create a timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_data/inquiry_{timestamp}.txt"
    
    # Write user data to file
    with open(filename, 'w') as f:
        f.write("CADD Center Course Inquiry\n")
        f.write("=" * 30 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Name: {user_data.get('name', 'N/A')}\n")
        f.write(f"Mobile: {user_data.get('mobile', 'N/A')}\n")
        f.write(f"Email: {user_data.get('email', 'N/A')}\n")
        f.write(f"Status: {user_data.get('status', 'N/A')}\n")
        f.write(f"Course Interest: {user_data.get('course', 'N/A')}\n")

def process_chat(user_message, current_step, user_data):
    if current_step == 'greeting':
        if any(word in user_message.lower() for word in ['course', 'enquire', 'information']):
            return {
                'message': "I'd be happy to help you with course information! Please provide the following details:\n\n1. Your Name:",
                'next_step': 'name'
            }
        else:
            return {
                'message': "I can help you with course inquiries, fee details, or schedule information. How may I assist you?",
                'next_step': 'greeting'
            }
    
    elif current_step == 'name':
        user_data['name'] = user_message
        return {
            'message': "2. Your Mobile Number:",
            'next_step': 'mobile',
            'userData': user_data
        }
    
    elif current_step == 'mobile':
        if validate_mobile_number(user_message):
            user_data['mobile'] = user_message
            return {
                'message': "3. Your Email ID:",
                'next_step': 'email',
                'userData': user_data
            }
        else:
            return {
                'message': "Invalid mobile number. Please enter exactly 10 digits.",
                'next_step': 'mobile',
                'userData': user_data
            }
    
    elif current_step == 'email':
        if validate_email(user_message):
            user_data['email'] = user_message
            return {
                'message': "4. What's your current status? (Student/Working Professional/Job Seeker/Other)",
                'next_step': 'status',
                'userData': user_data
            }
        else:
            return {
                'message': "Invalid email format. Please enter a valid email address.",
                'next_step': 'email',
                'userData': user_data
            }
    
    elif current_step == 'status':
        user_data['status'] = user_message
        courses_info = (
            "Which courses are you interested in? We offer:\n\n"
            "- Mechanical: AutoCAD, CATIA, SolidWorks, NX CAD, Creo, CAM\n"
            "- Civil: Revit, BIM (Building Information Modeling)\n"
            "- IT: Python, Java, C, C++, Web Design"
        )
        return {
            'message': courses_info,
            'next_step': 'course',
            'userData': user_data
        }
    
    elif current_step == 'course':
        user_data['course'] = user_message
        thank_you_message = (
            "Thank you for providing your details! Our team will contact you soon with more information about the courses you're interested in.\n\n"
            "For immediate assistance or more details, you can visit our center or call us at 7845821665.\n\n"
            "Thank you for your inquiry! Have a great day!"
        )
        return {
            'message': thank_you_message,
            'next_step': 'complete',
            'userData': user_data
        }
    
    else:
        return {
            'message': "How else can I assist you today?",
            'next_step': 'greeting',
            'userData': {}
        }

@app.route('/admin')
def admin():
    # Simple admin page to view inquiries (you may want to add authentication)
    inquiries = []
    for filename in os.listdir('user_data'):
        if filename.startswith('inquiry_'):
            with open(os.path.join('user_data', filename), 'r') as f:
                inquiries.append(f.read())
    
    return render_template('admin.html', inquiries=inquiries)

if __name__ == '__main__':
    app.run(debug=True)