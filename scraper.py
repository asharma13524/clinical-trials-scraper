from bs4 import BeautifulSoup
import requests
import re
from datetime import date, timedelta, time, datetime
import time
import yagmail


LINKS = ["http://www.ClinicalTrials.gov/api/query/study_fields?expr=agenus&fields=LastUpdatePostDate,NCTId&max_rnk=100",
         "http://www.ClinicalTrials.gov/api/query/study_fields?expr=anika&fields=LastUpdatePostDate,NCTId&max_rnk=100"]
receiver = "mattwilliams1760@gmail.com"
yag = yagmail.SMTP("mattwilliams1760@gmail.com",
                   oauth2_file="~/oauth2_creds.json")


def main():
    while True:
        cleaned_dates = get_cleaned_dates(LINKS)
        trials = trial_update_checker(cleaned_dates)
        #convert dates back to readabe format
        trials2 = {k.strftime("%B %d %Y"): v for k, v in trials.items()}
        updated_trials = []
        #add history link for each id in trials
        for value in trials2.values():
            updated_trials.append("https://clinicaltrials.gov/ct2/history/{url}".format(url=value))
        if trials:
            try:
                yag.send(
                    to=["asharma13524@gmail.com", "anilanish@yahoo.com"],
                    subject="Clinical Trial Update",
                    contents=updated_trials,
                )
            except:
                print("Error, email was not sent")
        time.sleep(432000)

def get_cleaned_dates(LINKS):
    # Get cleaned dates from request to each url
    cleaned_dates = []
    for link in LINKS:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "lxml")
        newsoup = soup.find_all("fieldvalue")
        CLEAN_FIELDVALUE = re.compile(r"\s+")
        cleaned_dates += [CLEAN_FIELDVALUE.sub(
            ' ', field.text.replace('\n', ',')).strip() for field in newsoup]
    return cleaned_dates


def trial_update_checker(cleaned_dates):
    #Check if trial was updated within past 7 days
    today = datetime.today()
    last_week = today - timedelta(days=7)
    trials = {}
    for i in range(0, len(cleaned_dates), 2):
        cleaned_dates[i] = datetime.strptime(cleaned_dates[i], "%B %d, %Y")
        if cleaned_dates[i] > last_week:
            trials[cleaned_dates[i]] = cleaned_dates[i+1]
    return trials


if __name__ == '__main__':
    main()

