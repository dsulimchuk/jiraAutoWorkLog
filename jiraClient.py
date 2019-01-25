from datetime import date, datetime

from jira import JIRA


class JiraClient:
    seconds_in_hour = 3600

    def __init__(self, url, login, password) -> None:
        self.jira = JIRA(url, auth=(login, password))

    def queryWorklog(self, work_day: date):
        issues = self.jira.search_issues(
            jql_str=f'assignee = currentUser() AND worklogAuthor =currentUser() AND worklogDate = "{work_day}"',
            json_result=True,
            maxResults=10000
        )

        timespent = 0
        start_of_date = datetime.combine(work_day, datetime.min.time())
        end_of_date = datetime.today().replace(year=work_day.year, month=work_day.month, day=work_day.day, hour=23,
                                               minute=59, second=59)

        for row in issues['issues']:
            worklogs = self.jira.worklogs(row['key'])
            for wl in worklogs:
                logged_at = datetime.strptime(wl.started, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
                if start_of_date <= logged_at < end_of_date:
                    max_seconds_in_day = (end_of_date - logged_at).seconds
                    timespent += min(wl.timeSpentSeconds, max_seconds_in_day)

        return timespent / self.seconds_in_hour

    def queryIssues(self, jql_str, fetch_size=10000):
        issues = self.jira.search_issues(
            jql_str=jql_str,
            json_result=True,
            maxResults=fetch_size,
            fields=None
        )

        return issues['issues']

    def add_worklog(self, issue, hours, work_date):
        self.jira.add_worklog(
            issue,
            timeSpentSeconds=hours * self.seconds_in_hour,
            started=work_date,
            comment="auto log"
        )


if __name__ == '__main__':
    JiraClient(None, None, None).queryWorklog(
        'parent in (CCM-10722, CCM-10723, CCM-10776, CCM-10738) AND issueFunction in aggregateExpression("Total Estimate for All Issues", "originalEstimate.sum()", "Remaining work", "remainingEstimate.sum()", "Time Spent", "timeSpent.sum()") ORDER BY updated DESC')
