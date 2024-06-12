from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import date, timedelta
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import re
# define the website to scrape and path where the chromediver is located
website = 'https://www.liveatc.net/archive.php?m=rcss2'


desired_stream=input("Enter the feed ")
desired_time=input("Enter time in the form (0000-0030Z,0030-0100Z) ")
# Get user input for the date (YYYY-MM-DD format)
while True:
  try:
    user_date_str = input("Enter a date (YYYY-MM-DD format): ")
    user_date = date.fromisoformat(user_date_str)
    break
  except ValueError:
    print("Invalid date format. Please try again (YYYY-MM-DD).")


# define 'driver' variable
driver = webdriver.Chrome()
# open Google Chrome with chromedriver
driver.get(website)

def is_date_within_range(user_date, date_info):
  """Checks if the user-entered date is within 7 days before today.

  Args:
      user_date (date): The user-entered date object.
      date_info (str): The date string extracted from the webpage (e.g., "Day Month Year").

  Returns:
      bool: True if the date is within 7 days before today, False otherwise."""
  

  try:
    # Extract day, month, and year from the webpage date string
    match = re.search(r"(\d+)\s+([A-Za-z]+)\s+(\d+)", date_info)

    if match:
      day, month_name, year = match.groups()
      month = get_month_number(month_name)
      extracted_date = date(year=int(year), month=month, day=int(day))
    else:
      print("Invalid date format on webpage. Could not extract date information.")
      return False  # Indicate invalid format

    # Calculate the date 7 days before today (using user's date)
    seven_days_ago = extracted_date - timedelta(days=7)

    return seven_days_ago <= user_date <= extracted_date
  except (ValueError, AttributeError):
    # Handle potential errors during extraction or conversion
    print("An error occurred while processing the date information.")
    return False

def get_month_number(month_name):
  """Converts a month name to its corresponding numerical value (e.g., "June" to 6).

  Args:
      month_name (str): The name of the month.

  Returns:
      int: The numerical value of the month (1-12)."""

  months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
            "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
  return months.get(month_name)


# Extract the date from the webpage
date_element = driver.find_element(By.ID, "tP")
date_text = date_element.text
date_parts = date_text.split("::")  # Assuming "::" separates date and time
date_string = date_parts[0].strip()
date_parts = date_string.split(" ", 1)  # Assuming format is "Day Month Year"
date_info = date_parts[1] # Assuming date is the first part, remove leading/trailing spaces

# Check if the entered date is within 7 days
if is_date_within_range(user_date, date_info):
    compare_date=date_info.split()
    compare_month = get_month_number(compare_date[1])
    if compare_month != user_date.month:
        prev_month= driver.find_element(By.CLASS_NAME, "calprevmonth")
        prev_month.click()
    # Select the option with the matching text (assuming extracted_date is valid)
    elements = driver.find_elements(By.XPATH, "//div[contains(@class,'dayinmonth')]")
    for element in elements:
            if element.text == str(user_date.day):
              element.click()
              break
else:
  print(f"The entered date is either 7 days earlier or is later than the current date ")
  driver.quit()
  exit()
time.sleep(5)
feed_names=driver.find_elements(By.TAG_NAME,"option")
for feed in feed_names:
    if feed.text == desired_stream:
        feed.click()  # Select the option with the matching text
        break

date = driver.find_elements(By.XPATH, "//select[@name='time']")
if len(date) == 1:
    select_element = date[0]  # Access the first element (assuming it's the select element)
else:
    # Handle case where date might contain multiple elements (less likely)
    raise Exception("Unexpected number of elements found")
options = select_element.find_elements(By.TAG_NAME,"option")

# Iterate through each option and compare its text
for option in options:
    if option.text == desired_time:
        option.click()  # Select the option with the matching text
        break  # Exit the loop after finding the desired option
# implicit wait (useful in JavaScript driven websites when elements need seconds to load and avoid error "ElementNotVisibleException")
time.sleep(5)
submit_button = driver.find_element(By.XPATH, "//input[@value='Submit'][@type='submit']")
submit_button.click()
time.sleep(10)
try:
    audio_link = driver.find_element(By.CSS_SELECTOR, "a[href*='.mp3']")
except NoSuchElementException:
    print("File not found, this might be because:\n"
          "- the feed may have been down during the requested time period,\n"
          "- the time period requested is later than the current time,\n"
          "- the requested file is more than 7 days old,\n"
          "- a technical error occurred\n")
    driver.quit()
    exit()
audio_url = audio_link.get_attribute("href")
response = requests.get(audio_url)
with open(f"{audio_link.text}", "wb") as f:
    f.write(response.content)
driver.quit()