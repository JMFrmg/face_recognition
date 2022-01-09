"""
Script de mesure de la performance des modèles.
Pour chaque photo, une requête est envoyée au backend de l'application.
Les visages identifiés sont comparés avec les labels.
L'accuracy est mesurée à l'aide de la méthode "intersection over union".
L'accuracy est comprise entre 0 et 1. 1 est le maximum.
A la fin du script, la moyenne, l'écart-type et les quartiles de l'accuracy sont affichés.
"""

import os
import sys
import glob
import base64
import requests
import pandas as pd
from pprint import pprint

from utils import intersection_over_union

models = ("hog", "cnn")
models_to_ignore = ("cnn")
models = [m for m in models \
		if m not in models_to_ignore]
#Path to images directory
images_dir = "photos_test/part2_photos/part2"
#Path to labels directory
labels_dir = "photos_test/part2_labels"
face_detection_url = "http://127.0.0.1:8000/model_accuracy_test/"

#Final results DataFrame
df_results = pd.DataFrame(columns=["image", "model", "detected_faces", "accuracy"])

#List of all labels files names
label_files = glob.glob(labels_dir + "/*.csv")

#Load and Concat all csv labels files in a unique DataFrame
li = []
for filename in label_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

df_labels = pd.concat(li, axis=0, ignore_index=True)

#Dict which register number of faces detected in a picture 
face_detected = {"No face": 0, "One face": 0, "Two faces": 0, "More": 0}

for label in df_labels.iterrows():
	#Loop over each labels row
	try:
		img_name = label[1].array[0]
		box_label = list(label[1].array[1:])
		img_full_name = img_name + ".jpg"
		img_path = os.path.join(images_dir,img_full_name)
		#Load picture from disk
		with open(img_path, "rb") as img_file:
			#base6' encoding
			base64_img = base64.b64encode(img_file.read())
		if base64_img:
			for model in models:
				accuracy = 0
				data = {"image": base64_img.decode("utf-8"), 
											"model": model}
				#Post request to backend
				resp = requests.post(face_detection_url, 
											json=data)
				data = resp.json()
				#Number of detected faces by model
				detected_faces = len(data["faces"])
				if detected_faces == 1:
					face_detected["One face"] += 1
					predicted_box = data["faces"][0]["boxes"]
					last = predicted_box.pop()
					predicted_box.insert(0, last)
					#Compare prediction and label to compute accuracy
					accuracy = intersection_over_union(box_label, 
													predicted_box)
					#Append results to DataFrame
					df_results = df_results.append({"image": img_name,
													"model": model, 
													"detected_faces": detected_faces, 
													"accuracy": accuracy},
													ignore_index=True)
				elif not detected_faces:
					face_detected["No face"] += 1
				elif detected_faces == 2:
					face_detected["Two faces"] += 1
				else:
					face_detected["More"] += 1
			print(f"Model: {model}, Accuracy: {accuracy}, Detected faces : {str(detected_faces)}")
	except KeyboardInterrupt:
		print("You pressed Ctrl + c.")
		print("Results :")
		break

print("\n\n")
pprint(df_results.describe())
print("\n")
print("Number of faces detected :")
[print(f"{k} : {v}") for k,v in face_detected.items()]
sys.exit(0)
