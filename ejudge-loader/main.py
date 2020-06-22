import requests
from bs4 import BeautifulSoup
from lxml import etree as et
import re, os
import tarfile, shutil

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

status_url = f'https://caos.ejudge.ru/ej/client/view-problem-summary/S{SID}'
resp = req_session.get(status_url, headers=dict(referer=status_url))
soup = BeautifulSoup(resp.content, 'html.parser')
table = et.HTML(str(soup.find_all('table')[1]))
run_id_data = dict()

for row in table[0].getchildren()[0].getchildren()[1:]:
    row = row.getchildren()

    status = re.search(r'<td class="b1">(.*)</td>', str(et.tostring(row[2]))).group(1)
    if status not in ['Pending review', 'Partial solution'] and 'OK' not in status:
        continue
    if status == 'Pending review' or 'OK' in status:
        status = 'OK'

    run_id = re.search(r'<td class="b1"><a class="tab" href=".*?">(.*)</a></td>', str(et.tostring(row[5])))
    if not run_id:
        continue
    run_id = run_id.group(1)
    long_name = re.search(r'<td class="b1"><a class="tab" href=".*?">(.*)</a></td>', str(et.tostring(row[1]))).group(1)
    short_name = re.search(r'<td class="b1">(.*)</td>', str(et.tostring(row[0]))).group(1)
    if 'ku' in short_name or 'kr' in short_name:
        short_name = short_name[0:1] + 'r' + short_name[2:]
        long_name = short_name[0:4] + '/' + short_name[5:]

    run_id_data[run_id] = [long_name, status]

    directory = f'{root_dir}/{long_name}'
    if not os.path.exists(directory):
        os.makedirs(directory)

status_url = f'https://caos.ejudge.ru/ej/client/view-submissions/S{SID}?all_runs=1'
resp = req_session.get(status_url, headers=dict(referer=status_url))
soup = BeautifulSoup(resp.content, 'html.parser')
table = et.HTML(str(soup.find_all('table')[1]))

for row in table[0].getchildren()[0].getchildren()[1:]:
    row = row.getchildren()

    run_id = re.search(r'<td class="b1">(.*)</td>', str(et.tostring(row[0]))).group(1)
    if run_id not in run_id_data:
        continue

    compiler = re.search(r'<td class="b1">(.*)</td>', str(et.tostring(row[4]))).group(1)
    directory = run_id_data[run_id][0]
    print(f'Loading {directory}')
    file_name = 'main'
    if 'gas' in compiler[:3]:
        file_name += '.S'
    elif 'gcc' in compiler[:3]:
        file_name += '.c'
    elif 'g++' in compiler[:3]:
        file_name += '.cpp'
    else:
        file_name += '.txt'

    if 'txt' in file_name:
        code_url = f'https://caos.ejudge.ru/ej/client/download-run/S{SID}?run_id={run_id}'
        code_resp = req_session.get(code_url, headers=dict(referer=code_url))
        with open(f'./{root_dir}/{directory}/archive.gz', 'wb') as f:
            f.write(code_resp.content)

        tar = tarfile.open(f'./{root_dir}/{directory}/archive.gz')
        tar.extractall(f'./{root_dir}/{directory}')
        tar.close()
        os.remove(f'./{root_dir}/{directory}/archive.gz')

    else:
        with open(f'./{root_dir}/{directory}/{file_name}', 'wb') as f:
            code_url = f'https://caos.ejudge.ru/ej/client/download-run/S{SID}?run_id={run_id}'
            code_resp = req_session.get(code_url, headers=dict(referer=code_url))
            f.write(code_resp.content)

    with open(f'./{root_dir}/{directory}/README.md', 'w') as f:
        status = run_id_data[run_id][1]
        f.write(f'#Status: {status}')

req_session.close()
print(f'Loaded all your successfull submissions to {root_dir}!')
