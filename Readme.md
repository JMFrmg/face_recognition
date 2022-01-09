# Projet de réidentification faciale via une interface
Ce projet a été réalisé dans le cadre de la formation Développeur IA dispensée par Simplon.
L'objectif du projet est de réaliser un POC de réidentification faciale sur des images avec une interface web.
## Installation (bash)
En console, se positionner à la racine du projet.
Créer un environnement virtuel.
```sh
python -m venv face_recognition_env
```
Charger l'environnement virtuel.
```sh
source face_recognition_env/bin/activate
```
Installer les dépendances.
```sh
pip install -r requirements.txt
```
Migrer la base de données.
```sh
python manage.py makemigrations
python manage.py migrate
```
Lancer le serveur de développement de Django.
```sh
python manage.py runserver
```
## Fonctionnement de l'application
L'URL de la page d'accueil de l'interface est la racine.
L'utilisateur peut sélectionner une photo sur son disque.
La photo est affichée et envoyée au backend de l'application.
Celui-ci utilise le module face_recognition pour détecter les visages. Chaque fois qu'un visage est identifié, l'application recherche dans la base de données si celui-ci est déjà présent. Dans le cas contraire une nouvelle entrée est créée en base.
Le backend retourne les boundings boxes de chaque visage ainsi que les informations du client correspondant (nom, prénom, commentaire et status).
Les données sont réceptionnées par le frontend en json. Les rectangles associés à chaque visage sont tracés sur l'image. Les informations sont affichées sous l'image. L'utilisateur peut modifier les informations relatives à chaque personne identifiée. 
## Tests de performance du modèle
### Prérequis
Copier les dossiers "part2_labels" et "part2_photos" dans le dossier photos_test situé à la racine du projet.
Il est aussi possible de modifier le path vers les dossiers des photos et des labels directement dans le fichier perfs_tests.py (lignes 25 et 27).
Dans le termial et à la racine du projet :
Charger l'environnement virtuel.
```sh
source face_recognition_env/bin/activate
```
Lancer le script.
```sh
python perfs_tests.py
```
Le script charge chaque image, l'envoie au backend et compare les prédictions avec les boundings boxes des fichiers labels. La moyenne, l'écart-type et les quartiles de l'accuracy sont affichés en console, ainsi que le nombre de visages identifiés dans les images.
Il est possible d'interrompre les tests avec ctrl+c. Le rapport de performance des images traitées sera tout de même affiché en console.
