from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from  RPA.PDF import PDF
import shutil
import os


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100
    )
    open_robot_order_website()
    global path
    global pdf
    pdf = PDF()
    path = os.getcwd()
    orders = get_orders()
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        screenshot_robot(order["Order number"])
        store_receipt_as_pdf(order["Order number"])
        embed_screenshot_to_receipt(f'output/image/{order["Order number"]}.png', f'output/pdf/{order["Order number"]}.pdf')
        page.click('#order-another')
    archive_receipts()




def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    global page
    page = browser.page()



def get_orders():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", "orders.csv", overwrite=True)
    tables = Tables()
    orders = tables.read_table_from_csv(path=f'{path}/orders.csv', header=True, delimiters=',')
    return orders


def close_annoying_modal():
    page = browser.page()
    page.click("button:text('Yep')")



def fill_the_form(row):
    page.select_option('#head', str(row['Head']))
    page.click(f'//*[@class="form-check-input" and @value="{row["Body"]}"]')
    page.fill("//*[@placeholder='Enter the part number for the legs']", str(row['Legs']))
    page.fill('//*[@placeholder="Shipping address"]', str(row['Address']))
    page.click('text="Preview"')
    page.click('//*[@id="order"]')
    try:
        page.query_selector('#receipt').inner_html()
    except:
        fill_the_form(row)

def store_receipt_as_pdf(order_number):
    receipt = page.locator('#receipt').inner_html()
    pdf.html_to_pdf(receipt, f'output/pdf/{order_number}.pdf')

def screenshot_robot(order_number):
    locator = page.locator('#robot-preview-image')
    locator.screenshot(path=f'output/image/{order_number}.png')


def embed_screenshot_to_receipt(screenshot, pdf_file):
    image = [f'{screenshot}:align=center']
    pdf.add_files_to_pdf(image, pdf_file, append=True)

def archive_receipts():
    archive_dir = "output/pdf"
    source_dir = "output/pdf"
    shutil.make_archive(archive_dir, 'zip', source_dir)
    