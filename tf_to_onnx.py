import tf2onnx
from tensorflow import keras

model = keras.models.load_model("pretrained/UNET_full_road_scratch.019.h5", compile= False)

keras.models.save_model(model, "my_model")
print(model.summary())


# python -m tf2onnx.convert --saved-model "my_model" --output "pretrained/UNET_full_road_scratch.019.onnx"