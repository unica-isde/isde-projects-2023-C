from typing import List

import starlette.datastructures
from fastapi import Request, UploadFile

from app.config import Configuration


# https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
class ClassificationFormUpload:
    def __init__(self, request: Request) -> None:
        self.request: Request = request
        self.errors: List = []
        self.image_file: UploadFile
        self.image_id: str
        self.model_id: str

    async def load_data(self):
        form = await self.request.form()
        self.image_file = form.get("immagine")
        self.model_id = form.get("model_id")
        self.image_id = self.image_file.filename

    def is_valid(self):
        # FastAPI bug https://github.com/tiangolo/fastapi/discussions/9705
        if not self.image_file or not isinstance(self.image_file, starlette.datastructures.UploadFile) \
                or not self.image_file.filename.upper().endswith((".JPEG", ".JPG")):
            self.errors.append("A valid JPEG image is required")
        if not self.image_id or not isinstance(self.image_id, str):
            self.errors.append("A valid image filename is required")
        if not self.model_id or not isinstance(self.model_id, str):
            self.errors.append("A valid model id is required")
        if not self.errors:
            return True
        return False

    async def save_image(self):

        # save the image
        # can't check if it already exists in the best way, we would need to modify the "prepare image file"
        # in order to calculate all the pre-existing images hashes, but we can't:
        # <<The old functionalities should be preserved, this is an additional feature.>>
        # We can check if filename already exists, but it would negatively impact performance with a big number of
        # pre-existing images.
        # We can just re-write the old image for now.

        with open(Configuration.image_folder_path + "/" + self.image_id, mode='wb') as f:
            await self.image_file.seek(0)  # wait to seek file cursor at the start of the tempfile
            f.write(await self.image_file.read())  # read all the tempfile at once and save it as a permanent file,
