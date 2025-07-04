from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date, timedelta
from collections import defaultdict
import subprocess
import time
from selenium.common.exceptions import ElementClickInterceptedException


# ========== CONFIGURATION ==========
USERNAME = "your_username"
PASSWORD = "your_password"
DESK_NUM = "your desk number e.g. 5.047"
TARGET_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# ========== HELPER FUNCTIONS ==========
def wait_for_page_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def safe_find_and_click(driver, by, selector, timeout=10):
    try:
        wait_for_page_load(driver)
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        element.click()
        return True
    except Exception as e:
        print(f"❌ Failed to click {selector}: {e}")
        return False

def safe_find_and_send_keys(driver, by, selector, keys, timeout=10):
    try:
        wait_for_page_load(driver)
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        element.clear()
        element.send_keys(keys)
        return True
    except Exception as e:
        print(f"❌ Failed to send keys to {selector}: {e}")
        return False
    

# Get today's date
today = date.today()

# Check if today is in the target weekdays
today_name = today.strftime("%A")
is_today_target = today_name in TARGET_WEEKDAYS

if is_today_target:

    # ========== CLEANUP & SETUP ==========
    subprocess.run("rm -rf ~/.wdm", shell=True)
    time.sleep(2)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 15)

    # ========== STEP 1: OPEN PAGE ==========
    driver.get('https://engage.spaceiq.com/floor/1666/desks')
    time.sleep(2)

    # ========== STEP 2: ENTER 'unimelb' ==========
    safe_find_and_send_keys(driver, By.CSS_SELECTOR, ".sc-1f01iie-2.koWaBa", "unimelb")
    safe_find_and_click(driver, By.CSS_SELECTOR, ".sc-17uyjaq-4.crOWzZ")
    time.sleep(2)

    # ========== STEP 3: ENTER USERNAME & SUBMIT ==========
    safe_find_and_send_keys(driver, By.CSS_SELECTOR, 'input[type="text"]', USERNAME)
    safe_find_and_click(driver, By.CSS_SELECTOR, ".button.button-primary")
    time.sleep(2)


    # ========== STEP 5: ENTER PASSWORD & SUBMIT ==========
    safe_find_and_send_keys(driver, By.CSS_SELECTOR, 'input[type="password"]', PASSWORD)
    time.sleep(1)
    safe_find_and_click(driver, By.CSS_SELECTOR, ".button.button-primary")
    time.sleep(2)

    # ========== STEP 6: OKTA PUSH ==========
    safe_find_and_click(driver, By.CSS_SELECTOR, '.authenticator-button[data-se="okta_verify-push"]')
    print("✅ Waiting for Okta push approval...")

    try:
        # Replace this with a selector that appears ONLY after login is successful
        # For example: wait for the agenda button
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "agenda-button"))
        )
        print("🎉 Okta approval detected! Proceeding.")
    except TimeoutException:
        print("⏰ Timed out waiting for Okta push approval.")
        driver.quit()
        exit()

    # ========== STEP 7: OPEN AGENDA ==========
    safe_find_and_click(driver, By.ID, "agenda-button")
    time.sleep(10)

    # ========== STEP 8: CHECK-IN IF ALREADY BOOKED ==========
    today = date.today()
    agenda_index = today.day - 1

    def find_agenda_item(index):
        scrollable_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sc-1cyoyds-1")))
        selector = f'[data-testid="AgendaItem-{index}"]'
        for _ in range(10):
            try:
                return driver.find_element(By.CSS_SELECTOR, selector)
            except NoSuchElementException:
                driver.execute_script("arguments[0].scrollTop += 50;", scrollable_div)
                time.sleep(0.3)
        raise Exception(f"Agenda item {index} not found.")

    try:
        agenda_item = find_agenda_item(agenda_index)
        container = agenda_item.find_element(By.CSS_SELECTOR, '.sc-1f0y6vn-0.iXPBRO')
        events = container.find_elements(By.CSS_SELECTOR, '[data-testid="event-item"]')

        if events:
            events[-1].click()
            
            try:
                # Wait until clickable
                check_in_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "booking-check-in-button"))
                )
                check_in_btn.click()

                time.sleep(5)
                # Send Enter key
                # Step 3: Press Enter (send to body or active element)
                active_el = driver.switch_to.active_element
                active_el.send_keys(Keys.ENTER)
            except ElementClickInterceptedException:
                # Fallback: use JS click
                print("⚠️ Check-in button not directly clickable, using JS click...")
                driver.execute_script("arguments[0].click();", check_in_btn)
            time.sleep(2)
        else:
            print("ℹ️ No event to check in for today.")
    except Exception as e:
        print(f"⚠️ Check-in check failed: {e}")

    # ========== STEP 9: GO BACK ==========
    safe_find_and_click(driver, By.CSS_SELECTOR, '[aria-label="Go back"]')
    time.sleep(2)

    # ========== STEP 10: CALCULATE TARGET DAYS ==========
    matching_days = []
    for i in range(14):
        d = today + timedelta(days=i)
        if d.strftime("%A") in TARGET_WEEKDAYS:
            matching_days.append((d.day, d.month))

    grouped = defaultdict(list)
    for day, month in matching_days:
        grouped[month].append((day, month))

    sorted_counts = [grouped[m] for m in sorted(grouped)]

    # ========== STEP 11: DETERMINE ALREADY BOOKED DAYS ==========
    booked_status = []

    for group in sorted_counts:
        for day, month in group:
            idx = day - 1
            try:
                agenda_item = find_agenda_item(idx)
                container = agenda_item.find_element(By.CSS_SELECTOR, '.sc-1f0y6vn-0.iXPBRO')
                events = container.find_elements(By.CSS_SELECTOR, '[data-testid="event-item"]')
                booked_status.append("Yes" if events else "No")
            except Exception as e:
                print(f"⚠️ Error checking booking on {day}/{month}: {e}")
                booked_status.append("No")

        if len(sorted_counts) == 2 and group == sorted_counts[0]:
            safe_find_and_click(driver, By.CSS_SELECTOR, '[aria-label="Navigate agenda calendar next month"]')
            time.sleep(2)

    # ========== STEP 12: BUILD FORMATTED DATES ==========
    year = today.year
    formatted_dates = []
    for group in sorted_counts:
        for day, month in group:
            d = date(year, month, day)
            formatted_dates.append(f"{d.day} {d.strftime('%b %Y')}")

    # ========== STEP 13: SEARCH FOR DESK ==========
    safe_find_and_click(driver, By.ID, "agenda-button")
    time.sleep(2)
    safe_find_and_send_keys(driver, By.CSS_SELECTOR, '[aria-label="Search for people, spaces and more"]', DESK_NUM)
    time.sleep(5)
    safe_find_and_click(driver, By.CLASS_NAME, "sc-ahajb8-1")
    time.sleep(2)

    # ========== STEP 14: BOOK FREE DAYS ==========
    safe_find_and_click(driver, By.CLASS_NAME, "date-button__text")
    time.sleep(2)

    for idx, date_str in enumerate(formatted_dates):
        print(f"📅 Handling {date_str}...")
        try:
            try:
                date_elem = wait.until(lambda driver: (
                    driver.find_element(By.CSS_SELECTOR, f'[aria-label="{date_str}"]')
                    if driver.find_elements(By.CSS_SELECTOR, f'[aria-label="{date_str}"]')
                    else driver.find_element(By.CSS_SELECTOR, f'[aria-label="{date_str} - selected date"]')
                    if driver.find_elements(By.CSS_SELECTOR, f'[aria-label="{date_str} - selected date"]')
                    else None
                ))
                date_elem.click()
                time.sleep(1)
            except TimeoutException:
                print("Neither of the date elements became clickable within the timeout.")

            if booked_status[idx] == "No":
                safe_find_and_click(driver, By.ID, "modal-date-time-picker-select-btn")
                time.sleep(2)
                safe_find_and_click(driver, By.CSS_SELECTOR, ".sc-285qdc-3.IDsAT.ReserveButton")
                time.sleep(5)
                safe_find_and_click(driver, By.CLASS_NAME, "date-button__text")
                time.sleep(2)
            else:
                print("✅ Already booked.")

        except Exception as e:
            print(f"⚠️ Failed on {date_str}: {e}")
            continue

    print("🎉 Done with all bookings/check-ins!")
