# -*- coding: utf-8 -*-

"""
A program to read the console messages from Chrome, using the Selenium
test driver.
"""

import argparse
import collections
from   collections import OrderedDict
from   collections import namedtuple
import json
import os
import re
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Credits
__author__ =        'Eric Palmer'
__copyright__ =     'Copyright 2017, University of Richmond'
__version__ =       '2.1'
__maintainer__ =    'Eric Palmer'
__email__ =         'epalmer@richmond.edu'
__status__ =        'production'
__licence__ =       'http://www.gnu.org/licenses/gpl-3.0.en.html'



def extract_mc_url(re_pattern, msg):
    '''return extracted mixed content url as string if found else empty string'''
    if "Mixed Content:" in msg:
        mc_url = "Error parsing message for mc url"
        results = re.search(re_pattern, msg)
        if results and (len(results.group()) > 1):
            mc_url = results.group(1)
    else:
        mc_url = ''
        pass
    return mc_url


def results2tsv(results):
    tsv_list = [("\t".join(['url', 'level', 'message', 'source', 'mc_url', 'timestamp']))]

    for url in results:
        if len(results[url]) == 0:
            tsv_list.append("\t".join([url, 'INFO', 'No log msg found for this url']))
        else:
            for logmsg in results[url]:
                tsv_row = "\t".join([url, logmsg['level'], logmsg['message']
                    logmsg['source'], logmsg['mc_url'], logmsg['timestamp']])
                tsv_list.append("\t".join(tsv_row))

    return tsv_list


def results2json(results):
    return json.dumps(results)


def cli_parse():
    parser = argparse.ArgumentParser(description="Get headless chrome console log output from urls")

    parser.add_argument('chromebrowser', type=str, help="Full path to Chrome browser binary file.")
    parser.add_argument('chromedriver', type=str, help="Full path to Chrome driver binary file.")
    parser.add_argument('infile', type=str,
                        help="Input file of valid urls to check.  One url per line.")
    parser.add_argument('outfile', type=str, help="Writable file path and filename for results.")

    parser.add_argument("-j", "--json", help="Json formatted results file", action="store_true")
    parser.add_argument("-t", "--tsv",
                        help="Tab separated values (tsv) formatted results file (default output_format)",
                        action="store_true")

    parser.add_argument("-v", "--verbose",
                        help="Outputs to stdout urls being processed and other useful information",
                        action="store_true")
    args = parser.parse_args()

    if args.json and args.tsv:
        raise Exception("Program argument conflict - pick json or tsv file formats not both.")

    output_format = 'json' if args.json else 'tsv'

    cli_args = namedtuple('cli_args', 'chromebrowser chromedriver infile outfile output_format verbose')
    return cli_args(chromebrowser=args.chromebrowser,
                    chromedriver=args.chromedriver,
                    infile=args.infile,
                    outfile=args.outfile,
                    output_format=output_format,
                    verbose=args.verbose)


def setup_chrome_options(cli_args:object) -> object:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = cli_args.chromebrowser
    # enable browser logging
    desired = DesiredCapabilities.CHROME
    desired['loggingPrefs'] = {'browser': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=desired,
                              executable_path=os.path.abspath(cli_args.chromedriver),
                              chrome_options=chrome_options)
    return driver


def get_console_msgs(driver:object, urls:str, re_pattern, verbose:bool) -> collections.OrderedDict:
    results = collections.OrderedDict()
    if verbose:
        print("Getting console log records from urls")
    for ct, url in enumerate(urls):
        if not url or url[1] == "#":
            continue

        try:
            driver.get(url)
        except Exception as e:
            print(str(e))
            continue

        log = driver.get_log('browser')
        for item in log:
            timestamp = item['timestamp']
            item['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime(int(str(timestamp)[:-3])))
            item['mc_url'] = extract_mc_url(re_pattern, item['message'])
        if verbose:
            print(str(ct), url)
        results[url] = log
    return results


def program_exit(driver, verbose):
    driver.close()
    if verbose:
        print("Program exit")
    sys.exit(os.EX_OK)


def json_output(output_file:str, results:object, verbose:bool):
    if verbose:
        print("Preparing and saving json output")
    json_str = results2json(results)
    with open(output_file, 'w') as outfile:
        outfile.write(json_str + "\n")
        outfile.close()


def tsv_output(output_file, results, verbose):
    if verbose:
        print("Preparing and saving tsv output")
    tsv = results2tsv(results)
    with open(output_file, 'w') as outfile:
        for row in tsv:
            outfile.write(row + "\n")
        outfile.close()


def main():
    re_pattern = "(http:.*)(\'. This content should also be served over HTTPS\.|. This request has been blocked; the content must be served over HTTPS\.$)"
    re.compile(re_pattern)

    try:
        cli_args = cli_parse()
        driver = setup_chrome_options(cli_args)
    except Exception as e:
        print(str(e))
        sys.exit(os.EX_DATA)

    input_file = cli_args.infile
    output_file = cli_args.outfile
    output_format = cli_args.output_format
    verbose = cli_args.verbose

    if verbose:
        print(cli_args.verbose)
        print(cli_args.output_format)
        print(cli_args.chromebrowser)
        print(cli_args.chromedriver)
        print(cli_args.infile)
        print(cli_args.outfile)

    urls = []
    if verbose:
        print("Opening input file")
    with open(input_file, 'r') as infile:
        urls = [ _.strip() for _ in infile.readlines() ]

    results = get_console_msgs(driver, urls, re_pattern, verbose)

    if output_format == 'tsv':
        tsv_output(output_file, results, verbose)
    else:
        # json
        json_output(output_file, results, verbose)

    program_exit(driver, verbose)
    # End of Program


if __name__ == '__main__':
    main()
