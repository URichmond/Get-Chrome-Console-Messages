# -*- coding: utf-8 -*-

"""
A program to read the console messages from Chrome, using the Selenium
test driver.
"""

import argparse
import collections
from collections import namedtuple
import json
import os
import re
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Credits
__author__ = 'Eric Palmer'
__copyright__ = 'Copyright 2017, University of Richmond'
__version__ = '1.1'
__maintainer__ = 'Eric Palmer'
__email__ = 'epalmer@richmond.edu'
__status__ = 'production'
__licence__ = 'https://opensource.org/licenses/MIT'


def extract_mc_url(re_pattern: str, msg: str) -> str:
    """
    return extracted mixed content url as string if found else empty string
    """

    if "Mixed Content:" in msg:
        results = re.search(re_pattern, msg)
        if results and (len(results.group()) > 1):
            return results.group(1)
        else:
            return "Error parsing message for mc url"
    else:
        return ""


def results2tsv(results: object) -> list:
    """
    Convert the results object to a tsv list of strings.
    """

    tsv_list = ["\t".join(['url', 'level', 'message', 'source', 'mc_url', 'timestamp'])]

    for url in results:
        if len(results[url]) == 0:
            tsv_list.append("\t".join([url, 'INFO', 'No log msg found for this url']))
        else:
            for logmsg in results[url]:
                tsv_row = "\t".join([url, logmsg['level'], logmsg['message'],
                                     logmsg['source'], logmsg['mc_url'], logmsg['timestamp']])
                tsv_list.append(tsv_row)

    return tsv_list


def cli_parse() -> tuple:
    """
    Parse the command line arguments using the argparse library.

    returns -- a named tuple with the arguments resolved and named.
    """

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
        raise Exception("Program argument conflict - pick json or tsv file format, not both.")

    output_format = 'json' if args.json else 'tsv'

    cli_args = namedtuple('cli_args',
                          'chromebrowser chromedriver infile outfile output_format verbose')
    return cli_args(chromebrowser=args.chromebrowser,
                    chromedriver=args.chromedriver,
                    infile=args.infile,
                    outfile=args.outfile,
                    output_format=output_format,
                    verbose=args.verbose)


def setup_chrome_options(cli_args: object) -> object:
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


def get_console_msgs(driver: object, urls: str, re_pattern,
                     verbose: bool) -> collections.OrderedDict:
    results = collections.OrderedDict()
    verbose and print("Getting console log records from urls")
    for ct, url in enumerate(urls):
        if not url or url[1] == "#":
            continue

        try:
            driver.get(url)
        except Exception as e:
            print("Unable to get console messages for url: " + url)
            print(str(e))
            print("continuing...")
            continue

        log = driver.get_log('browser')
        for item in log:
            timestamp = item['timestamp']
            item['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime(int(str(timestamp)[:-3])))
            item['mc_url'] = extract_mc_url(re_pattern, item['message'])
        verbose and print(str(ct), url)
        results[url] = log
    return results


def json_output(output_file: str, results: object, verbose: bool) -> None:
    """
    Saves the console messages as JSON, perhaps verbosely.

    output_file -- name of the output file.
    results     -- an OrderedDict with the console messages.
    verbose     -- perhaps

    returns -- None
    """
    verbose and print("Preparing and saving json output")
    with open(output_file, 'w') as outfile:
        outfile.write(json.dumps(results) + "\n")


def tsv_output(output_file: str, results: object, verbose: bool) -> None:
    """
    Saves the console messages as tab separated values.

    output_file -- name of the output file.
    results     -- an OrderedDict with the console messages.
    verbose     -- perhaps

    returns -- None
    """
    verbose and print("Preparing and saving tsv output")
    tsv = "\n".join(results2tsv(results))
    with open(output_file, 'w') as outfile:
        outfile.write(tsv)


def main():
    re_pattern = re.compile(
        "(http:.*)(\'. This content should also be served over HTTPS\.|. This request has been blocked; the content must be served over HTTPS\.$)")

    try:
        cli_args = cli_parse()
        driver = setup_chrome_options(cli_args)
    except Exception as e:
        print(str(e))
        sys.exit(os.EX_DATAERR)

    input_file = cli_args.infile
    output_file = cli_args.outfile
    output_format = cli_args.output_format
    verbose = cli_args.verbose

    if verbose:
        print("verbose mode")
        print("output format:" + output_format)
        print("chromebrowser:" + cli_args.chromebrowser)
        print("chromedriver:" + cli_args.chromedriver)
        print("input file: " + input_file)
        print("output file: " + output_file)

    verbose and print("Opening input file")
    # test comment lines
    with open(input_file) as infile:
        urls = [_.strip() for _ in infile.readlines()]

    results = get_console_msgs(driver, urls, re_pattern, verbose)

    convert = json_output if output_format == 'json' else tsv_output
    convert(output_file, results, verbose)

    driver.close()
    verbose and print("Program exit")
    sys.exit(os.EX_OK)


if __name__ == '__main__':
    main()
