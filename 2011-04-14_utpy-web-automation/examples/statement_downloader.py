#!/usr/bin/python

import datetime
import functools
import re
import sys

from BeautifulSoup import BeautifulSoup
import mechanize

from config import wf_username, wf_password, wf_account

LOGIN_URL = "https://www.wellsfargo.com/"

FIREFOX_USER_AGENT = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;\
 rv:1.9.2b1) Gecko/20091014 Firefox/3.6b1 GTB5"

STATEMENT_LINK_REGEX = \
    re.compile(r"Statement\s+([0-9]{2}/[0-9]{2}/[0-9]{2}).*")


def verify_on_page(page_title_regex, error_message):

    def decorator(function):

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            browser = args[0]
            title = browser.title()

            if re.match(page_title_regex, title):
                return function(*args, **kwargs)
            else:
                handle_page_error(error_message, browser)

        return wrapper
    return decorator


def setup_browser():
    browser = mechanize.Browser(factory=mechanize.RobustFactory())
    browser.addheaders = [('User-agent', FIREFOX_USER_AGENT)]
    browser.set_handle_robots(False)
    return browser


def handle_page_error(error_message, browser):
    sys.stderr.writelines([error_message])
    response = browser.response()
    if response is not None:
        sys.stderr.writelines([response.get_data()])
    sys.exit(1)


def login(browser):
    browser.open(LOGIN_URL)
    browser.select_form(name="signon")
    browser.form.set_value(wf_username, "userid")
    browser.form.set_value(wf_password, "password")

    response = browser.submit()
    parser = BeautifulSoup(response.get_data())

    meta_refresh = parser.find("meta",
                               attrs={"http-equiv": "Refresh"})
    refresh_url = meta_refresh["content"].split("URL=")[-1]
    browser.open(refresh_url)


def get_statements_page(browser):
    try:
        browser.follow_link(text_regex=r"Statements.*Documents")
    except mechanize.LinkNotFoundError:
        handle_page_error("Couldn't find Statements and Documents link.",
                          browser)


STATEMENTS_PAGE_TITLE_REGEX = r"Wells Fargo.*Statements & Documents"
STATEMENTS_PAGE_ERROR = "Not on statements page."


@verify_on_page(STATEMENTS_PAGE_TITLE_REGEX, STATEMENTS_PAGE_ERROR)
def get_statement_links(browser, account_name_regex):
    try:
        browser.select_form(name="StatementsAndDocumentsForm")
        accounts_control = browser.find_control(name="selectedAccountKey")
    except:
        handle_page_error("Couldn't find account selection control.",
                          browser)

    accounts = accounts_control.get_items()

    for account in accounts:
        match = re.search(account_name_regex,
                          account.attrs["contents"])
        if match:
            browser.set_value([account.attrs["value"]],
                              "selectedAccountKey")
            break

    browser.submit()

    links = browser._filter_links(browser._factory.links(),
                                  text_regex=STATEMENT_LINK_REGEX)

    statements = []

    for link in links:
        match = re.search(STATEMENT_LINK_REGEX, link.text)
        if match:
            month, day, year = map(int, match.group(1).split("/"))
            date = datetime.date(year, month, day)
            statements.append((date, link.absolute_url))

    statements.sort(key=lambda x: x[0])
    return statements


def download_latest_statement(browser):
    statements = get_statement_links(browser, wf_account)
    latest_statement = statements[-1]
    browser.retrieve(latest_statement[1],
                     filename="latest_statement.pdf")


def logoff(browser):
    browser.follow_link(text_regex=r"Sign Off")
    browser.close()


def main():
    """
    Run the statement downloader
    """
    browser = setup_browser()

    login(browser)
    get_statements_page(browser)
    download_latest_statement(browser)
    logoff(browser)


if __name__ == "__main__":
    main()
