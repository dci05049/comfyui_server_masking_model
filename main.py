from fastapi import FastAPI, Query
from fastapi import File, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import base64
import io
import comfyuiservice

app = FastAPI()

async def convert_image_to_base64(image_file):
    """
    Converts an uploaded image file to a Base64 string.
    """
    # Open the image from the uploaded file
    img = Image.open(BytesIO(await image_file.read()))
    
    # Save the image to a BytesIO object in the desired format
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)  # Reset stream pointer to the beginning

    # Encode the BytesIO content to Base64
    base64_encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
    return base64_encoded_image

async def save_base64_to_file(base64_data, filename):
    """
    Save a Base64 string to a text file.
    """
    with open(filename, "w") as file:
        file.write(base64_data)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; restrict to specific domains as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/image-prompt/")
async def get_image_with_prompt(
    input: str = Query(None)
):
    """
    Endpoint to process three images and return modified images as raw data.
    """
    # Load images into memory
    image = comfyuiservice.fetch_image_with_prompt(input)
    image_stream = io.BytesIO(image)
    return StreamingResponse(image_stream, media_type="image/png")


@app.post("/swap-cloth-model")
async def swap_cloth_on_model(
    mask_image: UploadFile = File(..., description="Mask image (JPG or PNG)"),
    cloth_image: UploadFile = File(..., description="Cloth image (JPG or PNG)"),
    model_image: UploadFile = File(..., description="Model person image (JPG or PNG)"),
):
    """
    Endpoint to process three images and return modified images as raw data.
    """
    # Load images into memory
    mask_image_base64 = await convert_image_to_base64(mask_image)
    cloth_image_base64 = await convert_image_to_base64(cloth_image)
    model_image_base64 = await convert_image_to_base64(model_image)

    result_image = comfyuiservice.get_model_image_with_cloth(cloth_base_64=cloth_image_base64, model_base_64=model_image_base64, mask_base_64=mask_image_base64)
    image_stream = io.BytesIO(result_image)
    return StreamingResponse(image_stream, media_type="image/png")

@app.post("/target-logo")
async def get_target_image_with_logo(
    mask_image: UploadFile = File(..., description="Mask image (JPG or PNG)"),
    logo_image: UploadFile = File(..., description="Logo image (JPG or PNG)"),
    target_image: UploadFile = File(..., description="Target output image (JPG or PNG)"),
):
    """
    Endpoint to process three images and return modified images as raw data.
    """
    # Load images into memory
    mask_image_base64 = await convert_image_to_base64(mask_image)
    target_image_base64 = await convert_image_to_base64(target_image)
    logo_image_base64 = await convert_image_to_base64(logo_image)

    result_image = comfyuiservice.get_target_image_with_logo(target_image_base64=target_image_base64, logo_image_base64=logo_image_base64, mask_image_base64=mask_image_base64)
    image_stream = io.BytesIO(result_image)
    return StreamingResponse(image_stream, media_type="image/png")

@app.post("/swap-face-image")
async def swap_face_and_create_new_image(
    reference_image: UploadFile = File(..., description="Mask image (JPG or PNG)"),
    user_prompt: str = Form(...),
):
    """
    Endpoint to process three images and return modified images as raw data.
    """
    # Load images into memory
    reference_image_base64 = await convert_image_to_base64(reference_image)
    # print(reference_image_base64)

    result_image = comfyuiservice.get_image_with_reference_pulid(reference_image_base64=reference_image_base64, prompt=user_prompt)
    image_stream = io.BytesIO(result_image)
    return StreamingResponse(image_stream, media_type="image/png")

@app.post("/outpaint-sdxl")
async def outpaint_sdxl(
    reference_image: UploadFile = File(..., description="Mask image (JPG or PNG)"),
    left: int = Form(...),
    right: int = Form(...),
    top: int = Form(...),
    bottom: int = Form(...),
):
    """
    Endpoint to process three images and return modified images as raw data.
    """

    # Load images into memory
    reference_image_base64 = await convert_image_to_base64(reference_image)
    result_image = comfyuiservice.get_image_with_outpainting_sdxl(reference_image_base64=reference_image_base64, left=left, right=right, top=top, bottom=bottom)
    image_stream = io.BytesIO(result_image)
    return StreamingResponse(image_stream, media_type="image/png")

@app.post("/magic-eraser")
async def magic_eraser(
    target_image: UploadFile = File(..., description="Target image (JPG or PNG)"),
    mask_image: UploadFile = File(..., description="Mask image (JPG or PNG)"),
):
    """
    Endpoint to process three images and return modified images as raw data.
    """

    # Load images into memory
    mask_image_base64 = await convert_image_to_base64(mask_image)
    target_image_base64 = await convert_image_to_base64(target_image)
    
    result_image = comfyuiservice.get_magic_eraser_image(image_base64=target_image_base64, mask_image_base64=mask_image_base64)
    image_stream = io.BytesIO(result_image)
    return StreamingResponse(image_stream, media_type="image/png")

@app.post("/sdxl-pulid-sticker")
async def sdxl_pulid_sticker(
    reference_image: UploadFile = File(..., description="Mask image (JPG or PNG)"),
    user_prompt: str = Form(...),
):
    """
    Endpoint to process three images and return modified images as raw data.
    """

    # Load images into memory
    reference_image_base64 = await convert_image_to_base64(reference_image)
    
    result_image = comfyuiservice.get_sticker_with_reference_sdxl_pulid(reference_image_base64=reference_image_base64, prompt=user_prompt)
    image_stream = io.BytesIO(result_image)
    return StreamingResponse(image_stream, media_type="image/png")

@app.get("/hello")
def read_hello():
    return {"message": "Hello World!"}



