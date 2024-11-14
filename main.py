from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import comfyuiservice

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; restrict to specific domains as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-image")
async def get_image(input: str = Query(None)):
    image = comfyuiservice.fetch_image_from_comfy(input)
    image_stream = io.BytesIO(image)
    return StreamingResponse(image_stream, media_type="image/png")

@app.get("/hello")
def read_hello():
    return {"message": "Hello World!"}