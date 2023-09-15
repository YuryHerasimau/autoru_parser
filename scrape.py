import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
}


def download_image(url, folder, filename):
    response = requests.get(url, headers=headers)
    with open(os.path.join(folder, filename), 'wb') as f:
        f.write(response.content)

def parse_photos_from_ads(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    driver.get(url=url)
    time.sleep(12)

    soup = BeautifulSoup(driver.page_source, "lxml")
    brands = soup.find_all(class_='IndexMarks__item')
    for brand in brands[:10]:                                                           # Parse the first 10 brands
        brand_name = brand.find_all('div', class_='IndexMarks__item-name')[0].string    # LADA (ВАЗ)
        brand_folder = os.path.join('photos', brand_name)
        os.makedirs(brand_folder, exist_ok=True)

        brand_url = brand.get('href')                                                   # https://auto.ru/cars/vaz/all/
        driver.get(url=brand_url)
        time.sleep(2)
        
        brand_soup = BeautifulSoup(driver.page_source, 'lxml')
        ad_list = brand_soup.find_all('a', class_='Link ListingItemTitle__link')        # Find the list of ads on the brand page
        for ad in ad_list[:10]:                                                         # Parse up to 10 ads
            ad_name = ad.text                                                           # LADA (ВАЗ) Granta I
            ad_folder = os.path.join(f'photos/{brand_name}', ad_name)
            os.makedirs(ad_folder, exist_ok=True)

            ad_url = ad.get('href')                                                     # https://auto.ru/cars/used/sale/vaz/granta/1119928464-3a63a769/
            driver.get(url=ad_url)
            time.sleep(1)

            print(f"{ad_name} -----------> {ad_url}")

            ad_soup = BeautifulSoup(driver.page_source, 'lxml')
            photo_list = ad_soup.find_all('img', class_='ImageGalleryDesktop__image')   # Find the list of photos in the ad
            for j, photo in enumerate(photo_list[:5]):                                  # Download up to 5 photos from the ad
                photo_url = f"https:{photo.get('src')}"
                photo_filename = f'photo{j+1}.jpg'
                download_image(photo_url, ad_folder, photo_filename)

def main():
    parse_photos_from_ads(url='https://auto.ru')

if __name__ == "__main__":
    main()
