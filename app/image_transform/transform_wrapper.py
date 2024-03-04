from PIL import ImageEnhance, Image


class TransformWrapper:
    """
    Wrapper class which enables the user to apply transformations.
    Default values use ImageEnhance
    """
    @staticmethod
    def set_transform_type(fun, name="name", min_value=0.0, max_value=2.0, default=1.0, step=0.1):
        """
        Returns a dictionary item for the _transform attribute
        """
        return {
            name: {
                "function": fun,
                "min": min_value,
                "max": max_value,
                "default": default,
                "step": step
            }
        }

    def __init__(self):
        self._transforms = {}
        self._transforms.update(self.set_transform_type(
            ImageEnhance.Color, "Color", min_value=-100, max_value=100, step=1)
        )
        self._transforms.update(self.set_transform_type(ImageEnhance.Contrast, "Contrast"))
        self._transforms.update(self.set_transform_type(ImageEnhance.Brightness, "Brightness"))
        self._transforms.update(self.set_transform_type(ImageEnhance.Sharpness, "Sharpness"))

    @property
    def transforms(self):
        return self._transforms

    def apply_single_transform(self, img: Image, name: str, value: float):
        """
        Apply a single transformation
        Input: img (PIL Image), name of the transformation, value of the transformation
        Output: PIL image
        """
        transform = self._transforms[name]['function']
        if transform is None:
            raise NotImplementedError

        if value == self._transforms[name]['default']:
            return img

        return transform(img).enhance(value)

    def apply_transform(self, img: Image, transform: dict):
        """
        Function that applies the transformations in batch.
        Input: img (PIL Image), dictionary of transformation (name and value needed)
        """
        e = img
        for name, value in transform.items():
            e = self.apply_single_transform(e, name, float(value))
        return e
