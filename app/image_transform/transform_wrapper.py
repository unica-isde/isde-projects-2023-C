from PIL import ImageEnhance, Image


class TransformWrapper():
    """
    Wrapper class which enables the user to apply transformations.
    Default values use ImageEnhance
    """
    def set_transform_type(self, fun, name="name", min=0.0, max=2.0, default=1.0):
        """
        Returns a dictionary item for the _transform attribute
        """
        return {
            name: {
                "function": fun,
                "min": min,
                "max": max,
                "default": default
            }
        }

    def __init__(self):
        self._transform = {}
        self._transform.update(self.set_transform_type(ImageEnhance.Color, "color"))
        self._transform.update(self.set_transform_type(ImageEnhance.Contrast, "contrast"))
        self._transform.update(self.set_transform_type(ImageEnhance.Brightness, "brightness"))
        self._transform.update(self.set_transform_type(ImageEnhance.Sharpness, "sharpness"))


    @property
    def get_transforms(self):
        return self._transform

    def get_transform_names(self):
        return self._transform.keys()

    def apply_single_transform(self, img, name: str, value: float):
        """
        Apply a single transformation
        Input: img (PIL Image), name of the transformation, value of the transformation
        Output: PIL image
        """
        transform = self._transform[name]['function']
        if transform is None:
            raise NotImplementedError

        if value == self._transform[name]['default']:
            return img

        return transform(img).enhance(value)

    def apply_transform(self, img, transform: dict):
        """
        Function that applies the transformations in batch.
        Input: img (PIL Image), dictionary of transformation (name and value needed)
        """
        e = img
        for name, value in transform.items():
            e = self.apply_single_transform(e, name, float(value))
            e.save(img.filename)
        return e





