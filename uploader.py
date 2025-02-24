import os
import re
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

photo_path = os.environ.get("PHOTO_PATH")

def get_exif_datetime(image_path):
    """ 画像のEXIFデータから撮影日時を取得 """
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if exif_data is not None:
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "DateTimeOriginal":
                    return value  # 'YYYY:MM:DD HH:MM:SS' 形式
    except Exception as e:
        print(f"エラー: {image_path} のEXIFデータ取得に失敗 - {e}")
    
    return None

def extract_serial_number(filename):
    """ ファイル名 (例: DSC00002.JPG) から連番部分 (00002) を抽出 """
    match = re.search(r"(\d{5})\.jpg$", filename, re.IGNORECASE)
    if match:
        return match.group(1)  # 例: "00002"
    return None  # 連番なし

def rename_photos(directory):
    """ 指定ディレクトリ内の写真を撮影日時でリネーム """
    for filename in os.listdir(directory):
        if filename.lower().endswith(".jpg"):  # JPGファイルのみ対象
            file_path = os.path.join(directory, filename)

            # 撮影日時を取得
            exif_datetime = get_exif_datetime(file_path)
            if exif_datetime:
                # 'YYYY:MM:DD HH:MM:SS' → 'YYYYMMDDHHMM'
                timestamp_str = datetime.strptime(exif_datetime, "%Y:%m:%d %H:%M:%S").strftime("%Y%m%d%H%M")

                # 連番部分を抽出 (例: DSC00002.JPG → "00002")
                serial_number = extract_serial_number(filename)

                # 新しいファイル名の組み立て
                new_filename = timestamp_str
                if serial_number:
                    new_filename += f"_{serial_number}"  # "_00002" を追加
                new_filename += ".JPG"

                new_file_path = os.path.join(directory, new_filename)

                # ファイル名をリネーム
                os.rename(file_path, new_file_path)
                print(f"リネーム: {filename} → {new_filename}")

            else:
                print(f"スキップ: {filename} の撮影日時が取得できませんでした")

if __name__ == "__main__":
    rename_photos(photo_path)
