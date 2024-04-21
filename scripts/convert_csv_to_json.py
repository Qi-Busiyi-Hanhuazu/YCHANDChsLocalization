from collections.abc import Callable
import csv
import hashlib
import json
import os
import re
import shutil
from typing import Any

LANGUAGE = os.getenv("XZ_LANGUAGE") or "zh_Hans"

DIR_JSON_ORIGINAL = "original_files/json"
DIR_JSON_TRANSLATED = f"texts/{LANGUAGE}"
DIR_CSV_TRANSLATED = f"texts/{LANGUAGE}"


def handle_json(sheet_name: str, handler: Callable[[dict[str, str], Any], Any]) -> bool:
  if not os.path.exists(f"{DIR_CSV_TRANSLATED}/{sheet_name}.csv") or not os.path.exists(
      f"{DIR_JSON_ORIGINAL}/{sheet_name}.json"):
    return False

  with open(f"{DIR_JSON_ORIGINAL}/{sheet_name}.json", "r", -1, "utf8") as reader:
    data = json.load(reader)

  with open(f"{DIR_CSV_TRANSLATED}/{sheet_name}.csv", "r", -1, "utf8", "ignore", "") as csvfile:
    reader = csv.reader(csvfile)

    row_iter = reader
    headers = next(row_iter)
    translations: dict[str, str] = {}
    for row in row_iter:
      item_dict = dict(zip(headers, row))
      translations[item_dict["id"]] = item_dict["target"].replace("\\r", "\r")

  if not handler(translations, data):
    return False

  with open(f"{DIR_JSON_TRANSLATED}/{sheet_name}.json", "w", -1, "utf8", None, "\n") as writer:
    json.dump(data, writer, ensure_ascii=False, indent=2)
  print(f"Converted: {sheet_name}.json")
  return True


def scripts_handler(translations: dict[str, str], data: dict[str, Any]) -> bool:
  messages = data["message"]
  if len(messages) < 1:
    return False

  for i, item in enumerate(messages):
    function = item["function"]
    text_id = f"{function}_{i:04d}"
    translation = translations.get(text_id, "")
    if function == "XMESS":
      text_id = f"{function}_{item['msgidx']:04d}"
      translation = translations[text_id]
      item["argument"] = translation.split("\n")
    elif function == "MSTD":
      for choice_i, choice in enumerate(item["argument"][3:]):
        text_id = f"{function}_{i:04d}-{choice_i}"
        line, _ = choice.split(",", 1)
        translation = translations[text_id]
        item["argument"][3 + choice_i] = f"{translation},{_}"
      continue
    else:
      continue

  return True


def omake_603d8b2_data_handler(translations: dict[str, str], data: dict[str, Any]) -> bool:
  for sublist in [x["items"] for x in data["pages"]]:
    for item in sublist:
      item["title"] = translations[f"omake#{item['ofs']:02d}"]

  return True


def omake_d1cca48_data_handler(translations: dict[str, str], data: dict[str, Any]) -> bool:
  for sublist in [x["items"] for x in data["pages"]]:
    for item in sublist:
      title: str = item["title"]
      ofs = re.sub(r"[０-９]", lambda x: f"{ord(x.group(0)) - ord('０')}", re.search(r"ＣＧ№([０-９]+)", title).group(1))
      front, end = title.rsplit("　", 1)
      end = translations[f"omake#{int(ofs) - 1:02d}"]
      item["title"] = f"{front}　{end}"

  return True


def text_handler(translations: dict[str, str], data: dict[str, str]) -> bool:
  for k, v in data.items():
    md5 = hashlib.md5(k.encode("utf-8")).hexdigest()
    if f"text#{md5}" not in translations:
      continue
    data[k] = translations[f"text#{md5}"]

  return True


def metadata_handler(translations: dict[str, str], data: dict[str, dict[str, int | str]]) -> bool:
  for i, item in enumerate(data):
    item["text"] = translations[f"metadata#0x{item['position']:08x}+{item['length']}"]

  return True


os.makedirs(f"{DIR_JSON_TRANSLATED}/scrpt.cpk", exist_ok=True)
for file_name in os.listdir(f"{DIR_JSON_ORIGINAL}/scrpt.cpk"):
  if not file_name.endswith(".json"):
    continue

  handle_json(f"scrpt.cpk/{file_name.removesuffix('.json')}", scripts_handler)

shutil.copyfile("original_files/json/OmakeData_603d8b201237d579.json", "original_files/json/OmakeData.json")
handle_json("OmakeData", omake_603d8b2_data_handler)
shutil.copyfile("texts/zh_Hans/OmakeData.json", "texts/zh_Hans/OmakeData_603d8b201237d579.json")

shutil.copyfile("original_files/json/OmakeData_d1cca4806d0942fd.json", "original_files/json/OmakeData.json")
handle_json("OmakeData", omake_d1cca48_data_handler)
shutil.copyfile("texts/zh_Hans/OmakeData.json", "texts/zh_Hans/OmakeData_d1cca4806d0942fd.json")

os.remove("original_files/json/OmakeData.json")
os.remove("texts/zh_Hans/OmakeData.json")

handle_json("Text", text_handler)
handle_json("Metadata", metadata_handler)
