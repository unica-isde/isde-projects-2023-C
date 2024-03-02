from typing import List

import PIL
import magic

import starlette.datastructures
from fastapi import Request, UploadFile

from app.config import Configuration


# https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
class ClassificationFormUpload:
    _MAGIC_BYTES_TO_READ = 2048  # magic package documentation on GitHub suggests reading at least 2048 bytes.

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

    async def is_valid(self):
        # FastAPI bug https://github.com/tiangolo/fastapi/discussions/9705
        if not self.image_file or not isinstance(self.image_file, starlette.datastructures.UploadFile) \
                or not self.image_file.filename.endswith(".JPEG"):  # utils.list_images() accepts only '.JPEG' extension
            self.errors.append("A valid .JPEG image is required (check file extension, it must be uppercase too!)")

        try:
            await self.image_file.seek(0)
            if 'JPEG image' not in magic.from_buffer(
                    await self.image_file.read(ClassificationFormUpload._MAGIC_BYTES_TO_READ)
            ):
                self.errors.append("You inserted a file which is not a valid JPEG image!")
        except magic.MagicException:
            self.errors.append("We couldn't recognize the file you sent! Are you sure it was a JPEG image?")

        if not self.image_id or not isinstance(self.image_id, str):
            self.errors.append("A valid image filename is required")

        if not self.model_id or not isinstance(self.model_id, str):
            self.errors.append("A valid model id is required")

        if not self.errors:
            return True
        # Deny default
        # If any error happens, get rid of the image_file without waiting for garbage collection
        await self.image_file.close()   # This should close its internal SpooledTemporaryFile,
                                        # effectively eliminating it from memory in case an error occurs.
                                        # We just explicitly insert this line for readability,
                                        # But it should get executed by python's garbage collector too!
        return False
