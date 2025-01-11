import websocket
import uuid
import json
import os
import urllib.request
import urllib.parse

save_image_websocket = 'SaveImageWebsocket'
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

# uses the flux-redux-cloth-swap workflow to inpaint image uploaded (changed to base 64) to target image (either model or shirt)
def get_inpaint_image_on_target_json(inpaint_image_base64, target_image_base64, mask_image_base64):
    TARGETIMAGEID = "405"
    INPAINTIMAGEID = "404"
    MASKIMAGEID = "403"

    file_path = "data.json"

    workflow_folder = "workflows-api"
    file_name = "flux-redux-logo-final-mango-api.json"

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    print(f"file path: {file_path}")

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[TARGETIMAGEID]["inputs"]["image"] = target_image_base64
        prompt_json[INPAINTIMAGEID]["inputs"]["image"] = inpaint_image_base64
        prompt_json[MASKIMAGEID]["inputs"]["mask"] = mask_image_base64
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

def fetch_image_from_comfy(input):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, get_cloth_with_prompt(input))
    ws.close()
    return images

def swap_clothes_on_model(cloth_base_64, model_base_64, mask_base_64):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, get_inpaint_image_on_target_json(inpaint_image_base64=cloth_base_64, target_image_base64=model_base_64, mask_image_base64=mask_base_64))

    print(images)
    ws.close()
    return images

def get_target_image_with_logo(target_image_base64, logo_image_base64, mask_image_base64):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, get_inpaint_image_on_target_json(inpaint_image_base64=logo_image_base64, target_image_base64=target_image_base64, mask_image_base64=mask_image_base64))

    print(images)
    ws.close()
    return images
