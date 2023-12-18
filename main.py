import sys
from os import getenv
from time import sleep

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# To remove duplicate lines in the scraped content


def remove_duplicates(data):
    count_dict = {}

    for element in data:
        if element in count_dict.keys():
            count_dict[element] += 1
        else:
            count_dict[element] = 1

    data.clear()

    for key in count_dict.keys():
        data.append(key)


# Defining the scraper class


class LinkedInScraper:
    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.options = webdriver.ChromeOptions()
        self.service = Service()

        self.driver = self.new_driver()
        self.driver.maximize_window()

        self.LOGIN_URL = "https://linkedin.com"

        self.info = []

    # Create and return a new instance of the webdriver

    def new_driver(self):
        driver = webdriver.Chrome(
            service=self.service, options=self.options
        )

        return driver

    # Login to linkedin

    def login(self, driver):
        driver.get(self.LOGIN_URL)

        username_element = driver.find_element(
            by=By.XPATH,
            value='//input[@autocomplete="username"]'
        )

        password_element = driver.find_element(
            by=By.XPATH,
            value='//input[@autocomplete="current-password"]'
        )

        username_element.send_keys(self.email)
        password_element.send_keys(self.password)

        signin_button = driver.find_element(
            by=By.CLASS_NAME,
            value="sign-in-form__submit-btn--full-width"
        )

        signin_button.click()

    # Method to fetch the default webdriver

    def get_driver(self):
        return self.driver

    # Method to check whether the given section of the page contains the given
    # id

    def section_contains_id(self, section, id):
        try:
            section.find_element(by=By.ID, value=id)

            return True
        except Exception:
            return False

    # Method to check whether the given section of the page contains the
    # "Show All X Experiences" or "Show All X Education" footer

    def section_contains_footer(self, section):
        try:
            section.find_element(
                by=By.CLASS_NAME, value="pvs-list__footer-wrapper"
            )

            return True
        except Exception:
            return False

    # Method to scrape the given profile

    def scrape_profile(self, profile_link):
        contents = []

        self.driver.get(profile_link)

        sleep(15)

        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        profile_scaffold = self.driver.find_element(
            by=By.CLASS_NAME, value='scaffold-layout__main'
        )

        sections = profile_scaffold.find_elements(
            by=By.TAG_NAME, value="section"
        )

        for section in sections:
            try:
                # Scraping the about section

                if self.section_contains_id(section, "about"):
                    about_text = section.find_elements(
                        by=By.TAG_NAME,
                        value="span"
                    )[2].text

                    contents.append(about_text)

                # Scraping the experiences section

                elif self.section_contains_id(section, "experience"):
                    sub_section = section.find_element(
                        by=By.CLASS_NAME, value="pvs-list__outer-container"
                    )

                    if not self.section_contains_footer(sub_section):
                        experiences = section.find_element(
                            by=By.TAG_NAME, value="ul"
                        ).text
                    else:
                        link = sub_section.find_element(
                            by=By.ID,
                            value="navigation-index-see-all-experiences"
                        ).get_attribute("href")

                        if link:
                            new_driver = self.new_driver()

                            self.login(new_driver)

                            new_driver.get(link)

                            sleep(5)

                            experiences = new_driver.find_element(
                                by=By.TAG_NAME, value="main"
                            ).find_element(by=By.TAG_NAME, value="ul").text

                            new_driver.close()
                        else:
                            continue

                    experiences = experiences.split("\n")
                    remove_duplicates(experiences)
                    experiences = "\n".join(experiences)

                    contents.append(experiences)

                # Scraping the education section

                elif self.section_contains_id(section, "education"):
                    sub_section = section.find_element(
                        by=By.CLASS_NAME, value="pvs-list__outer-container"
                    )

                    if not self.section_contains_footer(sub_section):
                        education = section.find_element(
                            by=By.TAG_NAME, value="ul"
                        ).text
                    else:
                        link = sub_section.find_element(
                            by=By.ID,
                            value="navigation-index-see-all-education"
                        ).get_attribute("href")

                        if link:
                            self.driver.get(link)

                            sleep(5)

                            education = self.driver.find_element(
                                by=By.TAG_NAME, value="main"
                            ).find_element(by=By.TAG_NAME, value="ul").text

                            self.driver.back()
                        else:
                            continue

                    education = education.split("\n")
                    remove_duplicates(education)
                    education = "\n".join(education)

                    contents.append(education)
                else:
                    continue
            except Exception as e:
                contents.append("")

                print(e)

        content = "\n".join(contents)

        self.info.append(content.replace("\n", " "))

    # Method to scrape all the profiles

    def scrape_profiles(self):
        for profile_link in self.profile_links:
            print(f"Scraping {profile_link} ...")

            self.scrape_profile(profile_link)

        print(
            f"Successfully scraped {len([i for i in self.info if i])} profiles"
        )

    # Method to load the profiles from a csv file

    def load_from_csv(self, filename):
        try:
            df = pd.read_csv(filename)
        except Exception as e:
            print(e)

            sys.exit(1)

        if "LinkedIn" in df.columns:
            self.names = df["Full Name"].to_list()
            self.profile_links = df["LinkedIn"].to_list()

            print(self.names)
            print(self.profile_links)

            print(f"Successfully loaded {len(self.profile_links)} profiles")
        else:
            print("No column named 'LinkedIn' found in the provided csv file")

            sys.exit(1)

    # Method to load the profiles from a xlsx file

    def load_from_xlsx(self, filename):
        try:
            df = pd.read_excel(filename)
        except Exception as e:
            print(e)

            sys.exit(1)

        if "LinkedIn" in df.columns:
            self.names = df["Full Name"].to_list()
            self.profile_links = df["LinkedIn"].to_list()

            print(self.names)
            print(self.profile_links)

            print(f"Successfully loaded {len(self.profile_links)} profiles")
        else:
            print("No column named 'LinkedIn' found in the provided xlsx file")

            sys.exit(1)

    # Method to save the data to a csv file

    def to_csv(self, filename):
        output_filename = filename.split("/")[-1].split(".")[0] + "_out.csv"

        try:
            df = pd.DataFrame(zip(self.names, self.profile_links, self.info))
            df.columns = ["Full Name", "LinkedIn", "Info"]
            df.to_csv(output_filename, index=False)

            print(f"Successfully saved the data to {output_filename}")
        except Exception as e:
            print(e)

            sys.exit(1)

    # Method to save the data to a xlsx file

    def to_xlsx(self, filename):
        output_filename = filename.split("/")[-1].split(".")[0] + "_out.xlsx"

        try:
            df = pd.DataFrame(zip(self.names, self.profile_links, self.info))
            df.columns = ["Full Name", "LinkedIn", "Info"]
            df.to_csv(output_filename, index=False)

            print(f"Successfully saved the data to {output_filename}")
        except Exception as e:
            print(e)

            sys.exit(1)

    # Method to close the webdriver

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    # Loading environment variables

    load_dotenv()

    email = getenv("EMAIL")
    password = getenv("PASSWORD")

    # Initializing the scraper

    liscraper = LinkedInScraper(
        email=email,
        password=password,
    )

    # Getting the filename from the command-line arguments

    filename = sys.argv[1]

    if filename.endswith(".csv"):
        liscraper.load_from_csv(filename)
    elif filename.endswith(".xlsx"):
        liscraper.load_from_xlsx(filename)
    else:
        print("Unsupported file format")

        sys.exit(1)

    driver = liscraper.get_driver()

    liscraper.login(driver)

    sleep(15)  # Waiting for the login to complete

    liscraper.scrape_profiles()

    print("Done")

    if filename.endswith(".csv"):
        liscraper.to_csv(filename)
    else:
        liscraper.to_xlsx(filename)

    liscraper.close()
