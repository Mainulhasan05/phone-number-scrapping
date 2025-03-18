from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

# Function to search for phone numbers in the page source
def find_phone_numbers(text):
    # Regex to match common US phone number formats
    phone_formats = [
        r"\(?\b\d{3}[-.)\s]?\s?\d{3}[-.\s]?\d{4}\b",  # (XXX) XXX-XXXX or XXX-XXX-XXXX
        r"\b\d{10}\b",  # 10-digit numbers
        r"\+?\d{1,4}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",  # With country code
    ]
    matches = []
    for regex in phone_formats:
        matches.extend(re.findall(regex, text))
    return matches

# Function to find all tel: href links
def find_tel_href(driver):
    tel_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'tel:')]")
    if tel_links:
        return [link.get_attribute("href").replace("tel:", "") for link in tel_links]
    return None

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()

websites_to_visit = [
    "bigeasybuyers.com", "aspectusgroup.com", "alphaomegapros.com", 
    "aircall.io", "captureone.com", "airmaxind.com", "aquasec.com", 
    "bmappliance.com", "bigpanda.io", "businessexits.com", "bsell.com"
]

for website in websites_to_visit:
    print(f"Visiting: {website}")
    driver.get("https://" + website)
    
    try:
        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Check for tel: href first
        tel_numbers = find_tel_href(driver)
        
        if tel_numbers:
            print(f"Found {len(tel_numbers)} tel: href links:")
            for number in tel_numbers:
                print(f"Phone number found: {number}")
        else:
            print("No tel: href links found. Searching for phone numbers in text...")
            
            # Fall back to regex search
            page_source = driver.page_source
            phone_numbers = find_phone_numbers(page_source)
            
            if phone_numbers:
                print(f"Found {len(phone_numbers)} phone numbers:")
                for number in phone_numbers:
                    print(f"Phone number found: {number}")
            else:
                print("No phone numbers found on homepage. Searching 'About Us' or 'Contact Us' pages...")
                
                # Try to find and click on "About Us" or "Contact Us" links
                about_contact_links = driver.find_elements(By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'about') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact') or contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'about') or contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')]")
                
                if about_contact_links:
                    about_contact_links[0].click()  # Click the first matching link
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    
                    # Check for tel: href again
                    tel_numbers = find_tel_href(driver)
                    
                    if tel_numbers:
                        print(f"Found {len(tel_numbers)} tel: href links on secondary page:")
                        for number in tel_numbers:
                            print(f"Phone number found: {number}")
                    else:
                        # Fall back to regex search
                        page_source = driver.page_source
                        phone_numbers = find_phone_numbers(page_source)
                        
                        if phone_numbers:
                            print(f"Found {len(phone_numbers)} phone numbers on secondary page:")
                            for number in phone_numbers:
                                print(f"Phone number found: {number}")
                        else:
                            print("Failed to find a phone number on secondary page.")
                else:
                    print("No 'About Us' or 'Contact Us' links found.")
    except Exception as e:
        print(f"Error processing {website}: {e}")
    
    print("-" * 50)

# Close the browser
driver.quit()