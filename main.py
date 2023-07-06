from facebook import FacebookScraper
import time
import configparser
import pandas as pd

MAX_RETRY = 5

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    with open("urls.txt", "r") as f:
        urls = f.readlines()

    with FacebookScraper(debug=True) as scraper:
        scraper.login(config.get('Facebook', 'email'), config.get('Facebook', 'password'))
        time.sleep(1)
        for i, url in enumerate(urls):
            print(f"processing in url {i}")
            scraper.logger.info(f"processing in url {i}")
            retry = 0
            while retry < MAX_RETRY:
                if retry:
                    print(f"retrying in url {i}")
                    scraper.logger.info(f"retrying in url {i}")

                time.sleep(5)

                try:
                    fan_page_name = url.split("/")[3]
                    reviews = scraper.get_reviews(url)
                    df = pd.DataFrame(reviews)
                    df.to_csv(f"{fan_page_name}.csv")
                    break
                except Exception as e:
                    scraper.logger.warning(e)
                    retry += 1
