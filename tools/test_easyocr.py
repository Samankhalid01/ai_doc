import easyocr

reader = easyocr.Reader(['en'])
res = reader.readtext('debug_page_0.png', detail=0)
print('EasyOCR result length:', len(res))
print(res)