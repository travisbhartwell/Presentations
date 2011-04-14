from selenium import webdriver
import time
import os

from config import amazon_password, amazon_username
CLOUD_PLAYER_URL = "http://www.amazon.com/gp/dmusic/mp3/player/ref=sa_menu_mp3_acp1"
PLAYLIST_LINK = "https://www.amazon.com/gp/dmusic/mp3/player?ie=UTF8&ref_=sa_menu_mp3_acp1&#latestPurchases"

driver = webdriver.Chrome()
#driver = webdriver.Firefox()
driver.get(CLOUD_PLAYER_URL)
driver.find_element_by_name("email").send_keys(amazon_username)
driver.find_element_by_name("password").send_keys(amazon_password)
driver.find_element_by_id("signInSubmit").click()

driver.wait_for_load_complete()
driver.get(PLAYLIST_LINK)

"""
<input type="checkbox" class="checkbox checkAll" itemtype="song">
"""
time.sleep(5)
checkbox = driver.find_element_by_class_name("checkbox checkAll")
checkbox.click()

"""
<span class="multiAction decoration buttonCenter" allactionname="Download" multiactionname="Download" itemtype="song" actiontype="download">Download</span>
"""

buttons = driver.find_elements_by_class_name("multiAction decoration buttonCenter")
for button in buttons:
    if button.get_attribute("allactionname") == "Download":
        button.click()
        break

driver.quit()

# Grab latest .amz file from downloads directory
download_dir = os.path.expanduser("~/Downloads")
files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)]
m_times = [(os.stat(f).st_mtime, f) for f in files if f.endswith(".amz")]
m_times.sort(key = lambda x: x[0])

latest = m_times[-1][1]

os.chdir(download_dir)
os.system("clamz %s" % latest)


