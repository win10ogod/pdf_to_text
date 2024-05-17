# 使用方式
# 下載依賴項：


pip install tqdm requests PyPDF2 PyMuPDF pytesseract pdf2image srt
# 使用示例：

# 1.單個 PDF 文件轉換為文本：

python convert_tool.py -i example.pdf -t output.txt -j output.json --pdf
# 2.單個 SRT 文件轉換為文本：

python convert_tool.py -i example.srt -t output.txt -j output.json --srt
# 3.批量處理 PDF 文件夾：

python convert_tool.py -b /path/to/pdf/folder --pdf --output-dir /path/to/output/folder
# 4.從網絡下載 PDF 文件並進行轉換：

python convert_tool.py --url https://example.com/document.pdf -t output.txt -j output.json --pdf
# 注意事項
若要使用 pdf2image，需要安裝 poppler，可參考官方指引。
確保 tesseract 已正確安裝並配置。
