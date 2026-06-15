# CloudSync Image Recognition Part 2

## Goal
This part adds a known actor image recognition feature to the CloudSync demo. The goal is to prepare a local image recognition workflow using 10 actor classes.

## Advisor Requirements
1. Set up the image recognition workflow locally.
2. Curate a known actor photo dataset.
3. Use 10 actor classes.
4. Collect 100+ images per actor.
5. Include different ages, poses, lighting, and photos with multiple people.
6. Annotate images using COCO JSON format.
7. Train the model using RF-DETR or Roboflow.
8. Test the trained model on a separate image subset.
9. Add a second Streamlit tab for photo uploads and image prediction results.

## Dataset Target
10 actors x 100+ images per actor = at least 1,000 actor photos total.

## Current Status
The image recognition branch has been created. The actor list file has been created with 10 classes. The folder structure is being prepared for dataset collection, annotation, model training, testing, and Streamlit integration.

## Safety and Scope
This project is for educational demo purposes using a controlled dataset of known public actor classes. It should not be used for private surveillance or unknown-person identification.
