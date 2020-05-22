# Import libraries
from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import pandas as pd

# Function to set up the chromedriver
# Returns: Browser
def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

# Function to visit links
# Parameters url: url to visit
#            seconds: seconds to wait before scraping
#            browser: instance of the browser
# Returns: browser.html
def visit_url(url,seconds,browser):
    browser.visit(url)
    time.sleep(seconds)
    return browser.html

# Function to scrape web pages
# Returns: mars_dict
def scrape():
    browser = init_browser()
    mars_dict = {}

    # Call visit_url to get html for the page
    soup = bs(visit_url("https://mars.nasa.gov/news/",5,browser), 'html.parser')

    # Find the Title and Description from the html and add it to mars_dict
    results = soup.find('li', class_='slide')
    news_title = results.find('h3').text
    news_p = results.find('div',class_="article_teaser_body").text
    mars_dict.update({"title": news_title, "description": news_p})

    # Call visit_url to get html for the page
    soup = bs(visit_url("https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars",0,browser), 'html.parser')
    
    # Click on the 'Full Image' and 'more info' to get to the correct page
    browser.click_link_by_id('full_image')
    browser.click_link_by_partial_text('more info')

    # Get the html for the page
    soup = bs(browser.html, 'html.parser')

    # Find the url for the image, split the browser url on '/spaceimages' and prepend the first part to the image url and add to mars_dict
    image_url = soup.find("img", class_="main_image")
    featured_image_url = browser.url.split("/spaceimages")[0] + image_url['src']
    mars_dict.update({"featimg" : featured_image_url})

    # Call visit_url to get html for the page
    soup = bs(visit_url("https://twitter.com/marswxreport?lang=en",20,browser), 'html.parser')

    # find all 'article' tags in the page
    articles = soup.find_all('article')

    # Set variables to do determine if a report was found, due to lengthy loading times sometimes the weather report is not found 
    latest_report_found = False
    i = 0
    mars_weather = "No Report Found  --- Try again shortly"

    # Loop until a report is found by filtering 'InSight sol' or until there are no more articles
    while latest_report_found == False and i < len(articles):
        spans = articles[i].find_all('span')
        if spans[4].text[0:11] == "InSight sol":
            latest_report_found = True
            mars_weather = spans[4].text
        i += 1
    # Add to mars_dict
    mars_dict.update({"weather": mars_weather})

    # Read html tables into a dataframe
    tables = pd.read_html("https://space-facts.com/mars/")

    # Select the first table and set the columns
    df = tables[0]
    df.columns = ['Category', 'Value']

    # Convert the dataframe into an html table, do not include an index
    html_table = df.to_html(index=False)

    # Remove new lines from the html
    html_table = html_table.replace('\n', '')
    mars_dict.update({"facts": html_table})

    # Call visit_url to get html for the page
    soup = bs(visit_url("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars",0,browser), 'html.parser')
    
    # Find all 'div' tags with the class 'description'
    items = soup.find_all('div',class_='description')

    #loop thru the links
    img_title = []
    i = 1
    for item in items:
        # Find an 'a' tag in current 'div' and set the title to the link text
        link = item.find("a")
        title = link.text[0:len(link.text)-9]
        # Click the link
        browser.click_link_by_partial_text(link.text)
        # Get the html from the page
        soup = bs(browser.html,'html.parser')
        # Find the Sample link and get the url
        image = browser.find_by_text('Sample')
        image_url = image['href']
        # Add the title and url as a delimited string to the list
        img_title.append(title + "|" + image_url)
        # Return to the previous page
        browser.back()
        i += 1

    # Add to mars_dict
    mars_dict.update({"img_title": img_title})

    # Close the browser
    browser.quit()
    return mars_dict
