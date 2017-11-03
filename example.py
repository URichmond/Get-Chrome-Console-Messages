import os
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

chrome_options = Options()

chrome_options.add_argument("--headless")
chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# enable browser logging
d = DesiredCapabilities.CHROME
d['loggingPrefs'] = {'browser': 'ALL'}


input_file = "/Users/epalmer/projects/python_projects/OSS_get_chrome_console_msg/inputs/top200_2017_11_01.txt"
tsv_file = "/Users/epalmer/projects/python_projects/OSS_get_chrome_console_msg/outputs/results_top200.tsv"
pattern = "(http:.*)(\'. This content should also be served over HTTPS\.|. This request has been blocked; the content must be served over HTTPS\.$)"


def extract_mc_url(msg):
    if "Mixed Content:" in msg:
        mc_url = "Error parsing message for mc url"
        results = re.search(pattern, msg)
        if results and (len(results.group()) > 1):
            mc_url = results.group(1)
    else:
        mc_url = ''
        pass
    return mc_url

def results2tsv(results):
    # TODO convert timestamp to local time
    # TODO extract urls from message and put into other col
    tsv_list = list()
    tsv_list.append("\t".join(['url', 'level', 'message', 'source', 'mc_url', 'timestamp']))
    for url in results:
        for logmsg in results[url]:
            tsv_row = list()
            tsv_row.append(url)
            tsv_row.append(logmsg['level'])
            tsv_row.append(logmsg['message'])
            tsv_row.append(logmsg['source'])
            tsv_row.append(extract_mc_url(logmsg['message']))
            tsv_row.append(str(logmsg['timestamp']))
            tsv_list.append("\t".join(tsv_row))

    return tsv_list
def main():
    driver = webdriver.Chrome(desired_capabilities=d,
                              executable_path=os.path.abspath("../chromedriver"),
                              chrome_options=chrome_options)
    urls = list()
    with open(input_file, 'r') as infile:
        for line in infile:
            urls.append(line.strip())


    results = dict()

    for ct,url in enumerate(urls):
        print(str(ct), url)
        driver.get(url)
        log = driver.get_log('browser')
        results[url] = log


    #json_log = json.dumps(results)

    driver.close()
    # TODO preserve the order of url processing

    tsv = results2tsv(results)

    with open(tsv_file, 'w') as outfile:
        for row in tsv:
            outfile.write(row + "\n")
        outfile.close()

if __name__ == '__main__':
    main()

