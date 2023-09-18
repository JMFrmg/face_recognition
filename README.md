# Application de reconnaissance et de réidentification faciale
Ce projet a été codé dans le cadre de la formation Simplon Développeur IA en partenariat avec Microsoft.
L'objectif était de coder une application avec une interface web avec la possibilité pour l'utilisateur d'uploader une image. Un modèle de Machine Learning identifie les visages présents sur l'image, les informations sont retournées au frontend et affichées. L'utilisateur peut alors visualiser les visages présents sur l'image, vérifier si certains sont déjà connus, et modifier les méta-données associées à chaque visage identifié.
Nous avions pour consigne de ne pas prendre en compte les contraintes légales notamment liées à la protection des données personnelles.
## Lancer l'application
L'application utilise Docker et Docker Compose.
Dans le terminal :
```sh
git clone https://github.com/JMFrmg/face_recognition.git
```
```sh
docker compose up -d
```
## Choix technologiques
 - Bootstrap (frontend)
 - Python Django (backend)
 - face_recognition (reconnaissance faciale)
 - Postgresql (BDD)
