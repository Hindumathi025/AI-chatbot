import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

# LangChain and LangGraph imports
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database functions
INQUIRY_DB_FILE = "inquiry_database.json"

def load_inquiry_database() -> Dict:
    """Load the inquiry database from file."""
    if os.path.exists(INQUIRY_DB_FILE):
        try:
            with open(INQUIRY_DB_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"inquiries": []}
    return {"inquiries": []}

def save_inquiry_database(db: Dict) -> None:
    """Save the inquiry database to file."""
    with open(INQUIRY_DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def check_existing_inquiry(mobile: str, email: str) -> bool:
    """Check if user has already made an inquiry with the same mobile or email."""
    db = load_inquiry_database()
    
    for inquiry in db["inquiries"]:
        if inquiry["mobile"] == mobile or inquiry["email"] == email:
            return True
    return False

def save_inquiry(name: str, mobile: str, email: str, status: str, courses: List[str]) -> None:
    """Save user inquiry to database."""
    db = load_inquiry_database()
    
    new_inquiry = {
        "name": name,
        "mobile": mobile,
        "email": email,
        "status": status,
        "courses": courses,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    db["inquiries"].append(new_inquiry)
    save_inquiry_database(db)

def simulate_typing(text: str) -> None:
    """Simulate typing effect for bot responses."""
    print("Bairo is typing...", end="\r")
    time.sleep(1)  # Simulate typing delay
    print(" " * 20, end="\r")  # Clear the typing indicator
    print(f"Bairo: {text}")

# ----- Tools for CADD Center Bot ----- 
@tool
def collect_user_info(name: str = "", mobile: str = "", email: str = "", status: str = "") -> str:
    """
    Collects and validates user information.
    
    Args:
        name: User's full name
        mobile: User's mobile number
        email: User's email address
        status: User's current status (Student/Working Professional/Job Seeker)
    
    Returns:
        str: Confirmation of collected information
    """
    if not name or not mobile or not email or not status:
        return "Please provide all required information."
    
    # Check if user has already made an inquiry with the same mobile or email
    if check_existing_inquiry(mobile, email):
        return "This mobile number or email is already registered for an inquiry."
    
    return f"Information collected - Name: {name}, Mobile: {mobile}, Email: {email}, Status: {status}"

@tool
def get_course_info(course_category: str) -> str:
    """
    Provides information about courses in the specified category.
    
    Args:
        course_category: Category of courses (mechanical, civil, it)
    
    Returns:
        str: List of courses in the category
    """
    courses = {
        "mechanical": ["AutoCAD", "CATIA", "SolidWorks", "NX CAD", "Creo", "CAM"],
        "civil": ["Revit", "BIM (Building Information Modeling)"],
        "it": ["Python", "Java", "C", "C++", "Web Design"]
    }
    
    if course_category.lower() in courses:
        return f"Courses in {course_category}: {', '.join(courses[course_category.lower()])}"
    else:
        return "Category not found. Available categories: mechanical, civil, it"

@tool
def save_inquiry_info(name: str, mobile: str, email: str, status: str, courses: str) -> str:
    """
    Saves the user inquiry to the database.
    
    Args:
        name: User's name
        mobile: User's mobile number
        email: User's email address
        status: User's current status
        courses: Courses the user is interested in (comma-separated)
    
    Returns:
        str: Confirmation message
    """
    course_list = [course.strip() for course in courses.split(",")]
    save_inquiry(name, mobile, email, status, course_list)
    return "Your inquiry has been saved. Our team will contact you soon."

@tool
def get_contact_details() -> str:
    """Returns contact details for the CADD center."""
    return "For more details, please contact us at 7845821665 or visit our center in person."

@tool
def say_hello(name: str = "there") -> str:
    """Greets the user by name."""
    return f"Hello {name}, welcome to CADD Center Assistance! How can I help you today?"

def main():
    # Setup LangChain components
    model = ChatOpenAI(
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE"),
    )
    
    # Set up tools for the agent
    tools = [
        collect_user_info,
        get_course_info,
        save_inquiry_info,
        get_contact_details,
        say_hello
    ]
    
    # Create the agent with the React framework
    agent_executor = create_react_agent(model, tools)
    
    print("\n" + "="*50)
    print("🤖 CADD Center Assistant Bot - Bairo")
    print("="*50)
    
    # Initial greeting
    print("Bairo is typing...", end="\r")
    time.sleep(1)
    print(" " * 20, end="\r")
    print("Bairo: Welcome to the CADD Center Assistance! How can I help you today?")
    
    # Message history to maintain context
    messages = [AIMessage(content="Welcome to the CADD Center Assistance! How can I help you today?")]
    
    # User information storage
    user_info = {
        "name": "",
        "mobile": "",
        "email": "",
        "status": "",
        "courses": []
    }
    
    # Conversation state
    state = "greeting"
    
    while True:
        user_input = input("\nYou: ").strip()
        messages.append(HumanMessage(content=user_input))
        
        # Handle exit commands
        if user_input.lower() in ["bye", "exit", "quit", "thank you"]:
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: Thank you for your inquiry! Have a great day!")
            break
        
        # Simple state machine for guided conversation
        if state == "greeting" and any(word in user_input.lower() for word in ["enquire", "course", "information", "hi", "hello"]):
            state = "collect_name"
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: I'd be happy to help you with course information! Please provide the following details:")
            
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: 1. Your Name:")
            continue
            
        elif state == "collect_name":
            user_info["name"] = user_input
            state = "collect_mobile"
            
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: 2. Your Mobile Number:")
            continue
            
        elif state == "collect_mobile":
            user_info["mobile"] = user_input
            state = "collect_email"
            
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: 3. Your Email ID:")
            continue
            
        elif state == "collect_email":
            user_info["email"] = user_input
            
            # Check if user has already made an inquiry
            if check_existing_inquiry(user_info["mobile"], user_info["email"]):
                print("Bairo is typing...", end="\r")
                time.sleep(1)
                print(" " * 20, end="\r")
                print("Bairo: I notice you've inquired with us before using this mobile number or email.")
                print("Bairo is typing...", end="\r")
                time.sleep(1)
                print(" " * 20, end="\r")
                print("Bairo: Our team will contact you soon with more information.")
                print("Bairo is typing...", end="\r")
                time.sleep(1)
                print(" " * 20, end="\r")
                print("Bairo: Thank you for your interest! Have a great day!")
                break
                
            state = "collect_status"
            
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: 4. What's your current status? (Student/Working Professional/Job Seeker/Other)")
            continue
            
        elif state == "collect_status":
            user_info["status"] = user_input
            state = "collect_courses"
            
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: Which courses are you interested in? We offer:")
            
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: - Mechanical: AutoCAD, CATIA, SolidWorks, NX CAD, Creo, CAM")
            
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: - Civil: Revit, BIM (Building Information Modeling)")
            
            print("Bairo is typing...", end="\r")
            time.sleep(1)
            print(" " * 20, end="\r")
            print("Bairo: - IT: Python, Java, C, C++, Web Design")
            continue
            
        elif state == "collect_courses":
            course_interest = user_input.lower()
            
            # Process the input through the LangChain agent for fee/syllabus questions
            if any(word in course_interest for word in ["fee", "cost", "price", "syllabus", "curriculum", "duration", "time"]):
                print("Bairo is typing...", end="\r")
                time.sleep(1)
                print(" " * 20, end="\r")
                
                if any(word in course_interest for word in ["fee", "cost", "price"]):
                    print("Bairo: For detailed information about fees structure, we recommend visiting our center in person.")
                elif any(word in course_interest for word in ["syllabus", "curriculum"]):
                    print("Bairo: For detailed course syllabus and curriculum, we recommend visiting our center.")
                elif any(word in course_interest for word in ["duration", "time", "long"]):
                    print("Bairo: The duration varies based on the course and your learning pace. For specific duration details, please visit our center.")
                
                # Use the agent for the next response
                print("Bairo is typing...", end="\r")
                try:
                    for chunk in agent_executor.stream({"messages": messages}):
                        if "agent" in chunk and "messages" in chunk["agent"]:
                            for message in chunk["agent"]["messages"]:
                                if isinstance(message, AIMessage):
                                    messages.append(message)
                    print(" " * 20, end="\r")
                    print(f"Bairo: Please contact us at 7845821665 for more details.")
                except Exception as e:
                    print(" " * 20, end="\r")
                    print(f"Bairo: Please contact us at 7845821665 for more details.")
                
                # Save the inquiry
                courses = []
                for category in ["mechanical", "civil", "it"]:
                    if category in course_interest:
                        courses.append(f"{category.capitalize()} Courses")
                
                if not courses:
                    courses = ["General Course Inquiry"]
                
                save_inquiry(user_info["name"], user_info["mobile"], user_info["email"], user_info["status"], courses)
                
                print("Bairo is typing...", end="\r")
                time.sleep(1)
                print(" " * 20, end="\r")
                print("Bairo: Thank you for providing your details! Our team will contact you soon with more information.")
                
                print("Bairo is typing...", end="\r")
                time.sleep(1)
                print(" " * 20, end="\r")
                print("Bairo: Thank you for your inquiry! Have a great day!")
                break
            else:
                # Identify courses mentioned
                courses = []
                all_courses = {
                    "mechanical": ["AutoCAD", "CATIA", "SolidWorks", "NX CAD", "Creo", "CAM"],
                    "civil": ["Revit", "BIM"],
                    "it": ["Python", "Java", "C", "C++", "Web Design"]
                }
                
                for category, course_list in all_courses.items():
                    if category in course_interest:
                        courses.append(f"{category.capitalize()} Courses")
                    else:
                        for course in course_list:
                            if course.lower() in course_interest.lower():
                                courses.append(course)
                
                if not courses:
                    courses = ["General Course Inquiry"]
                
                # Save the inquiry
                save_inquiry(user_info["name"], user_info["mobile"], user_info["email"], user_info["status"], courses)
                
                # Use the agent for the final response
                print("Bairo is typing...", end="\r")
                time.sleep(1)
                print(" " * 20, end="\r")
                print("Bairo: Thank you for providing your details! Our team will contact you soon with more information about the courses you're interested in.")
                
                print("Bairo is typing...", end="\r")
                time.sleep(1)
                print(" " * 20, end="\r")
                print("Bairo: For immediate assistance or more details, you can visit our center or call us at 7845821665.")
                
                print("Bairo is typing...", end="\r")
                time.sleep(1)
                print(" " * 20, end="\r")
                print("Bairo: Thank you for your inquiry! Have a great day!")
                break
        else:
            # Use the LangChain agent for general responses
            print("Bairo is typing...", end="\r")
            
            try:
                for chunk in agent_executor.stream({"messages": messages}):
                    if "agent" in chunk and "messages" in chunk["agent"]:
                        for message in chunk["agent"]["messages"]:
                            if isinstance(message, AIMessage):
                                messages.append(message)
                                response = message.content
                print(" " * 20, end="\r")
                print(f"Bairo: {response}")
            except Exception as e:
                print(" " * 20, end="\r")
                print(f"Bairo: I'm Bairo, the CADD Center assistant. I can help you with course inquiries. Are you interested in learning about our courses?")

if __name__ == "__main__":
    main()