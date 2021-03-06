#!/usr/bin/env python3
#
#          Pizza scraper
#   This software takes a bunch of websites and tries to scrape
#   data off of them. For now it's "hardcoded", as in it contains
#   no machine-learning like stuff. This is needed for an other repo of mine.

import re
import os
from getkey     import getkey, keys
from requests   import get
from requests   import RequestException
from contextlib import closing
from bs4        import BeautifulSoup

program_name    = "pizza scraper"
program_ver     = "0.0.3"

# Basic web scraping based on the following tutorial (as of 15/02/2018):
# https://realpython.com/python-web-scraping-practical-introduction/
def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error("Error during requests to {0} : {1}".format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

# ----------------------------------------------------------------------

# Self explanatory.
def info(text):
    print("INFO:", text)

# Self explanatory.
def err(text):
    print("ERROR:", text)

# This function shows a simple yes-or-no dialog.
def warningDialog(text):
    print("WARNING: Are you sure you want to", text, "(y/n)")

    key = getkey()

    if key == 'y' or key == 'Y' or key == '\n':
        return True
    else:
        return False

def deleteWithWarning(filename):
    if warningDialog("remove the old %s?".replace("%s", filename)) and os.path.exists(filename):
            os.remove(filename)

# writeDataToFile(...) ~ This function attempts to write the data collected
# about a pizza to a text file.
def writeDataToFile(filename, pizzaname, diameter, vendor, price):
    with open(filename, "a") as file:
        file.write(str(diameter))
        file.write(",")
        file.write(str(price))
        file.write(",")
        file.write(vendor)
        file.write(",")
        file.write(pizzaname)
        file.write("\n")


def concatFiles(filenames, outf):
    with open(outf, 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                outfile.write(infile.read())

# getGino() ~ this functions tries to parse ginopizza.hu to get pizza prices and names
def getGino():
    info("Trying to scrape ginopizza.hu...")

    raw_html = simple_get("http://www.ginopizza.hu/index.php?option=com_content&view=article&id=13:vekony-tesztas-pizza&catid=8:menu")

    if(len(raw_html) > 0):
        # Delete "gino.txt" if we have one and the user chose to
        deleteWithWarning("gino.txt")

        # Actually parse the site
        # The data is contained in a table so we parse every row and column
        # to mine what we need.
        html = BeautifulSoup(raw_html, "html.parser")
        for i, tr in enumerate(html.select("tr")):
            name = ""
            # Ginopizza offers 28 and 45 cm pizzas, hence why the two variables
            price_28 = 0
            price_45 = 0

            # Skip the table header
            if(i == 0):
                continue

            tds = tr.select("td")

            name = re.sub(r"(.*)\((.*)\)", r"\1", tds[0].text)
            price_28 = re.search("[0-9]{3,4}", tds[2].text).group(0)
            price_45 = re.search("[0-9]{3,4}", tds[3].text).group(0)

            writeDataToFile("gino.txt", name, "28", "Gino", price_28)
            writeDataToFile("gino.txt", name, "45", "Gino", price_45)

        info("gino.txt written.\n")

    else:
        err("Failed to scrape ginopizza.hu...")

# getSziget() ~ This function tries to scrape szigetelbar.hu
def getSziget():
    # Pass for now as there is an error occuring when doing simple_get(...)
    pass

# getKerekes() ~ This function tries to parse kerekespizza.hu for offers
def getKerekes():
    info("Trying to scrape kerekespizza.hu")

    raw_html = simple_get("http://www.kerekespizza.hu/index.php")

    if(len(raw_html) > 0):
        deleteWithWarning("kerekes.txt")

        html = BeautifulSoup(raw_html, "html.parser")

        name = ""
        price = 0

        for i, div in enumerate(html.select("div.etel-kategoria")):
            if(i == 1):
                for j, food in enumerate(div.select("div.etlap_wrap_table")):
                    name = food.select("span.etelnev_table")[0].text
                    price = re.sub( r"([0-9]{3,4})Ft",
                                    r"\1",
                                    food.select("div.ar_table")[0].text.replace(" ", ""))
                    writeDataToFile("kerekes.txt", name, "28", "Kerekes", price)
            else:
                continue
        info("kerekes.txt written.\n")
    else:
        err("Failed to scrape kerekespizza.hu")

def getPecsi():
    # http://pecsenyesarok.hu/pizzak
    info("Trying to scrape pecsenyesarok.hu")

    raw_html = simple_get("http://pecsenyesarok.hu/pizzak")

    if(len(raw_html) > 0):
        deleteWithWarning("pecsenye.txt")

        html = BeautifulSoup(raw_html, "html.parser")
        name = ""
        price = 0

        for i, tr in enumerate(html.select("tr")):
            if(i < 1 or i > 38):
                continue
            name = tr.select("h4")[0].text
            price = tr.select("td")[1].text.replace(" ", "")
            price = re.sub(r"([0-9]{3,4})Ft", r"\1", price)
            writeDataToFile("pecsenye.txt", name, 30, "Pecsenye", price)

        info("pecsenye.txt written.\n")

    else:
        err("Failed to scrape pecsenyesarok.hu")

# Main
def main():
    print("Welcome to ", program_name, " v", program_ver, ".", sep="")
    print()

    getGino()
    getKerekes()
    getPecsi()

    deleteWithWarning('pizza.txt')
    concatFiles(['gino.txt', 'kerekes.txt', 'pecsenye.txt'], 'pizza.txt')
    info('All outputs written to pizza.txt.')

main()
