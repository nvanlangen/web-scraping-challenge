from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    mars_dict = {}

    url = "https://mars.nasa.gov/news/"

    browser.visit(url)
    time.sleep(5)
    html = browser.html

    soup = bs(html, 'html.parser')

    results = soup.find('li', class_='slide')
    news_title = results.find('h3').text
    news_p = results.find('div',class_="article_teaser_body").text
    mars_dict.update({"title": news_title, "description": news_p})

    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    html = browser.html

    soup = bs(html, 'html.parser')
    browser.click_link_by_id('full_image')

    browser.click_link_by_partial_text('more info')

    html = browser.html
    soup = bs(html, 'html.parser')

    image_url = soup.find("img", class_="main_image")
    featured_image_url = url.split("/spaceimages")[0] + image_url['src']
    mars_dict.update({"featimg" : featured_image_url})

    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    time.sleep(20)
    html = browser.html

    soup = bs(html, 'html.parser')

    articles = soup.find_all('article')

    latest_report_found = False
    i = 0
    mars_weather = "No Report Found"
    while latest_report_found == False and i < len(articles):
        spans = articles[i].find_all('span')
        if spans[4].text[0:11] == "InSight sol":
            latest_report_found = True
            mars_weather = spans[4].text
        i += 1
    
    mars_dict.update({"weather": mars_weather})

    url = "https://space-facts.com/mars/"
    tables = pd.read_html(url)

    df = tables[0]
    df.columns = ['Category', 'Value']

    html_table = df.to_html(index=False)

    html_table = html_table.replace('\n', '')
    mars_dict.update({"facts": html_table})

    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    time.sleep(0)
    html = browser.html

    soup = bs(html, 'html.parser')
    items = soup.find_all('div',class_='description')

    #loop thru the links and add dictionary to list
    i = 1
    for item in items:
        link = item.find("a")
        title = link.text[0:len(link.text)-9]
        browser.click_link_by_partial_text(link.text)
        html = browser.html
        soup = bs(html,'html.parser')
        image = browser.find_by_text('Sample')
        image_url = image['href']
        mars_dict.update({"title" + str(i): title, "img_url" + str(i): image_url})
        browser.back()
        i += 1

    return mars_dict
