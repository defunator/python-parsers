import requests
from bs4 import BeautifulSoup
from lxml import etree as et
import re
import os

login = str(input('login: '))
password = str(input('password: '))
contest_id = str(input('contest_id: '))
root_dir = str(input('root dir name to load: '))
if not os.path.exists(root_dir):
        os.makedirs(root_dir)

req_session = requests.session()
login_url = f'https://caos.ejudge.ru/ej/client?contest_id={contest_id}'
login_data = {'login': login, 'password': password}
resp = req_session.post(login_url, data=login_data, headers=dict(referer=login_url))

soup = BeautifulSoup(resp.content, 'html.parser')
SID = re.search(r'var SID="(.*)"', str(soup.find_all('script')[2])).group(1)
status_url = f'https://caos.ejudge.ru/ej/client/view-submissions/S{SID}?all_runs=1'
resp = req_session.get(status_url, headers=dict(referer=status_url))

soup = BeautifulSoup(resp.content, 'html.parser')
table = et.HTML(str(soup.find_all('table')[1]))
for row in table[0].getchildren()[0].getchildren()[1:]:
    row = row.getchilder()
    if row[7].text == 'N/A':
        continue
    points = re.search(r'<b>(.*)</b>', str(et.tostring(row[7].getchildren()[0]))).group(1)
    if points != '100':
        continue
    run_id = re.search(r'<td class="b1">(.*)</td>', str(et.tostring(row[0]))).group(1)
    task_name = re.search(r'<td class="b1">(.*)</td>', str(et.tostring(row[3]))).group(1)
    directory = f'{root_dir}/{task_name[0:4]}'
    file_name = task_name[5:]
    compiler = re.search(r'<td class="b1">(.*)</td>', str(et.tostring(row[4]))).group(1)
    if compiler[:3] == 'gas':
        file_name += '.S'
    elif compiler[:3] == 'gcc':
        file_name += '.c'
    else:
        continue

    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f'./{directory}/{file_name}', 'w') as f:
        code_url = f'https://caos.ejudge.ru/ej/client/download-run/S{SID}?run_id={run_id}'
        code_resp = req_session.get(code_url, headers=dict(referer=code_url))
        code_soup = BeautifulSoup(code_resp.content, 'html.parser')
        f.write(code_soup.prettify())

req_session.close()
print(f'Loaded all your successfull submissions to {root_dir}!')
