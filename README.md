# ScrapedIn

An easy-to-use LinkedIn profile scraper.

## Setup

- Clone the repo.
- Change your working directory to the project directory.
```
cd scrapedin
```
- Install the dependencies from the requirements.txt.
```
pip install -r requirements.txt
```
- Once completed, you need to set your linkedin account's email and password in the environment variables
```
cp .env.example .env
```
Set the variables in the .env file

## Usage
- Make sure you have a .csv or a .xlsx file with the columns 'Full Name' and 'LinkedIn', consisting of the profiles that you wish to scrape.

| Full Name      | LinkedIn                               | Info |
| -------------- | -------------------------------------- | ---- |
| Saahil Bhavsar | https://linkedin.com/in/saahil-bhavsar |      | 

- Then run the following command:
```
python main.py /path/to/csv_or_xlsx
```
Replace the path with the path of your .csv or .xlsx file
- Once the scraping is completed, a new file will be created with the "_out" suffix in the project directory, containing the scraped info.


#### Tested only on Linux.

