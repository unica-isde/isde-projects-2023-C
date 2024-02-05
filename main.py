import io
import json
import matplotlib.pyplot as plot
from typing import Dict, List
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import Configuration
from app.forms.classification_form import ClassificationForm
from app.forms.classification_form_upload import ClassificationFormUpload
from app.ml.classification_utils import classify_image
from app.utils import list_images

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

@app.get("/histogram")# ADDED
def create_histogram(request: Request):
    """ Page in which an image can be selected for its histogram generation. """
    return templates.TemplateResponse(
        "histogram_select.html",
        {"request": request, "images": list_images()},
    )


@app.post("/histogram") # ADDED
async def request_histogram(request: Request):
    """ Page in which the histogram of the selected image is generated and showed. """
    form = ClassificationForm(request)
    await form.load_data()
    image_id = form.image_id
    return templates.TemplateResponse(
        "histogram_output.html",
        {
            "request": request,
            "image_id": image_id,
        },
    )

@app.get("/download_results/{image_id}")
def download_results(classification_scores: str):
    classification_scores_dict = json.loads(classification_scores)
    json_content = json.dumps(classification_scores_dict, indent=4)

    # Json file streaming
    def generate():
        yield json_content.encode()

    # Return a StreamingResponse
    return StreamingResponse(
        generate(),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment"}
    )


@app.get("/download_plot/{image_id}")
async def download_results(classification_scores: str):
    classification_scores_dict = json.loads(classification_scores)

    # Pick up the values for the plot
    categories = [item[0] for item in classification_scores_dict]
    values = [item[1] for item in classification_scores_dict]

    # Graph creation
    sorted_indices = sorted(range(len(values)), key=lambda k: values[k], reverse=False)
    categories = [categories[i] for i in sorted_indices]
    values = [values[i] for i in sorted_indices]
    plot.figure(figsize=(10, len(categories) * 0.5))
    plot.barh(categories, values, color=['#3F0355', '#06216C', '#795703', '#750014', '#1A4A04'])
    plot.title('Output Scores')
    plot.margins(y=0.01)
    plot.tight_layout()
    plot.grid(True)

    # Save graph as png
    image_stream = io.BytesIO()
    plot.savefig(image_stream, format='png')
    image_stream.seek(0)
    plot.close()

    # Return a StreamingResponse
    return StreamingResponse(io.BytesIO(image_stream.read()), media_type="image/png")
