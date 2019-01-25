from jira import JIRA


class JiraClient:
    seconds_in_hour = 3600

    def __init__(self, url, login, password) -> None:
        self.jira = JIRA(url, auth=(login, password))

    def queryWorklog(self, jql_str):
        issues = self.jira.search_issues(
            jql_str=jql_str,
            json_result=True,
            maxResults=10000,
            fields="timespent, timeestimate, timeoriginalestimate"
        )

        timespent = 0
        originalEstimate = 0
        for row in issues['issues']:
            # print(row['key'], "  ", row['fields'])
            if row['fields']['timespent'] is not None:
                timespent += row['fields']['timespent']
            if row['fields']['timeoriginalestimate'] is not None:
                originalEstimate += row['fields']['timeoriginalestimate']

        return {'timespent': timespent / self.seconds_in_hour,
                'originalEstimate': originalEstimate / self.seconds_in_hour}

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
