import os
import random
import requests
import zipfile


response = requests.get(f"https://www.zcool.com.cn/event/getFile.do?fileId=1200&t={random.random()}", headers={
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})
file_url = response.json()["fileUrl"]
response = requests.get(file_url)

os.makedirs("out", exist_ok=True)
with open("out/zcool.zip", "wb") as writer:
  writer.write(response.content)

with zipfile.ZipFile("out/zcool.zip", "r") as zfile:
  for file in zfile.filelist:
    try:
      file_name = file.filename.encode("cp437").decode("utf8", "ignore")
    except:
      continue
    if file_name != "站酷仓耳渔阳体（家族字体）/站酷仓耳渔阳体-W03.ttf":
      continue
  
    os.makedirs("files/fonts", exist_ok=True)
    with open(f"files/fonts/FOT-BudoStd-L.ttf", "wb") as writer:
      writer.write(zfile.read(file))