import numpy as np
import cv2
import tensorflow as tf
from keras import layers, models, optimizers

from yolo_ai.custom_layers import yolov4_neck, yolov4_head, nms
from yolo_ai.utils import load_weights, get_detection_data, draw_bbox
from yolo_ai.config import yolo_config
from yolo_ai.loss import yolo_loss


class Yolov4(object):
    def __init__(self,
                 weight_path=None,
                 class_name_path='coco_classes.txt',
                 config=yolo_config,
                 ):
        assert config['img_size'][0] == config['img_size'][1], 'not support yet'
        assert config['img_size'][0] % config['strides'][-1] == 0, 'must be a multiple of last stride'
        self.class_names = [line.strip() for line in open(class_name_path).readlines()]
        self.img_size = yolo_config['img_size']
        self.num_classes = len(self.class_names)
        self.weight_path = weight_path
        self.anchors = np.array(yolo_config['anchors']).reshape((3, 3, 2))
        self.xyscale = yolo_config['xyscale']
        self.strides = yolo_config['strides']
        self.output_sizes = [self.img_size[0] // s for s in self.strides]
        self.class_color = {name: list(np.random.random(size=3)*255) for name in self.class_names}
        # Training
        self.max_boxes = yolo_config['max_boxes']
        self.iou_loss_thresh = yolo_config['iou_loss_thresh']
        self.config = yolo_config
        assert self.num_classes > 0, 'no classes detected!'

        tf.keras.backend.clear_session()
        if yolo_config['num_gpu'] > 1:
            mirrored_strategy = tf.distribute.MirroredStrategy()
            with mirrored_strategy.scope():
                self.build_model(load_pretrained=True if self.weight_path else False)
        else:
            self.build_model(load_pretrained=True if self.weight_path else False)

    def build_model(self, load_pretrained=True):
        # core yolo model
        input_layer = layers.Input(self.img_size)
        yolov4_output = yolov4_neck(input_layer, self.num_classes)
        self.yolo_model = models.Model(input_layer, yolov4_output)

        # Build training model
        y_true = [
            layers.Input(name='input_2', shape=(52, 52, 3, (self.num_classes + 5))),  # label small boxes
            layers.Input(name='input_3', shape=(26, 26, 3, (self.num_classes + 5))),  # label medium boxes
            layers.Input(name='input_4', shape=(13, 13, 3, (self.num_classes + 5))),  # label large boxes
            layers.Input(name='input_5', shape=(self.max_boxes, 4)),  # true bboxes
        ]
        loss_list = tf.keras.layers.Lambda(yolo_loss, name='yolo_loss',
                                           arguments={'num_classes': self.num_classes,
                                                      'iou_loss_thresh': self.iou_loss_thresh,
                                                      'anchors': self.anchors})([*self.yolo_model.output, *y_true])
        self.training_model = models.Model([self.yolo_model.input, *y_true], loss_list)

        # Build inference model
        yolov4_output = yolov4_head(yolov4_output, self.num_classes, self.anchors, self.xyscale)
        # output: [boxes, scores, classes, valid_detections]
        self.inference_model = models.Model(input_layer,
                                            nms(yolov4_output, self.img_size, self.num_classes,
                                                iou_threshold=self.config['iou_threshold'],
                                                score_threshold=self.config['score_threshold']))

        if load_pretrained and self.weight_path and self.weight_path.endswith('.weights'):
            if self.weight_path.endswith('.weights'):
                load_weights(self.yolo_model, self.weight_path)
                print(f'load from {self.weight_path}')
            elif self.weight_path.endswith('.h5'):
                self.training_model.load_weights(self.weight_path)
                print(f'load from {self.weight_path}')

        self.training_model.compile(optimizer=optimizers.Adam(learning_rate=1e-4),
                                    loss={'yolo_loss': lambda y_true, y_pred: y_pred})

    def save_model(self, path):
        self.yolo_model.save(path)

    def preprocess_img(self, img):
        img = cv2.resize(img, self.img_size[:2])
        img = img / 255.
        return img

    # raw_img: RGB
    def predict_img(self, raw_img, random_color=True, plot_img=True, figsize=(10, 10), show_text=True, return_output=False):
        #print('img shape: ', raw_img.shape)
        img = self.preprocess_img(raw_img)
        imgs = np.expand_dims(img, axis=0)
        pred_output = self.inference_model.predict(imgs)
        detections = get_detection_data(
            img=raw_img,
            model_outputs=pred_output,
            class_names=self.class_names
        )
        # print(detections)
        return detections
        #output_img = draw_bbox(raw_img, detections, cmap=self.class_color, random_color=random_color, figsize=figsize,
        #          show_text=show_text)
        #self.export_gt()
        #if return_output:
        #    return output_img, detections
        #else:
        #    return detections

    def predict(self, img_path, random_color=True, plot_img=True, figsize=(10, 10), show_text=True):
        raw_img = cv2.imread(img_path)[:, :, ::-1]
        return self.predict_img(raw_img, random_color, plot_img, figsize, show_text)
