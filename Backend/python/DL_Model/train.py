import cv2
import numpy as np
from rembg import remove
from PIL import Image
import os
import random
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import VGG16
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Layer

#Set paths

DATASET_PATH = os.path.join(os.getcwd(), "Backend\python\DL_Model\Dataset")
MODEL_PATH = os.path.join(os.getcwd(), "Backend\python\DL_Model\Models\signature_siamese_model.keras")


#Image Preprocessing

def preprocess(path_or_file, IMG_SIZE = 224):

    input_image = Image.open(path_or_file)
    output_image = remove(input_image)

    output_image = output_image.convert("RGB")

    img = np.array(output_image)

    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))

    img = img / 255.0

    return img


#Setup Dataset Array

def create_pairs(dataset_path):

    persons = os.listdir(dataset_path)

    img1 = []
    img2 = []
    labels = []

    for person in persons:

        person_path = os.path.join(dataset_path,person)
        images = os.listdir(person_path)

        # positive pairs
        for i in range(len(images)-1):

            img_a = preprocess(os.path.join(person_path,images[i]))
            img_b = preprocess(os.path.join(person_path,images[i+1]))

            img1.append(img_a)
            img2.append(img_b)
            labels.append(1)

        # negative pairs
        other_person = random.choice(persons)

        if other_person != person:

            other_path = os.path.join(dataset_path,other_person)
            other_images = os.listdir(other_path)

            img_a = preprocess(os.path.join(person_path,images[0]))
            img_b = preprocess(os.path.join(other_path,other_images[0]))

            img1.append(img_a)
            img2.append(img_b)
            labels.append(0)

    return np.array(img1),np.array(img2),np.array(labels)


#Build a Model

class L1DistanceLayer(Layer):
    def call(self, inputs):
        x, y = inputs
        return tf.abs(x - y)
    
    
def build_siamese():

    base = VGG16(
        weights="imagenet",
        include_top=False,
        input_shape=(224,224,3)
    )

    for layer in base.layers:
        layer.trainable = False

    x = base.output
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(512,activation="relu")(x)
    x = layers.Dense(128,activation="relu")(x)

    feature_extractor = Model(base.input,x)

    inputA = tf.keras.Input(shape=(224,224,3))
    inputB = tf.keras.Input(shape=(224,224,3))

    featA = feature_extractor(inputA)
    featB = feature_extractor(inputB)

    distance = L1DistanceLayer()([featA, featB])

    output = layers.Dense(1,activation="sigmoid")(distance)

    model = Model([inputA,inputB],output)

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    return model


#Model Train

def Model_train():
    
    img1,img2,labels = create_pairs(DATASET_PATH)

    X1_train,X1_test,X2_train,X2_test,y_train,y_test = train_test_split(
        img1,img2,labels,test_size=0.2
    )

    model = build_siamese()

    model.fit(
        [X1_train,X2_train],
        y_train,
        validation_data=([X1_test,X2_test],y_test),
        epochs=10,
        batch_size=16
    )
    
    model.save(MODEL_PATH)
    
    return True
    
    

def get_verify(customerID, uploaded_img):
    
    MODEL = load_model(
        MODEL_PATH,
        custom_objects={"L1DistanceLayer": L1DistanceLayer}
    )
    
    original_img_path = os.path.join(DATASET_PATH, customerID)
    images = os.listdir(original_img_path)
    
    score_list =[]
    for img in images:
        img_path = os.path.join(original_img_path, img)
    
        img1 = preprocess(img_path)
        img2 = preprocess(uploaded_img)

        img1 = np.expand_dims(img1,axis=0)
        img2 = np.expand_dims(img2,axis=0)

        score = MODEL.predict([img1,img2])[0][0]
        score_list.append(score)
        
    max_score = max(score_list)
    print("Similarity Max Score:",max_score)
        
    if max_score > 0.5:
        status = True
    else:
        status = False
        
    return max_score, status
            

        
def add_new_data(customerID, uploaded_imgs):
    
    new_img_path = os.path.join(DATASET_PATH, customerID)
    os.makedirs(new_img_path, exist_ok=True)
    
    images = os.listdir(new_img_path)
    saved_files = []
    for i, uploaded_img in enumerate(uploaded_imgs):
    
        img_name = f"{customerID}-{len(images)+i+1}.png"
        save_path = os.path.join(new_img_path, img_name)
    
        with open(save_path, "wb") as f:
            f.write(uploaded_img.getbuffer())
        
        saved_files.append(img_name)
        
    return saved_files