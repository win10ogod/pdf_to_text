import os
import json
import argparse
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from pdf2image import convert_from_path
import pytesseract
import PyPDF2
import srt
import chardet


def download_file(url, output_dir):
    """下載網絡文件."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    output_path = os.path.join(output_dir, filename)
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    with open(output_path, 'wb') as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
        for chunk in response.iter_content(32 * 1024):
            f.write(chunk)
            pbar.update(len(chunk))
    return output_path


def extract_text_from_pdf(pdf_path):
    """從 PDF 文件提取文本."""
    text = ""
    reader = PyPDF2.PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_text_from_pdf_ocr(pdf_path):
    """從 PDF 文件使用 OCR 提取文本（適用於掃描件）."""
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text


def extract_text_from_srt(srt_path):
    """從 SRT 文件提取文本。"""
    # 檢測文件編碼
    with open(srt_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    # 使用檢測到的編碼讀取文件
    with open(srt_path, 'r', encoding=encoding) as file:
        subtitles = srt.parse(file.read())

    return "\n".join([subtitle.content for subtitle in subtitles])


def save_as_txt(text, output_path):
    """保存為 txt 文件."""
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)


def save_as_json(text, output_path):
    """保存為 json 文件."""
    data = {"content": text}
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def process_file(input_path, output_txt=None, output_json=None, file_type=None):
    """處理單個文件."""
    if file_type == 'pdf':
        try:
            text = extract_text_from_pdf(input_path)
        except Exception as e:
            print(f"Error extracting text from {input_path}: {e}. Trying OCR.")
            text = extract_text_from_pdf_ocr(input_path)
    elif file_type == 'srt':
        text = extract_text_from_srt(input_path)
    else:
        raise ValueError("Invalid file type specified.")

    if output_txt:
        save_as_txt(text, output_txt)
    if output_json:
        save_as_json(text, output_json)


def process_directory(input_dir, output_dir, file_type):
    """處理文件夾中的所有文件."""
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file_type == 'pdf' and file.lower().endswith('.pdf'):
                input_path = os.path.join(root, file)
                output_txt = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.txt")
                output_json = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.json")
                process_file(input_path, output_txt, output_json, file_type=file_type)
            elif file_type == 'srt' and file.lower().endswith('.srt'):
                input_path = os.path.join(root, file)
                output_txt = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.txt")
                output_json = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.json")
                process_file(input_path, output_txt, output_json, file_type=file_type)


def main():
    parser = argparse.ArgumentParser(description="將 PDF 或 SRT 文件轉換為文本數據集的工具。")
    parser.add_argument('-i', '--input', type=str, help='輸入文件或文件夾路徑')
    parser.add_argument('-t', '--txt', type=str, help='輸出 txt 文件路徑')
    parser.add_argument('-j', '--json', type=str, help='輸出 json 文件路徑')
    parser.add_argument('-b', '--batch', type=str, help='批量處理文件夾')
    parser.add_argument('--pdf', action='store_true', help='處理 PDF 文件')
    parser.add_argument('--srt', action='store_true', help='處理 SRT 文件')
    parser.add_argument('--url', type=str, help='從網絡下載文件並處理')
    parser.add_argument('--output-dir', type=str, help='批量處理文件夾輸出路徑', default='output')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.pdf:
        file_type = 'pdf'
    elif args.srt:
        file_type = 'srt'
    else:
        raise ValueError("必須指定 --pdf 或 --srt 之一作為文件類型。")

    if args.url:
        input_path = download_file(args.url, args.output_dir)
        process_file(input_path, args.txt, args.json, file_type=file_type)
    elif args.input:
        process_file(args.input, args.txt, args.json, file_type=file_type)
    elif args.batch:
        process_directory(args.batch, args.output_dir, file_type=file_type)
    else:
        raise ValueError("必須指定 --input、--url 或 --batch 之一作為輸入文件。")


if __name__ == '__main__':
    main()