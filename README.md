# Digital_Race_2023: https://digitalrace.feexp.space/
Source code for self driving car in VIA simulator, which is contributed by FutuDrive - my team in Digital Race 2023

### Installation

- conda create -n futudrive python==3.10.12
- pip install -r requirements.txt
- pip install torch==2.0.0+cu118 torchvision==0.15.1+cu118 torchaudio==2.0.1 --index-url https://download.pytorch.org/whl/cu118 

---

### Module

- drive.py: main file run this to make the car run in simulator environment
- lane_line_detection.py: segments roads, controls the car.
- traffic_sign_detection.py: detect signs, objects and calculate distance
- tf_to_onnx.py: convert h5 file to onnx file

### Run simulation

- For the copyright reason, we cannot share the simulator we use in competitions, but you guys can find the similar in VIA automous: https://via-sim.makerviet.org/
- python run drive.py

### Model

- The model to segment the road (UNet) and the model to detect signs (YOLO) are all included in pretrained folder
- To change type of weights of UNet model, modify the config_param.json by change "model_onnx_path":"link model"
- To change type of weights of YOLO model, modify the config_param.json by change "model_detect_sign_path": "link model"

### Fuzzy Logic

- The fuzzy logic is contained in cds_fuzzy_logic 
- We use fuzzy logic to control throttle and steering of the car combining with other technique.

### Dataset
- https://www.kaggle.com/datasets/ducido/lane-segmentation
- https://www.kaggle.com/datasets/ducido/object-detection


 
