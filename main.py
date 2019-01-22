import csv
import getpass
from datetime import datetime

import keyring

from jiraTimeAggregator import JiraTimeAggregator

JIRA_URL = 'https://jira.billing.ru'
JIRA_USER = 'dmitrii.sulimchuk'


def main():
    jira_client = init_jira()

    issues = jira_client.query(
        "assignee = Dmitrii.Sulimchuk  and status not in (Closed, Backlog, Open) and project = CCM-CCM ORDER BY timespent")
    print(issues)
    now = datetime.now()
    time = str(now)
    current_month = now.month
    current_year = now.year
    print(time)
    holidays = getAllHolidays(current_month, current_year)

    data = [time, issues['originalEstimate'], issues['timespent']]

    print("Try to append: ", data)
    # gservice.append(data)


def getAllHolidays(current_month, current_year):
    with open('resources/all_holidays.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            if row[0] == str(current_year):
                row[current_month].split(',')
                all_holidays_in_month = set(map(lambda x: int(x), row[current_month].split(',')))
                print(f'All holidays in {current_year}.{current_month}: {all_holidays_in_month}')
                return all_holidays_in_month


def init_jira():
    jira_password = keyring.get_password(JIRA_URL, JIRA_USER)
    if jira_password is None:
        jira_password = getpass.getpass()
        jira_client = JiraTimeAggregator(JIRA_URL, JIRA_USER, jira_password)
        keyring.set_password(JIRA_URL, JIRA_USER, jira_password)
        return jira_client
    jira_client = JiraTimeAggregator(JIRA_URL, JIRA_USER, jira_password)
    return jira_client


if __name__ == '__main__':
    main()
