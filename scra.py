#check youtube channels for new videos
##############################################################################################
from selenium import webdriver
from selenium.common import exceptions as seleExceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

import zipfile

# import pyminizip
import os
import time

options = webdriver.firefox.options.Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.set_window_size(1000, 1080)

#automatically open channels with new videos in firefox
openURL = True
firefoxPath = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'

def getVidFromChannel(channelUrl):
    try:
        driver.get(channelUrl)
        while True:
            loaded = driver.execute_script('return document.readyState')
            if(loaded == 'complete'):
                break
            else:
                time.sleep(0.2)
        
        #check if I have to agree to a cookie banner
        try:
            ariaLabel = 'Agree to the use of cookies and other data for the purposes described'
            xPath = f'//button[@aria-label="{ariaLabel}"]'
            agree = driver.find_element(by=By.XPATH, value=xPath)
            print('cookie banner in the way, clicking it')
            agree.click()
        except seleExceptions.NoSuchElementException:
            try:
                xPath = f'//button[@aria-label="Accept all"]'
                agree = driver.find_element(by=By.XPATH, value=xPath)
                print('cookie banner in the way, clicking it')
                agree.click()
            except seleExceptions.NoSuchElementException:
                #print('no cookie banner in the way')
                pass
        finally:
            vidTitle = None
            try:
                firstVidxPath = '//div[@class="style-scope ytd-rich-item-renderer"]'
                firstVidDiv = WebDriverWait(driver, 8).until(
                ec.presence_of_element_located( (By.XPATH, firstVidxPath) ))
                vidTitle = firstVidDiv.find_element(by=By.XPATH, value='.//a[@id="video-title-link"]')
            except seleExceptions.TimeoutException as ex:
                print("youtube's older grid renderer got loaded")
                firstVidxPath = '//div[@class="style-scope ytd-grid-video-renderer"]'
                firstVidDiv = WebDriverWait(driver, 8).until(
                    ec.presence_of_element_located( (By.XPATH, firstVidxPath) ))
                vidTitle = firstVidDiv.find_element(by=By.XPATH, value='.//a[@id="video-title"]')
            finally:
                #get the video's unique hash from the end of its url
                vidHash = vidTitle.get_attribute('href')
                if 'v=' in vidHash:
                    vidHash = vidHash.split('v=')[1]
                elif 'shorts' in vidHash:
                    #the page links the last video not as a "/watch?v=hash" but as
                    #https://www.youtube.com/shorts/hash => can still access the vid as "/watch?v=hash"
                    vidHash = vidHash.split('/')[-1]
                else:
                    print(f'new type of video found: {vidHash}')
                    exit()
                return vidTitle.text, vidHash
    
    except seleExceptions.NoSuchElementException:
        print('no such element')
        #quit driver upon error
        driver.quit()


# password = os.environ['MYZIP_PASSWORD']

# pyminizip.uncompress('channels.zip', '.', password, True)

# with ZipFile.extract(member, path=None, pwd=None)      ZipFile('channels.zip', 'r') as zip_file:
#     zip_file.setpassword(bytes(password,'utf-8'))
#     with zip_file.open('channels.csv') as f:
#         channels = f.readlines()


# with zipfile.ZipFile('channels.zip') as zip_file:
#     with zip_file.open('channels.csv', pwd=bytes(password,'utf-8')) as f:
#         channels = f.readlines()



with zipfile.ZipFile('channels.zip') as zip_file:
    password = os.environ['MYZIP_PASSWORD'].encode('utf-8')
    zip_file.extractall(path=os.environ['GITHUB_WORKSPACE'], pwd=password)

with open('channels.csv') as f:
    channels = f.readlines()





print(f'checking {len(channels)} channels:')
for i, channel in enumerate(channels):
    channel = channel.rstrip()
    channel = channel.split(',')
    while len(channel)>3:           #there was a , in the title
        channel[2] += ',' + channel.pop(3)
    channelURL = 'https://www.youtube.com/' + channel[1] + '/videos'
    
    #compare the last saved video hash with the newest video's hash
    newestTitle, newestHash = getVidFromChannel(channelURL)
    #remove utf characters
    newestTitle = newestTitle.encode('ascii', errors='ignore') #'replace' would make unicode
    newestTitle = newestTitle.decode('ascii', errors='ignore').rstrip()      #chars into '?'
    if i % 10 == 0 and i != 0:
        print()    
    print(f'{i:>2d}', end=' ')           #2 spaces for up to 2 digits, ">" = aligned right
    if channel[2] != newestHash:
        print(f'\n{channel[0]} has a new video: {newestTitle}')
        print(f'channel url: {channelURL}')
        if openURL:
            os.system(f'""{firefoxPath}" -new-tab "{channelURL}""')
            #yes, os.system() needs those extra surrounding double quotes to correctly use
            #commands which contain a "
        
    #replace each last video with the most current last video  
    channel[2] = newestHash
    channel = ','.join(channel) + '\n'
    channels[i] = channel
        
driver.quit()
#update the list
with open('channels.csv', 'w') as f:
    f.writelines(channels)





with zipfile.ZipFile(os.environ['GITHUB_WORKSPACE'] + '/' + 'channels.zip', 'w', zipfile.ZIP_DEFLATED) as myzip:
    password = os.environ['MYZIP_PASSWORD'].encode('utf-8')    
    myzip.setpassword(password)
    myzip.write('channels.csv')


# src_file = "/path/to/source/file.txt"
# dest_file = "/path/to/destination/file.zip"
# password = "mypassword"
# level = 0
# pyminizip.compress(src_file, None, dest_file, password, level)

# zip_file = zipfile.ZipFile('example.zip', 'w')
# zip_file.write('file1.txt')
# zip_file.write('file2.txt')
# zip_file.setpassword(b'my_password')
# zip_file.close()
