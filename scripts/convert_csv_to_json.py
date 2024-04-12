import csv
import hashlib
import json
import os

LANGUAGE = os.getenv("XZ_LANGUAGE") or "zh_Hans"

DIR_JSON_ORIGINAL = "original_files/json"
DIR_JSON_TRANSLATED = f"texts/{LANGUAGE}"
DIR_CSV_TRANSLATED = f"texts/{LANGUAGE}"


def get_sheet(sheet_name: str) -> dict[str, str]:
  csvfile = open(f"{DIR_CSV_TRANSLATED}/{sheet_name}.csv", "r", -1, "utf8", "ignore", "")
  reader = csv.reader(csvfile)

  row_iter = reader
  headers = next(row_iter)
  translations: dict[str, str] = {}
  for row in row_iter:
    item_dict = dict(zip(headers, row))
    translations[item_dict["id"]] = item_dict["target"].replace("\\r", "\r")

  return translations


# Scripts
os.makedirs(f"{DIR_JSON_TRANSLATED}/scrpt.cpk", exist_ok=True)
for file_name in os.listdir(f"{DIR_JSON_ORIGINAL}/scrpt.cpk"):
  if not file_name.endswith(".json"):
    continue

  with open(f"{DIR_JSON_ORIGINAL}/scrpt.cpk/{file_name}", "r", -1, "utf8") as reader:
    data = json.load(reader)
    messages = data["message"]
  if len(messages) < 1:
    continue

  sheet_name = f"scrpt.cpk/{file_name.removesuffix('.json')}"
  translations = get_sheet(sheet_name)

  for i, item in enumerate(messages):
    function = item["function"]
    if function == "XMESS":
      text_id = f"{function}_{item['msgidx']:04d}"
      translation = translations[text_id]
      item["argument"] = translation.split("\n")
    elif function == "MSTD":
      for choice_i, choice in enumerate(item["argument"][3:]):
        line, _, text_id = choice.split(",")
        translation = translations[text_id]
        item["argument"][3 + choice_i] = f"{translation},{_},{text_id}"
      continue
    else:
      continue

  with open(f"{DIR_JSON_TRANSLATED}/scrpt.cpk/{file_name}", "w", -1, "utf8", "ignore", "\n") as writer:
    json.dump(data, writer, ensure_ascii=False, indent=2)

  print(f"Converted: {file_name}")

# OmakeData
if True:
  omake_translations = get_sheet("OmakeData")
  file_name = "OmakeData_603d8b201237d579.json"
  with open(f"{DIR_JSON_ORIGINAL}/{file_name}", "r", -1, "utf8") as reader:
    data = json.load(reader)

  for sublist in [x["items"] for x in data["pages"]]:
    for item in sublist:
      item["title"] = omake_translations[item["title"]]

  with open(f"{DIR_JSON_TRANSLATED}/{file_name}", "w", -1, "utf-8") as writer:
    json.dump(data, writer, indent=2, ensure_ascii=False)
  print(f"Converted: {file_name}")

  file_name = "OmakeData_d1cca4806d0942fd.json"
  with open(f"{DIR_JSON_ORIGINAL}/{file_name}", "r", -1, "utf8") as reader:
    data = json.load(reader)

  for sublist in [x["items"] for x in data["pages"]]:
    for item in sublist:
      title = item["title"].split("　")[-1]
      item["title"] = item["title"].replace(title, omake_translations[title], 1)

  with open(f"{DIR_JSON_TRANSLATED}/{file_name}", "w", -1, "utf-8") as writer:
    json.dump(data, writer, indent=2, ensure_ascii=False)
  print(f"Converted: {file_name}")

# Text
if True:
  text_translations = get_sheet("Text")
  file_name = "Text.json"
  with open(f"{DIR_JSON_ORIGINAL}/{file_name}", "r", -1, "utf8") as reader:
    data = json.load(reader)

  for k, v in data.items():
    md5 = hashlib.md5(k.encode("utf-8")).hexdigest()
    if f"text#{md5}" not in text_translations:
      continue
    data[k] = text_translations[f"text#{md5}"]

  with open(f"{DIR_JSON_TRANSLATED}/{file_name}", "w", -1, "utf-8") as writer:
    json.dump(data, writer, indent=2, ensure_ascii=False)
  print(f"Converted: {file_name}")
