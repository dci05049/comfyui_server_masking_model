import websocket
import uuid
import json
import os
import urllib.request
import urllib.parse
import base64
from io import BytesIO
from PIL import Image

save_image_websocket = 'SaveImageWebsocket'
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

# for magic eranser
def get_magic_eraser_json(image_base64, mask_image_base64):
    IMAGEID = "85"
    MASKID = "99"

    workflow_folder = "workflows-api"
    file_name = "magic-eraser-api.json"


    with open("image.txt", "w") as file:
        file.write(str(image_base64))  # Convert result to string if it's not already

    with open("mask.txt", "w") as file:
        file.write(str(mask_image_base64))  # Convert result to string if it's not already

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[IMAGEID]["inputs"]["image"] = image_base64
        prompt_json[MASKID]["inputs"]["mask"] = mask_image_base64
        return prompt_json
    

# for magic eranser
def get_sdxl_pulid_sticker_json(reference_image_base64, prompt):
    REFERENCEIMAGEID = "528"
    PROMPTID = "313"

    workflow_folder = "workflows-api"
    file_name = "sdxl-pulid-sticker-api.json"

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[PROMPTID]["inputs"]["prompt_1"] = prompt
        return prompt_json

# for inpainting logo on target image
def get_inpaint_image_on_target_json(inpaint_image_base64, target_image_base64, mask_image_base64):
    TARGETIMAGEID = "405"
    INPAINTIMAGEID = "404"
    MASKIMAGEID = "403"

    workflow_folder = "workflows-api"
    file_name = "flux-redux-logo-final-mango-guff-api.json"

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[TARGETIMAGEID]["inputs"]["image"] = target_image_base64
        prompt_json[INPAINTIMAGEID]["inputs"]["image"] = inpaint_image_base64
        prompt_json[MASKIMAGEID]["inputs"]["mask"] = mask_image_base64
        return prompt_json
    
# swap cloth on model image with mask
def swap_cloth_model_iamge_json(model_image_base_64, cloth_image_base_64, mask_image_base_64):
    CLOTHIMAGEID = "410"
    MODELIMAGEID = "412"
    MASKIMAGEID = "393"

    workflow_folder = "workflows-api"
    file_name = "flux-redux-cloth-swap-api-guff-api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[CLOTHIMAGEID]["inputs"]["image"] = cloth_image_base_64
        prompt_json[MODELIMAGEID]["inputs"]["image"] = model_image_base_64
        prompt_json[MASKIMAGEID]["inputs"]["mask"] = mask_image_base_64
        return prompt_json

# flux pulid
def flux_pulid_json(reference_image_base64, prompt):
    REFERENCEIMAGEID = "66"
    PROMPTID = "6"

    workflow_folder = "workflows-api"
    file_name = "flux-pulid-api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[PROMPTID]["inputs"]["text"] = prompt
        return prompt_json
    
# outpainting sdxl
def outpainting_sdxl_json(reference_image_base64, left, right, top, bottom):
    REFERENCEIMAGEID = "361"
    NEWIMAGESIZENODEID = "340"
    IMAGEBLENDADVANCENODEID = "355"

    image_data = base64.b64decode(reference_image_base64)
    
    # Open the image using Pillow
    image = Image.open(BytesIO(image_data))
    
    # Get width and height
    width, height = image.size

    # calculate x and y pivot


    new_width = width + left + right
    new_height = height + top + bottom

    print (new_width)
    print (new_height)
    center_point_width = width / 2
    center_point_height = height / 2


    x_percent = (center_point_width + left) / new_width * 100
    y_percent = (center_point_height + top) / new_height  * 100

    workflow_folder = "workflows-api"
    file_name = "sdxl-outpainting-api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[NEWIMAGESIZENODEID]["inputs"]["width"] = new_width
        prompt_json[NEWIMAGESIZENODEID]["inputs"]["height"] = new_height
        prompt_json[IMAGEBLENDADVANCENODEID]["inputs"]["x_percent"] = x_percent
        prompt_json[IMAGEBLENDADVANCENODEID]["inputs"]["y_percent"] = y_percent
        return prompt_json

# uses the flux-guff-text-api.json workflow to generate image with prompt
def get_cloth_with_prompt(prompt):
    TEXTID = "6"

    file_path = "data.json"

    workflow_folder = "workflows-api"
    file_name = "flux-guff-text-api.json"

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[TEXTID]["inputs"]["text"] = prompt
        return prompt_json


def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())



def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_image = None
    current_node = ""
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    if data['node'] is None:
                        break #Execution is done
                    else:
                        node_number = data['node']
                        current_node = prompt[node_number]["class_type"]
        else:
            if current_node == save_image_websocket:
                output_image = out[8:]

    return output_image

# Gets the new image with prompt
def fetch_image_with_prompt(input):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, get_cloth_with_prompt(input))
    ws.close()
    return images

# Gets the new image with model with new clothes
def get_model_image_with_cloth(cloth_base_64, model_base_64, mask_base_64):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, swap_cloth_model_iamge_json(cloth_image_base_64=cloth_base_64, model_image_base_64=model_base_64, mask_image_base_64=mask_base_64))

    ws.close()
    return images

# Gets new image with prompt and reference image using Pulid
def get_image_with_reference_pulid(reference_image_base64, prompt):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, flux_pulid_json(reference_image_base64=reference_image_base64, prompt=prompt))

    ws.close()
    return images

# Gets new image with prompt and reference image using Pulid
def get_sticker_with_reference_sdxl_pulid(reference_image_base64, prompt):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, get_sdxl_pulid_sticker_json(reference_image_base64=reference_image_base64, prompt=prompt))

    ws.close()
    return images

# Gets outpainting image with increaes in each sides 
def get_image_with_outpainting_sdxl(reference_image_base64, left, right, top, bottom):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, outpainting_sdxl_json(reference_image_base64=reference_image_base64, left=left, right=right, top=top, bottom=bottom))

    ws.close()
    return images

# Gets new image with object removed, input target image and mask where mask area is where object is removed
def get_magic_eraser_image(image_base64, mask_image_base64):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, get_magic_eraser_json(image_base64=image_base64, mask_image_base64=mask_image_base64))

    ws.close()
    return images

# Gets new image with logo printed on clothes
def get_target_image_with_logo(target_image_base64, logo_image_base64, mask_image_base64):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, get_inpaint_image_on_target_json(inpaint_image_base64=logo_image_base64, target_image_base64=target_image_base64, mask_image_base64=mask_image_base64))

    ws.close()
    return images
