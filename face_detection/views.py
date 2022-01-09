from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

import logging
import io, base64
import pickle
import json
import cv2
import numpy as np
from PIL import Image
import face_recognition
from datetime import datetime


from .models import Client, Face

#logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#logging handler
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def loadBase64Img(encoded_data):
    """
    Transform base64 image to numpy array
    Args:
        encoded_data (str) : base64 encoded image
    Returns:
        decoded image (numpy.array)
    """
    nparr = np.fromstring(base64.b64decode(encoded_data), 
                            np.uint8)
    img = cv2.imdecode(nparr, 
            cv2.IMREAD_COLOR)
    print(type(img))
    return img

def preprocess_image(base64_img):
    if not isinstance(base64_img, str):
        logger.error(f"Base64 encoded image must be string, not {type(base64_img)}.")
        logger.debug(f"Image data recieved : {base64_img}.")
        logger.debug(f"Image data type recieved : {type(base64_img)}.")
        raise TypeError
    logger.info(f"Start image preprocessing.")
    try:
        base64_prefix, base64_img_data = base64_img.split(',')
    except:
        base64_prefix, base64_img_data = "", base64_img
    img_arr = loadBase64Img(base64_img_data)
    rgb = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
    return (rgb, img_arr)

def crop_face_image(img_arr, face_location):
    top, right, bottom, left = face_location
    face_image = img_arr[top:bottom, left:right]
    return face_image

def encode_face(face_image):
    """
    Return the model face representation.
    Args:
        face_image (numpy.array) : face image
    Returns:
        encoded face (list) : model representation of the face
    """
    retry = 0
    while retry < 3:
        face_encoded = face_recognition.face_encodings(face_image)
        if not face_encoded:
            retry += 1
        else:
            break
    return face_encoded

def regiser_new_client(face_encoded):
    """
    Register new client and his encoded face in db.
    Args:
        face_encoded (list) : model representation of the face
    Returns:
        New client
    """
    new_client = Client(last_view=datetime.now(),
                                status=True)
    new_face = Face(encoded=np.array(face_encoded).tobytes(),
                    client=new_client)
    new_client.save()
    new_face.save()
    return new_client


def index(request):
    return render(request, 'face_detection/index.html')


@csrf_exempt
@xframe_options_exempt
def update_face_data(request):
    face_infos = dict(request.POST)
    logger.info(f"Update data request for client {str(face_infos['id'])}.")
    keys_to_ignore = ("id", "index", "last_view")
    #Only keep updatable data
    updated_data = {k:v for k,v in face_infos.items() \
                    if k not in keys_to_ignore}
    #Update client data
    for k,v in updated_data.items():
        Client.objects.filter(faces=int(face_infos["id"][0])).update(**{k:v[0]})
    logger.info(f"Update data request : success.")
    return JsonResponse({})


@csrf_exempt
def identify_faces(request):
    logger.info("Start processing new prediction request.")
    data = json.loads(request.body.decode("utf-8"))
    try:
        base64_img = data["image"]
    except KeyError:
        #Wrong data structure has been sent
        logger.error("No 'image' key in Json data sent by client.")
        return HttpResponse(status=500)
    except Exception as e:
        #Catch exception to prevent app to crash
        logger.error(f"{str(e)}.")
        return HttpResponse(status=500)
    try:
        rgb, img_arr = preprocess_image(base64_img)
    except TypeError:
        #Image recieved is not base64 encoded
        logger.error("Image data recieved is not base64 encoded.")
        return HttpResponse(status=500)
    except Exception as e:
        #Catch exception to prevent app to crash
        logger.error(f"Unknowed error occured : {str(e)}.")
        return HttpResponse(status=500)
    #Faces boxes detection
    face_boxes = face_recognition.face_locations(rgb, 
                                        model="hog")
    logger.info(f"Number of faces identified in the image : \
                {len(face_boxes)}.")
    logger.debug(f"Face boxes identified : {face_boxes}.")
    #Get previous identified faces
    known_faces = Face.objects.all()
    known_faces_encoded = [np.frombuffer(f.encoded, 
            np.float64).tolist() \
                for f in known_faces]
    logger.debug(f"Number of known faces in db : \
                    {len(known_faces_encoded)}.")
    #Final variable to return in json format
    data_to_return = {"faces": []}
    #Loop over identified faces
    for i, face_location in enumerate(face_boxes):
        face_data = {"boxes": face_location}
        logger.debug(f"Identified face : {str(i)}.")
        #Crop face from image sent by client
        face_image = crop_face_image(img_arr, 
                                face_location)
        #Face image encoding
        face_encoded = encode_face(face_image)
        if not face_encoded:
            #Model can't encode the face
            #Mostly append when face is profile
            logger.info(f"Model can't encode the face.")
            face_data["infos"] = {"index": len(data_to_return["faces"])+1}
            data_to_return["faces"].append(face_data)
            #go to next face
            continue
        #Face has been correctly encoded by model
        logger.info(f"Face has been encoded by model.")
        logger.debug(f"Face encoded data : {face_encoded}")
        #Compare face with all known faces in db
        if known_faces_encoded:
            distances = face_recognition.face_distance(known_faces_encoded, 
                                                        face_encoded[0]).tolist()
            similarities = [1 - d for d in distances]
            similarity = max(similarities)
            face = known_faces[similarities.index(similarity)]
        else:
            similarity = 0
        if similarity < 0.5:
            new_client = regiser_new_client(face_encoded)
            face_data["infos"] = new_client.get_data()
        else:
            face_data["infos"] = face.client.get_data()
        face_data["infos"]["index"] = str(len(data_to_return["faces"])+1)
        data_to_return["faces"].append(face_data)
    return JsonResponse(data_to_return)


@csrf_exempt
def model_accuracy_test(request):
    logger.info("Start processing new prediction request.")
    data = json.loads(request.body.decode("utf-8"))
    model = data["model"]#hog or cnn
    try:
        base64_img = data["image"]
    except KeyError:
        #Wrong data structure has been sent
        logger.error("No 'image' key in Json data sent by client.")
        return HttpResponse(status=500)
    except Exception as e:
        #Catch exception to prevent app to crash
        logger.error(f"{str(e)}.")
        return HttpResponse(status=500)
    try:
        rgb, img_arr = preprocess_image(base64_img)
    except TypeError:
        #Image recieved is not base64 encoded
        logger.error("Image data recieved is not base64 encoded.")
        return HttpResponse(status=500)
    except Exception as e:
        #Catch exception to prevent app to crash
        logger.error(f"Unknowed error occured : {str(e)}.")
        return HttpResponse(status=500)
    #Faces boxes detection
    face_boxes = face_recognition.face_locations(rgb, 
                                        model=model)
    data_to_return = {"faces": []}
    for i, face_location in enumerate(face_boxes):
        face_data = {"boxes": face_location}
        data_to_return["faces"].append(face_data)
    return JsonResponse(data_to_return)