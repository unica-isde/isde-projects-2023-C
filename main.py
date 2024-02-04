import json
from typing import Dict, List
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import redis
from rq import Connection, Queue
from rq.job import Job
from app.config import Configuration
from app.forms.classification_form import ClassificationForm
from app.forms.classification_form_upload import ClassificationFormUpload
from app.forms.transform_image_form import TransformImageForm
from app.ml.classification_utils import classify_image, fetch_image
from app.utils import list_images
from app.image_transform import TransformWrapper
from io import BytesIO
import base64, os

app = FastAPI()
config = Configuration()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/info")
def info() -> Dict[str, List[str]]:
    """Returns a dictionary with the list of models and
    the list of available image files."""
    list_of_images = list_images()
    list_of_models = Configuration.models
    data = {"models": list_of_models, "images": list_of_images}
    return data


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """The home page of the service."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/classifications")
def create_classify(request: Request):
    return templates.TemplateResponse(
        "classification_select.html",
        {"request": request, "images": list_images(), "models": Configuration.models},
    )


@app.post("/classifications")
async def request_classification(request: Request):
    form = ClassificationForm(request)
    await form.load_data()
    image_id = form.image_id
    model_id = form.model_id
    classification_scores = classify_image(model_id=model_id, img_id=image_id)

    return templates.TemplateResponse(
        "classification_output.html",
        {
            "request": request,
            "image_id": image_id,
            "classification_scores": json.dumps(classification_scores),
        },
    )


@app.get("/classifications_upload")
def create_classify_upload(request: Request):
    """ Returns a form which enables the user to upload an JPEG/JPG image to be classified."""

    return templates.TemplateResponse(
        "classification_upload.html",
        {"request": request, "models": Configuration.models},
    )


@app.post("/classifications_upload")
async def request_classification_upload(request: Request):
    """
    Handles the HTTP POST form request which enables the user to upload an JPEG/JPG image to be classified.
    If errors occur, the page will reload to show them.
    """

    form = ClassificationFormUpload(request)
    await form.load_data()

    if form.is_valid():
        model_id = form.model_id
        image_id = form.image_id

        await form.save_image()  # save image before classifying it!

        classification_scores = classify_image(model_id=model_id, img_id=image_id)
        return templates.TemplateResponse(
            "classification_output.html",
            {
                "request": request,
                "image_id": image_id,
                "classification_scores": json.dumps(classification_scores),
            },
        )
    else:
        return templates.TemplateResponse(
            "classification_upload.html",
            {"request": request, "models": Configuration.models, "errors":form.errors},
        )


@app.get("/transform_image")
def transform(request: Request):
    """
    Returns a form to enable the user to apply the available transformations in separate module
    """
    return templates.TemplateResponse(
        "transform_image.html",
        {"request": request, "images": list_images(), "transforms": TransformWrapper().transforms},
    )


@app.post("/transform_image")
async def transform_image(request: Request):
    """
    Handles the POST request to transform the image based on the wrapper class.
    """
    form = TransformImageForm(request)
    await form.load_data()
    image_id = form.image_id
    transforms = form.transforms

    if form.is_valid():
        # Apply transformations only if the form is valid
        img = fetch_image(image_id)
        img = TransformWrapper().apply_transform(img, transforms)

        # Convert image to base64
        buff = BytesIO()
        img.save(buff, format="JPEG")
        image_b64 = base64.b64encode(buff.getvalue())
        image_b64 = image_b64.decode("utf-8")

        response = templates.TemplateResponse(
            "transform_image_output.html",
            {
                "request": request,
                "image_id": image_id,
                "image": image_b64
            },
        )

        response.headers["cache-control"] = "no-store"
        return response

