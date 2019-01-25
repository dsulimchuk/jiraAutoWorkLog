import csv
import getpass
from datetime import date

import keyring

from jiraClient import JiraClient

JIRA_URL = 'https://jira.billing.ru'
JIRA_USER = 'dmitrii.sulimchuk'
PROJECT = "CCM-CCM"


def main():
    jira_client = init_jira()
    now = date.today()
    working_days_in_current_month = workingdays(now)

    for day in working_days_in_current_month:
        spent = findAlreadyLogged(jira_client, day)
        if spent < 8:
            add_work_log(jira_client, day, 8 - spent)
        else:
            print(f"at {day} all ok!")


def getAllHolidays(current_month, current_year):
    with open('resources/all_holidays.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            if row[0] == str(current_year):
                row[current_month].split(',')
                all_holidays_in_month = set(map(lambda x: int(x), row[current_month].split(',')))
                # print(f'All holidays in {current_year}.{current_month}: {all_holidays_in_month}')
                return all_holidays_in_month


def workingdays(now):
    holidays = getAllHolidays(now.month, now.year)
    result = []
    for i in range(1, date.today().day):
        if i not in holidays:
            result.append(date.today().replace(day=i))
    return result


def init_jira():
    jira_password = keyring.get_password(JIRA_URL, JIRA_USER)
    if jira_password is None:
        jira_password = getpass.getpass()
        jira_time_aggregator = JiraClient(JIRA_URL, JIRA_USER, jira_password)
        keyring.set_password(JIRA_URL, JIRA_USER, jira_password)
        return jira_time_aggregator
    jira_time_aggregator = JiraClient(JIRA_URL, JIRA_USER, jira_password)
    return jira_time_aggregator


def findAlreadyLogged(jira_client, day):
    time = jira_client.queryWorklog(
        f'assignee = currentUser() AND worklogAuthor =currentUser() AND worklogDate = "{day}"',
    )
    return time["timespent"]


def add_work_log(jira_client, day, hours):
    issue = jira_client.queryIssues(
        f"assignee = currentUser()  and status not in (Closed, Backlog, Open, Resolved) and project = {PROJECT}  AND issuetype in (Bug, Story,Sub-task ) ORDER BY timespent ASC",
        fetch_size=1
    )[0]
    print(f"i want to log {hours} hour(s) at {day} to {issue['key']} {issue['fields']['summary']}")
    jira_client.add_worklog(issue['key'], hours)


if __name__ == '__main__':
    main()
