from jira import JIRA


class JiraTimeAggregator:
    seconds_in_day = 28800

    def __init__(self, url, login, password) -> None:
        self.jira = JIRA(url, auth=(login, password))

    def query(self, jql_str):
        issues = self.jira.search_issues(
            jql_str=jql_str,
            json_result=True,
            maxResults=10000,
            fields="timespent, timeestimate, timeoriginalestimate"
        )

        timespent = 0
        originalEstimate = 0
        for row in issues['issues']:
            print(row['key'], "  ", row['fields'])
            if row['fields']['timespent'] is not None:
                timespent += row['fields']['timespent']
            if row['fields']['timeoriginalestimate'] is not None:
                originalEstimate += row['fields']['timeoriginalestimate']

        print(issues)
        print(timespent / self.seconds_in_day)
        print(originalEstimate / self.seconds_in_day)
        return {'timespent': timespent / self.seconds_in_day,
                'originalEstimate': originalEstimate / self.seconds_in_day}


if __name__ == '__main__':
    JiraTimeAggregator(None, None, None).query(
        'parent in (CCM-10722, CCM-10723, CCM-10776, CCM-10738) AND issueFunction in aggregateExpression("Total Estimate for All Issues", "originalEstimate.sum()", "Remaining work", "remainingEstimate.sum()", "Time Spent", "timeSpent.sum()") ORDER BY updated DESC')
