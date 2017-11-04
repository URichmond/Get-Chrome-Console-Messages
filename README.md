# Get Chrome Console Log Messages

You feed this program URLs and it returns console log messages in JSON or TSV format from Chrome. This program runs [Headless Chrome](https://developers.google.com/web/updates/2017/04/headless-chrome) and uses [Selenium](http://www.seleniumhq.org/) to get the console log messages from Chrome. This tool works on a list of URLs. You can create the list, run the program and examine the results for as many website pages as you want.

## Why?

I had to move more than 180 websites from http to https (TLS) and wanted to query popular page urls for [mixed content](https://developers.google.com/web/fundamentals/security/prevent-mixed-content/what-is-mixed-content) warnings after I completed the migration.
 
Chrome displays mixed content warning and errors, along with other messages in the [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools/) Console pane.  That got me thinking about using headless chrome to get the warnings.  An added bonus is all types of warning and errors can be displayed as console messages. Now I have a tool that can automatically get these messages for any web page.

### Example Mixed Content Message
![Example Console Messages](./images/example_mixed_content.png?raw=true "Console Messages")

## Outputs

The program can output the results in JSON format or Tab Separated Value (TSV) format.  We are using TSV mostly and importing the results into a spreadsheet for further analysis.

## Compatibility

This has only been tested on Python 3.6.0 on Mac OS X 10.11.6 El Capitan.  Please file an issue when you test this in other environments whether it works or fails. It should work with 3.x on Mac OS X and Linux.  I have no idea if it works on Windows at all. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

This is pretty easy.  I tried to provide details so that almost anyone can follow along. 


### Prerequisites

You will need one python package installed and will need to know where your Chrome Browser binary is located.  You will also need a ChromeDriver binary file and its install location.  See below:

#### Python Package Dependencies


```
pip install -r requirements.txt
```

### Installing the Binaries


#### Chrome Binary Dependency

You need to determine the full path to your Chrome browser binary image.  Your browser version needs to be 59 or later. Since Chrome auto-updates versions your chrome version should be at least 61. 

On my Mac (10.11.6 El Capitan) my Chrome binary is:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

#### ChromeDriver Dependency

The [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) is a binary file that is necessary to run headless Chrome. You need to [download](https://sites.google.com/a/chromium.org/chromedriver/downloads) a version for your operating system.

You will need to know the relative or full path to chromedriver.  On my system I put it into the project root:

```
"./chromedriver"
```

### URLs

Create a text file with urls that you want to query for console log messages.  Put one url on each line.  The file can have optional comment lines and blank lines, both of which will be ignored.

For example you might create `urls.txt` :

```
# example URLS
https://www.google.com/

https://www.bing.com/
# End of File
```

### Sample Command Line Invocation

`python get_msg.py --help` displays help information.

This gives you an idea of how to call the program:

```
python get_msg.py \
-t \
-v \
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
"./chromedriver" \
"/tmp/sample.txt"
"/tmp/results.tsv"
```

Replace the parameters above with ones relevant to your system. 

## Coded With

* [PyCharm IDE](https://www.jetbrains.com/pycharm/)
* [Python 3.6](https://www.python.org/downloads/release/python-360/)

Of course you can use any Python IDE or any text editor. 
 
## Authors and Contributors

* **Eric Palmer** - *Initial work* - [DaddyOh](https://github.com/DaddyOh)

Currently there are no other contributors. 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details



