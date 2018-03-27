import tensorflow as tf
from os import path
import numpy as np
from scipy import misc
from styx_msgs.msg import TrafficLight
import cv2
import rospy


import tensorflow as tf

class CarlaModel(object):
    def __init__(self, model_checkpoint):
        self.sess = None
        self.checkpoint = model_checkpoint
        self.prob_thr = 0.90
        self.TRAFFIC_LIGHT_CLASS = 10
        self.image_no = 10000
        tf.reset_default_graph()
    
    def predict(self, img):
        if self.sess == None:
            gd = tf.GraphDef()
            gd.ParseFromString(tf.gfile.GFile(self.checkpoint, "rb").read())
            tf.import_graph_def(gd, name="object_detection_api")
            self.sess = tf.Session()
        
            g = tf.get_default_graph()
            self.image = g.get_tensor_by_name("object_detection_api/image_tensor:0")
            self.boxes = g.get_tensor_by_name("object_detection_api/detection_boxes:0")
            self.scores = g.get_tensor_by_name("object_detection_api/detection_scores:0")
            self.classes = g.get_tensor_by_name("object_detection_api/detection_classes:0")
        
        img_h, img_w = img.shape[:2]

        self.image_no = self.image_no+1
        cv2.imwrite("full_"+str(self.image_no)+".png", img)
        
        for h0 in [img_h//3, (img_h//3)-150]:
            for w0 in [0, img_w//3, img_w*2//3]:
                grid = img[h0:h0+img_h//3+50, w0:w0+img_w//3, :] # grid
                pred_boxes, pred_scores, pred_classes = self.sess.run([self.boxes, self.scores, self.classes],
                                                             feed_dict={self.image: np.expand_dims(grid, axis=0)})
                pred_boxes = pred_boxes.squeeze()
                pred_scores = pred_scores.squeeze() #  descreding order
                pred_classes = pred_classes.squeeze()

                traffic_light = None
                h, w = grid.shape[:2]
                cv2.imwrite("grid_"+str(self.image_no)+"_"+str(h0)+"_"+str(w0)+".png",grid)
                rospy.loginfo("w,h is %s,%s",h0,w0)

                for i in range(pred_boxes.shape[0]):
                    box = pred_boxes[i]
                    score = pred_scores[i]
                    if score < self.prob_thr: continue
                    if pred_classes[i] != self.TRAFFIC_LIGHT_CLASS: continue
                    x0, y0 = box[1] * w, box[0] * h
                    x1, y1 = box[3] * w, box[2] * h
                    x0, y0, x1, y1 = map(int, [x0, y0, x1, y1])
                    x_diff = x1 - x0
                    y_diff = y1 - y0
                    xy_ratio = x_diff/float(y_diff)
                    rospy.loginfo("image_no is %s", self.image_no)
                    rospy.loginfo("x,y ratio is %s",xy_ratio)
                    rospy.loginfo("score is %s",score)
                    if xy_ratio > 0.48: continue            
                    area = np.abs((x1-x0) * (y1-y0)) / float(w*h)
                    rospy.loginfo("area is %s",area)
                    if area <= 0.001: continue
                    traffic_light = grid[y0:y1, x0:x1]
                    rospy.loginfo("traffic light given")
                    # select first -most confidence
                    if traffic_light is not None: break
            if traffic_light is not None: break


        if traffic_light is None:
            pass
        else:
            rospy.loginfo("w,h is %s,%s",h0,w0)
            rospy.loginfo("x,y ratio is %s",xy_ratio)
            rospy.loginfo("score is %s",score)
            cv2.imwrite("light_"+str(self.image_no)+".png",traffic_light)
            #cv2.imwrite("full_"+str(self.image_no)+".png", img)
            #cv2.imwrite("grid_"+str(self.image_no)+".png",grid)
            #self.image_no = self.image_no+1
            brightness = cv2.cvtColor(traffic_light, cv2.COLOR_RGB2HSV)[:,:,-1] 
            hs, ws = np.where(brightness >= (brightness.max()-30))
            hs_mean = hs.mean()
            tl_h = traffic_light.shape[0]
            if hs_mean / tl_h < 0.4:
                rospy.loginfo("image"+str(self.image_no-1)+" is RED")
                return TrafficLight.RED
            elif hs_mean / tl_h >= 0.55:
                rospy.loginfo("image"+str(self.image_no-1)+" is GREEN")
                return TrafficLight.GREEN
            else:
                rospy.loginfo("image"+str(self.image_no-1)+" is YELLOW")
                return TrafficLight.YELLOW
        return TrafficLight.UNKNOWN
