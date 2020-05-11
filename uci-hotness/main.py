import requests
from bs4 import BeautifulSoup
from lxml import etree as et
import re
import os

resp = requests.get('https://archive.ics.uci.edu/ml/datasets.php')
soup = BeautifulSoup(resp.content, 'html.parser')

hrefs = soup.find_all('b')[16:]
# assert len(hrefs) == 497, 'Invalid number of datasets!' # 497 is number of datasets

dataset_hotness = []
for href in hrefs:
    try:
      dataset_path = re.search(r'<a href="(.*)">.*</a>', str(href)).group(1)
      print(dataset_path, end=' ')
      url = f'https://archive.ics.uci.edu/ml/{dataset_path}'
      resp = requests.get(url)
      soup = BeautifulSoup(resp.content, 'html.parser')
      number_hits_p = soup.find_all('table')[1].find_all('table')[1].find_all('p')[-1]
      number_hits = int(re.search(f'<p class="normal">(.*)</p>', str(number_hits_p)).group(1))
      dataset_hotness.append((number_hits, url))
      print(number_hits)
    except:
        pass

dataset_hotness.sort(reverse=True)
with open('dataset_hotness.txt', 'w') as f:
  for dataset in dataset_hotness:
    f.write(f'{dataset[0]} {dataset[1]}\n')
