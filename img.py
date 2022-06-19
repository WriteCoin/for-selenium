import base64
import os
import uuid
from PIL import Image

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def compress_img(image_name, new_size_ratio=0.9, quality=90, width=None, height=None, to_jpg=True) -> str:
    # load the image to memory
    img = Image.open(image_name)
    # print the original image shape
    print("[*] Image shape:", img.size)
    # get the original image size in bytes
    image_size = os.path.getsize(image_name)
    # print the size before compression/resizing
    print("[*] Size before compression:", get_size_format(image_size))
    if new_size_ratio < 1.0:
        # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
        img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)
        # print new image shape
        print("[+] New Image shape:", img.size)
    elif width and height:
        # if width and height are set, resize with them instead
        img = img.resize((width, height), Image.ANTIALIAS)
        # print new image shape
        print("[+] New Image shape:", img.size)
    # split the filename and extension
    filename, ext = os.path.splitext(image_name)
    # make new filename appending _compressed to the original file name
    if to_jpg:
        # change the extension to JPEG
        new_filename = f"{filename}_compressed.jpg"
    else:
        # retain the same extension of the original image
        new_filename = f"{filename}_compressed{ext}"
    try:
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
    except OSError:
        # convert the image to RGB mode first
        img = img.convert("RGB")
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
    print("[+] New file saved:", new_filename)
    # get the new image size in bytes
    new_image_size = os.path.getsize(new_filename)
    # print the new size in a good format
    print("[+] Size after compression:", get_size_format(new_image_size))
    # calculate the saving bytes
    saving_diff = new_image_size - image_size
    # print the saving percentage
    print(f"[+] Image size change: {saving_diff/image_size*100:.2f}% of the original image size.")
    return new_filename

def base64_to_image_file(text: str) -> str:
  image_recovered = base64.b64decode(text)
  filename = str(uuid.uuid4())
  filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), f"images/{filename}.jpeg")
  with open(filepath, "wb") as file:
    file.write(image_recovered)
  return filepath

def image_file_to_base64(filepath: str) -> str:
  with open(filepath, 'rb') as file:
    encoded_string = base64.b64encode(file.read()).decode("utf-8")
    return encoded_string

def base64_to_compress_base64(data: str) -> str:
  filepath = base64_to_image_file(data)
  new_filepath = compress_img(filepath, 0.95)
  try:
    os.remove(filepath)
  except OSError as ex:
    print(ex)
  result = image_file_to_base64(new_filepath)
  try:
    os.remove(new_filepath)
  except OSError as ex:
    print(ex)
  return result

if __name__ == '__main__':
  with open("input.txt", "r") as file: 
    result = base64_to_compress_base64(file.read())
    # print(result)
    with open('output.txt', "w") as file:
      file.write(result)
    # base64text = file.read()
    # filepath = base64_to_image_file(base64text)
    # compress_img(filepath, 1)