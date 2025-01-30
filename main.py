from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random
import time

def fill_google_form(driver, wait):
    # Google Form URL
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdYb2utxCM_snvc_Dq0mcbSLbnhesKXHK9T0gxkfHdr6--hNw/viewform?usp=dialog"
    driver.get(form_url)
    
    def is_question_answered(question_element):
        question_container = question_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'geS5n')]")
        selected_radios = question_container.find_elements(By.CSS_SELECTOR, "div.Od2TWd[aria-checked='true']")
        return len(selected_radios) > 0

    def fill_radio_question(question_element, max_retries=3):
        for attempt in range(max_retries):
            question_container = question_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'geS5n')]")
            radio_options = question_container.find_elements(By.CSS_SELECTOR, "div.Od2TWd[role='radio']")
            
            if radio_options:
                random_option = random.choice(radio_options)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", random_option)
                time.sleep(0.5)
                
                try:
                    driver.execute_script("arguments[0].click();", random_option)
                except:
                    try:
                        random_option.click()
                    except:
                        continue
                
                time.sleep(0.5)
                
                if is_question_answered(question_element):
                    return True
            
        return False

    def fill_checkbox_question(question_element, max_retries=3):
        for attempt in range(max_retries):
            question_container = question_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'geS5n')]")
            checkbox_options = question_container.find_elements(By.CSS_SELECTOR, "div.Od2TWd[role='checkbox']")
            
            if checkbox_options:
                num_selections = random.randint(1, len(checkbox_options))
                selected_options = random.sample(checkbox_options, num_selections)
                
                success = False
                for option in selected_options:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
                    time.sleep(0.3)
                    
                    try:
                        driver.execute_script("arguments[0].click();", option)
                        success = True
                    except:
                        try:
                            option.click()
                            success = True
                        except:
                            continue
                
                if success:
                    return True
                
        return False

    def fill_scale_question(question_element, max_retries=3):
        return fill_radio_question(question_element, max_retries)

    def verify_all_questions_answered():
        questions = driver.find_elements(By.CSS_SELECTOR, "div.HoXoMd[role='heading']")
        return [q for q in questions if not is_question_answered(q)]

    # Main form filling loop
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            questions = driver.find_elements(By.CSS_SELECTOR, "div.HoXoMd[role='heading']")
            
            for question in questions:
                try:
                    if is_question_answered(question):
                        continue
                    
                    wait.until(EC.visibility_of(question))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", question)
                    time.sleep(0.5)
                    
                    question_text = question.text.strip()
                    question_container = question.find_element(By.XPATH, "./ancestor::div[contains(@class, 'geS5n')]")
                    
                    if question_container.find_elements(By.CSS_SELECTOR, "div.Od2TWd[role='checkbox']"):
                        success = fill_checkbox_question(question)
                    elif question_container.find_elements(By.CSS_SELECTOR, "div.Od2TWd[role='radio']"):
                        if "1" in question_text and "5" in question_text:
                            success = fill_scale_question(question)
                        else:
                            success = fill_radio_question(question)
                    
                    if not success:
                        print(f"Failed to fill question: {question_text}")
                    
                except Exception as e:
                    print(f"Error on question: {question_text if 'question_text' in locals() else 'Unknown question'}")
                    print(f"Error details: {str(e)}")
                    continue
            
            unanswered = verify_all_questions_answered()
            if not unanswered:
                try:
                    submit_button = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[role='button'][jsname='M2UYVd']")
                    ))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                    time.sleep(0.5)
                    submit_button.click()
                    
                    time.sleep(2)
                    
                    if "formresponse" in driver.current_url:
                        print("Form submitted successfully!")
                        return True
                except Exception as e:
                    print("Error submitting form:", e)
            else:
                print(f"Found {len(unanswered)} unanswered questions. Retrying...")
                continue
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
    
    print("Failed to complete the form after maximum attempts")
    return False

def main():
    # Initialize Chrome WebDriver
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    submission_count = 0
    
    try:
        while True:  # Infinite loop
            try:
                print(f"\nStarting submission #{submission_count + 1}")
                success = fill_google_form(driver, wait)
                
                if success:
                    submission_count += 1
                    print(f"Total successful submissions: {submission_count}")
                    
                    # Add a random delay between submissions (1-3 seconds)
                    delay = random.uniform(1, 3)
                    time.sleep(delay)
                else:
                    print("Submission failed, retrying...")
                    
            except Exception as e:
                print(f"Error during form submission: {str(e)}")
                print("Restarting the process...")
                
                # Try to refresh the page
                try:
                    driver.refresh()
                except:
                    # If refresh fails, recreate the driver
                    driver.quit()
                    driver = webdriver.Chrome()
                    wait = WebDriverWait(driver, 10)
                
                time.sleep(2)
                
    except KeyboardInterrupt:
        print("\nScript stopped by user")
        print(f"Total successful submissions: {submission_count}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()