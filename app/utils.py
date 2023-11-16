import os

from fastapi import UploadFile

from app.config import Configuration

conf = Configuration()


def list_images():
    """Returns the list of available images."""
    img_names = filter(
        lambda x: x.endswith(".JPEG"), os.listdir(conf.image_folder_path)
    )
    return list(img_names)


async def save_image(image: UploadFile, path=Configuration.image_folder_path):
    """
    Saves an image as a file inside path (default: Configuration.image_folder_path).
    If a file with the same name as image already exists in path, it gets overwritten!
    If you want to change the image filename, just change its attribute 'filename' before
    passing it as an input to this function, example (REMEMBER THE .JPEG FILE EXTENSION!):

        image.filename = "new_name.JPEG"

    Notice that the extension must be uppercase in order for it to appear in the dropdown HTML menu! (see utils.list_images())
    """
    with open(path + "/" + image.filename, mode='wb') as f:
        await image.seek(0)  # wait to seek file cursor at the start of the tempfile
        f.write(await image.read())  # read all the tempfile at once and save it as a permanent file,
