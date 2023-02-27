"""Template robot with Python."""
import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium
from selenium.webdriver.support.ui import Select
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from RPA.PDF import PDF
import csv

browser = webdriver.Chrome(
    # ChromeDriver executable path (download from https://chromedriver.chromium.org/downloads)
    executable_path="/Users/mac/Downloads/chromedriver"
    # windows in download folder
    # executable_path="C:\\Users\\gundo\\Downloads\\chromedriver.exe"
)

# Variables
CSV_URL = "https://robotsparebinindustries.com/orders.csv"


def open_orders_site():
    browser.get("https://robotsparebinindustries.com/#/robot-order")
    browser.save_screenshot("output/website.png")
    # browser.find_element(value="username").send_keys("maria")
    # browser.find_element(value='password').send_keys('thoushallnotpass')
    # browser.find_element(value="Log in").click()
    # Click Button When Visible    locator=//button[@class="btn btn-dark"]
    browser.find_element(
        by="xpath", value="//button[@class='btn btn-dark']").click()


def create_directory():
    os.makedirs("temp", exist_ok=True)


def download_csv():
    http = HTTP()
    http.download(
        url=CSV_URL, overwrite=True)


def read_table_csv():

    # Open the CSV file
    with open('orders.csv', newline='') as csvfile:
        # Create a CSV reader
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        # Skip the header row if it exists
        next(reader, None)

        # Loop through each row in the CSV file
        for row in reader:
            # Retrieve the Head, Body, Legs, and Address values from the row
            head = row[0]
            body = row[1]
            legs = row[2]
            address = row[3]
            fill_and_submit_order(row)

            # Do something with the values
            print(
                f"Head: {head}, Body: {body}, Legs: {legs}, Address: {address}")


def fill_and_submit_order(order):
    # Order number,Head,Body,Legs,Address
    head = order[1]
    body = order[2]
    legs = order[3]
    address = order[4]

    # FILL FORM
    Select(browser.find_element(value="head")).select_by_value(head)

    elementValue = "id-body-"+body
    browser.find_element(by="id", value=elementValue).click()
    browser.find_element(
        By.CSS_SELECTOR, value="input.form-control[type=number][placeholder='Enter the part number for the legs']").send_keys(legs)

    browser.find_element(By.ID, value="address").send_keys(address)
    browser.find_element(By.ID, value="preview").click()
    # Take page screenshot
    browser.find_element(By.ID, "robot-preview-image").screenshot(
        "temp/robot_preview" + head+body+legs+".png")
    # convet png to pdf
    # pdf = pdfkit.from_file(png, 'output/robot_preview+{head}+{body}+{legs}.pdf')
    # pdfkit.from_file('temp/robot_preview.png', 'output/robot_preview.pdf')

    if browser.find_element(By.ID, value="order").is_displayed():
        print("Order Placed")
        browser.find_element(By.ID, value="order").click()
    else:
        # WebDriverWait(browser, 10).until(
        #     browser.find_element(By.ID, value="order").is_displayed())
        browser.find_element(By.ID, value="order").click()
        print("Order Failed")

        if browser.find_element(By.CSS_SELECTOR, value="alert alert-danger").is_displayed():
            browser.find_element(By.ID, "order").click()
            print("Tried To Click Order Button")

    browser.find_element(By.ID, value="order-another").click()
    browser.find_element(
        by="xpath", value="//button[@class='btn btn-dark']").click()


def fill_and_submit_the_form_for_one_person(sales_rep):
    browser.find_element_by_id("firstname").send_keys(sales_rep["First Name"])
    browser.find_element_by_id("lastname").send_keys(sales_rep["Last Name"])

    browser.find_element_by_id("submit").click()


def fill_the_form_using_the_data_from_the_excel_file():
    excel = Files()
    excel.open_workbook("SalesData.xlsx")
    sales_reps = excel.read_worksheet_as_table(header=True)
    excel.close_workbook()
    for sales_rep in sales_reps:
        fill_and_submit_the_form_for_one_person(sales_rep)


def collect_the_results():
    # Take page screenshot
    browser.take_screenshot(
        filename=f"{os.getcwd()}/output/sales_summary.png",
        selector="css=div.sales-summary")


def export_the_table_as_a_pdf():
    sales_results_html = browser.get_property(
        selector="css=#sales-results", property="outerHTML")
    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, "output/sales_results.pdf")


def log_out():
    browser.click("css=logout")


def main():
    open_orders_site()
    create_directory()
    download_csv()
    read_table_csv()


if __name__ == "__main__":
    main()
