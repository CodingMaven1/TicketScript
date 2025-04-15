import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
YOUR_PHONE_NUMBER = os.getenv('YOUR_PHONE_NUMBER')

# Target dates and teams
TARGET_DATES = ['Apr 24', 'May 3', 'May 13']
TARGET_TEAMS = ['Rajasthan Royals', 'Chennai Super Kings', 'Sunrisers Hyderabad']
URL = 'https://shop.royalchallengers.com/ticket'

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        # Create a ChromeDriverManager instance
        driver_manager = ChromeDriverManager()
        
        # Install and get the path
        base_path = driver_manager.install()
        
        # Determine the correct chromedriver path
        driver_dir = os.path.dirname(base_path)
        driver_path = None
        
        # Look for the actual chromedriver executable
        for file in os.listdir(driver_dir):
            if file == 'chromedriver' or (file.startswith('chromedriver') and 
                                          'NOTICES' not in file and 
                                          '.zip' not in file):
                driver_path = os.path.join(driver_dir, file)
                # On Mac, the executable is often in a subdirectory
                if os.path.isdir(driver_path):
                    for subfile in os.listdir(driver_path):
                        if subfile == 'chromedriver':
                            driver_path = os.path.join(driver_path, subfile)
                            break
                break
        
        # If we couldn't find it via the loop, try a direct path for Mac
        if not driver_path or not os.path.exists(driver_path):
            possible_path = os.path.join(driver_dir, 'chromedriver-mac-x64', 'chromedriver')
            if os.path.exists(possible_path):
                driver_path = possible_path
        
        print(f"Using ChromeDriver path: {driver_path}")
        
        # Verify the driver file exists and is executable
        if not os.path.exists(driver_path):
            raise FileNotFoundError(f"ChromeDriver not found at {driver_path}")
        
        if not os.access(driver_path, os.X_OK):
            print(f"Making ChromeDriver executable: {driver_path}")
            os.chmod(driver_path, 0o755)
        
        # Create the service and driver
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    except Exception as e:
        print(f"Error setting up Chrome driver: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python version: {os.sys.version}")
        
        # Fallback method: Let Selenium handle it directly
        try:
            print("Attempting fallback method for ChromeDriver...")
            service = Service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as fallback_error:
            print(f"Fallback method also failed: {str(fallback_error)}")
            raise e

def send_notification(message):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send SMS
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=YOUR_PHONE_NUMBER
        )
        
        # Make a call
        client.calls.create(
            twiml=f'<Response><Say>{message}</Say></Response>',
            from_=TWILIO_PHONE_NUMBER,
            to=YOUR_PHONE_NUMBER
        )
        
        print(f"Notification sent: {message}")
    except Exception as e:
        print(f"Failed to send notification: {str(e)}")

def check_tickets():
    driver = None
    try:
        driver = setup_driver()
        print("Driver setup successful, navigating to URL...")
        driver.get(URL)
        
        # Wait for the page to load
        print("Waiting for page to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get the page source
        page_source = driver.page_source
        print("Page loaded successfully")
        
        # Check for dates and teams
        found_match = False
        for date in TARGET_DATES:
            if date in page_source:
                for team in TARGET_TEAMS:
                    if team in page_source:
                        message = f"Match found! {team} vs RCB on {date}!"
                        send_notification(message)
                        print(f"{datetime.now()}: {message}")
                        found_match = True
                        break
                if found_match:
                    break
        
        if not found_match:
            print(f"{datetime.now()}: No target matches found")
        
    except Exception as e:
        print(f"Error during ticket check: {str(e)}")
    
    finally:
        if driver:
            driver.quit()
            print("Browser session closed")

def main():
    print("Starting ticket monitoring...")
    try:
        while True:
            print(f"\n{datetime.now()}: Checking for tickets...")
            check_tickets()
            print(f"Next check in 60 seconds. Press Ctrl+C to exit.")
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nTicket monitoring stopped by user.")
    except Exception as e:
        print(f"Unexpected error in main loop: {str(e)}")
        print("Ticket monitoring stopped due to error.")

if __name__ == "__main__":
    main()