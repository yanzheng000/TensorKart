#!/usr/bin/env python

import tensorflow as tf
import time
from utils import take_screenshot, prepare_image
from utils import FakeController, XboxController

IMG_W = 320
IMG_H = 240

IN_SHAPE = IMG_W*IMG_H
OUT_SHAPE = 5


# Start session
sess = tf.InteractiveSession()


# Placeholders
x = tf.placeholder(tf.float32, shape=[None, IN_SHAPE])
y_ = tf.placeholder(tf.float32, shape=[None, OUT_SHAPE])


# Weight Initialization
def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)


# Convolution and Pooling
def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_6x6(x):
  return tf.nn.max_pool(x, ksize=[1, 6, 6, 1],
                        strides=[1, 6, 6, 1], padding='SAME')


# First Convolutional Layer
W_conv1 = weight_variable([5, 5, 1, 32])
b_conv1 = bias_variable([32])

x_image = tf.reshape(x, [-1,IMG_W,IMG_H,1])

h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_6x6(h_conv1)


# Second Convolutional Layer
W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])

h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_6x6(h_conv2)

#print(h_pool2.get_shape()) # this is transfered into the next step


# Densely Connected Layer
W_fc1 = weight_variable([9 * 7 * 64, 1024])
b_fc1 = bias_variable([1024])

h_pool2_flat = tf.reshape(h_pool2, [-1, 9*7*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)


# Dropout
keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)


# Readout Layer
W_fc2 = weight_variable([1024, OUT_SHAPE])
b_fc2 = bias_variable([OUT_SHAPE])

y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2


saver = tf.train.Saver()
saver.restore(sess, "./model.ckpt")


# Play
fake_controller = FakeController()
real_controller = XboxController()
while True:
    ## Look
    bmp = take_screenshot()
    vec = prepare_image(bmp)

    ## Think
    joystick_output = y_conv.eval(feed_dict={x: [vec], keep_prob: 1.0})[0]

    ## Act
    manual_override = real_controller.btn_b()
    if (manual_override == 1):
        print "Manual Override"
        joystick_output = real_controller.read()

    # its not using my fake controller ...
    # I can tell because with manual override I can
    # use other buttons (that aren't mapped)

    fake_controller.write(joystick_output)

    time.sleep(0.1)
