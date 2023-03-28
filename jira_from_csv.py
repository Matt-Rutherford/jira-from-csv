#from atlassian import Jira
import csv,json
import os
from jira import JIRA #pip install jira
from jira.resources import Issue

########################################################
# Make sure we cwd is correct
########################################################
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

########################################################
# grab the credentials and set project key
########################################################
with open('keys/keys.json') as f:
    json_keys = json.load(f)

jira_username = json_keys['jira_user']
jira_api_token = json_keys['jira_apikey']
jira_url = json_keys['jira_server']

########################################################
# establish connection to Jira Cloud
########################################################
jira = JIRA(
    server=jira_url,
   basic_auth=(jira_username,jira_api_token), max_retries=3)

########################################################
# Define and read file containing the issues
########################################################

import_dir = f'{dname}/to_import'
f = f'{import_dir}/issues.csv'

issues = []

with open(f, 'r') as f:
    reader = csv.DictReader(f)
    issues = [row for row in reader]

########################################################
# Logic for organizing dicts
########################################################

epic_list = []
issue_list=[]



for i in issues:
    
    if i['issuetype']=='Sub-task':
        i.pop('duedate')
        i.pop('epic')
    else:
        if i['duedate']=='':
            i.pop('duedate')
            epic_list.append(i.pop('epic'))


    i['project'] = {'key': i['project']}
    i['issuetype'] = {'name': i['issuetype']}
    i['assignee'] = {'accountId': i['assignee']}

iterator = iter(issues)

while (element := next(iterator, None)) is not None:
     if (element['issuetype'] == {'name': 'Task'}):
          element.pop('parent')
          issue = jira.create_issue(element)
          parent = issue.key
          issue_list.append(issue)
          
     if (element['issuetype'] == {'name': 'Sub-task'}):
            element['parent']= {'key': parent}
            issue = jira.create_issue(element)
            


########################################################
# create issues using 'issues' list
########################################################

#issue_list = jira.create_issues(field_list = issues)

########################################################
# link issues to epic
########################################################

for i,j in zip(epic_list, issue_list):
    if i != '':
            jira.add_issues_to_epic(epic_id = i,issue_keys= j.key)

print('success!')



#jira.add_issues_to_epic(epic_id=epic,issue_keys=list) ###original, used for adding all issues to one epic
'''
for issue in issues:
    id = jira.create_issue(field=issue)
    print(id)
'''
    

    
