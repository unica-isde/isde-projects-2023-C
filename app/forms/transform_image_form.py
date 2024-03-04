from typing import List
from fastapi import Request
from app.image_transform import TransformWrapper


class TransformImageForm:
    def __init__(self, request: Request) -> None:
        self.request: Request = request
        self.errors: List = []
        self.image_id: str
        self.transforms: dict = {}

    async def load_data(self):
        form = await self.request.form()
        self.image_id = form.get("image_id")
        for t in TransformWrapper().transforms:
            self.transforms.update({t: form.get(t)})

    def is_valid(self):
        if not self.transforms or not isinstance(self.transforms, dict):
            self.errors.append("A valid dictionary of transformations is required")
        if not self.image_id or not isinstance(self.image_id, str):
            self.errors.append("A valid image id is required")
        if not self.errors:
            return True
        return False
