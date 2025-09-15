import requests
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd

def scrape_99acres():
    # Start with a specific search URL from 99acres
    url = "https://www.99acres.com/search/property/buy/residential-all/delhi-ncr-all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("Fetching page...")
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # First, let's see what we got
            print("Page title:", soup.title.text if soup.title else "No title found")
            
            # Look for property listings - you'll need to inspect the page to get exact selectors
            # These are common patterns, but may need adjustment
            listings = soup.find_all('div', {'data-testid': 'srp-tuple'}) or \
                      soup.find_all('div', class_=lambda x: x and 'tuple' in x.lower()) or \
                      soup.find_all('article') or \
                      soup.find_all('div', class_=lambda x: x and 'property' in x.lower())
            
            print(f"Found {len(listings)} potential listings")
            
            data = []
            for i, listing in enumerate(listings[:5]):  # Start with first 5 for testing
                try:
                    # Extract basic info - these selectors need to be updated based on actual page structure
                    title_elem = listing.find('h2') or listing.find('h3') or listing.find('a')
                    title = title_elem.text.strip() if title_elem else "No title"
                    
                    # Look for price
                    price_elem = listing.find(text=lambda x: x and '₹' in str(x))
                    price = str(price_elem).strip() if price_elem else "Price not found"
                    
                    # Look for location
                    location_elem = listing.find(text=lambda x: x and any(word in str(x).lower() for word in ['delhi', 'gurgaon', 'noida', 'mumbai']))
                    location = str(location_elem).strip() if location_elem else "Location not found"
                    
                    data.append({
                        'title': title,
                        'price': price,
                        'location': location
                    })
                    
                    print(f"Listing {i+1}: {title[:50]}...")
                    
                except Exception as e:
                    print(f"Error processing listing {i+1}: {e}")
            
            # Save to CSV
            if data:
                df = pd.DataFrame(data)
                df.to_csv('99acres_data.csv', index=False)
                print(f"\nSaved {len(data)} listings to 99acres_data.csv")
                print("\nFirst few entries:")
                print(df.head())
            else:
                print("No data extracted - need to adjust selectors")
                
        else:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

# Alternative method using Selenium for JavaScript-heavy pages
def scrape_with_selenium():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Remove this to see browser window
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = "https://www.99acres.com/search/property/buy/residential-all/delhi-ncr-all"
        print("Loading page with Selenium...")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Find listings - adjust selectors based on actual page structure
        listings = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='tuple'], .tuple, article")
        print(f"Found {len(listings)} listings with Selenium")
        
        data = []
        for i, listing in enumerate(listings[:5]):  # Test with first 5
            try:
                title = listing.find_element(By.TAG_NAME, "h2").text or \
                       listing.find_element(By.TAG_NAME, "h3").text or \
                       listing.find_element(By.TAG_NAME, "a").text
                
                # You'll need to inspect and adjust these selectors
                price_elements = listing.find_elements(By.XPATH, ".//*[contains(text(), '₹')]")
                price = price_elements[0].text if price_elements else "Price not found"
                
                data.append({
                    'title': title,
                    'price': price,
                })
                
                print(f"Selenium listing {i+1}: {title[:50]}...")
                
            except Exception as e:
                print(f"Error with listing {i+1}: {e}")
        
        # Save data
        if data:
            df = pd.DataFrame(data)
            df.to_csv('99acres_selenium_data.csv', index=False)
            print(f"Saved {len(data)} listings to 99acres_selenium_data.csv")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Method 1: Using requests + BeautifulSoup")
    scrape_99acres()
    
    print("\n" + "="*50 + "\n")
    
    print("Method 2: Using Selenium")
    scrape_with_selenium()
