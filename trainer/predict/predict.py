from easyocr import easyocr

if __name__ == '__main__':
    reader = easyocr.Reader(
        ['ru'],
        model_storage_directory='custom_EasyOCR/model',
        user_network_directory='custom_EasyOCR/user_network',
        recog_network='custom_example'
    )
    image = 'obj446_ufms.jpg'
    result = reader.readtext(image)
    for r in result:
        print(r[1] + ' ')
