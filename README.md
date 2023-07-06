# FB review crawler

## Install

```shell
pip install -r requirements.txt
```

## Usage

1. 將想要爬取的紛絲評論頁放至 urls.txt 並以換行分隔
   ```shell
   https://www.facebook.com/JRSTAIWAN/reviews?locale=zh_TW
   https://www.facebook.com/JRSTAIWAN/reviews?locale=zh_TW
   https://www.facebook.com/JRSTAIWAN/reviews?locale=zh_TW
   ```
2. 在 config.ini 中輸入自己的 fb 帳號密碼
   ```shell
   [Facebook]
   email = example@yahoo.com.tw
   password = example
   ```
3. 執行 main.py
   ```shell
   python main.py
   ```
