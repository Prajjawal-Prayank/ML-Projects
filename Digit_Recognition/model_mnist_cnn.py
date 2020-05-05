# -*- coding: utf-8 -*-
"""model_mnist_cnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/178nvJf5kAm-SJYFlpHOsghwd-EO7zALW
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
import tensorflow as tf
print(tensorflow.__version__)

from tensorflow.examples.tutorials.mnist import input_data

mnist= input_data.read_data_sets("MNIST_data/",one_hot=True)



# some helper functions:-

# 1) initializing weights
def init_weights(shape):
    init_random_dist=tf.truncated_normal(shape,stddev=0.1)
    """Outputs random values from a truncated normal distribution.
    The generated values follow a normal distribution with specified mean and standard deviation, 
    except that values whose magnitude is more than 2 standard deviations from the mean are dropped 
    and re-picked."""
    """Normal distribution, also known as the Gaussian distribution, is a probability distribution that is 
    symmetric about the mean, showing that data near the mean are more frequent in occurrence than data far 
    from the mean. In graph form, normal distribution will appear as a bell curve."""
    return tf.Variable(init_random_dist)

# 2) initializing bias
def init_bias(shape):
    init_bias_vals=tf.constant(0.1,shape=shape)          # all values are 0.1 and the shape is that of the tensor
    return tf.Variable(init_bias_vals)

# 3) convolutional func
def conv2d(x,W):
    # x is the input tensor.A 4d tensor. its shape:- [batch,height,width,channel]  (channel is 1 for grayscale and 3 for rgb)
    # batch basically tells which all images are being taken as i/p/. height and weight are of individual images. 
    # W is the kernel(or the filter).its shape:- [filter height,filter width,no. of channels as i/p, no. of channels as o/p ]
    return tf.nn.conv2d(x,W,strides=[1,1,1,1],padding='SAME')    
                        # basic 2d convolutional function

# 4) pooling
def max_pool_2by2(x):
    # x is the input tensor. its shape:- [batch,height,width,channel] 
    return tf.nn.max_pool(x,ksize=[1,2,2,1],strides=[1,2,2,1],padding="SAME")
                # pooling is done only along height and width. so, it is basically 2*2 pooling
                # ksize specifies the size of the window for each dimension of input tensor
                # stride specifies the stride of the sliding window for each dimension of input tensor



# convolutional layer
def convolutional_layer(input_x,shape):
    w=init_weights(shape)
    b=init_bias([shape[3]])
    return tf.nn.relu(conv2d(input_x,w)+b)

# normal (or, fully connected) layer
def normal_full_layer(input_layer,size):
    input_size=int(input_layer.get_shape()[1])
    w=init_weights([input_size,size])
    b=init_bias([size])
    return tf.matmul(input_layer,w)+b



# placeholder
x=tf.placeholder(tf.float32,shape=[None,784])
y_true=tf.placeholder(tf.float32,shape=[None,10])



# layers
x_image= tf.reshape(x,[-1,28,28,1])   # converting the i/p img back to layers. The 28*28 is h*w. 1 is coz of grayscale.

# first convolutional layer
convo_1=convolutional_layer(x_image,shape=[5,5,1,32]) # the wt. tensor is [5,5,1,32]
                                                      # 5 by 5 convolutional layer. so, this convolution will compute
                                                      # 32 features for each 5 by 5 patch. 1 is the i/p channels.32 is the no.
                                                      # of o/p channels.

# first pooling layer
convo_1_pooling = max_pool_2by2(convo_1)

# second convolutional layer
convo_2 = convolutional_layer(convo_1_pooling,shape=[5,5,32,64])    # 64 features
convo_2_pooling= max_pool_2by2(convo_2)

#this o/p is now flattened out so that it gets connected to a fully connected layer
convo_2_flat= tf.reshape(convo_2_pooling,[-1,7*7*64])
#here 7*7 is dimension of each image. here's how:-
#28*28 on pooling with 2*2 gives 14*14
#14*14 on pooling with 2*2 gives 7*7
#NOTE:- the dimension of the image didn't change on convolution as "SAME" type of convolution is used.Meaning to say that the padding is such that the final
#       o/p dimension remains the same.here, padding=(f-1)/2=(5-1)/2=2 . so after padding , 28*28 becomes 32*32. and on convolution gives 28*28 
#       (as, n-f+1=32-5+1=28  )
full_layer_one=tf.nn.relu(normal_full_layer(convo_2_flat,1024))



# dropout
hold_prob= tf.placeholder(tf.float32)
full_one_dropout= tf.nn.dropout(full_layer_one,keep_prob=hold_prob)

y_pred= normal_full_layer(full_one_dropout,10)    # 10 is the no. of labels



# loss function
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_true,logits=y_pred))

# optimizer
optimizer = tf.train.AdamOptimizer(learning_rate=0.001)
train =  optimizer.minimize(cross_entropy)

init= tf.global_variables_initializer()

steps=5000
with tf.Session() as sess:
    sess.run(init)
    
    for i in range(steps):
        batch_x,batch_y= mnist.train.next_batch(50)
        sess.run(train,feed_dict={x:batch_x,y_true:batch_y,hold_prob:0.5})   
                                    # hold_prob:0.5 implies every neuron has a 50% hold probablity
        if(i%100==0):
            print("On Step: {}".format(i))
            print("Accuracy:  ")
            matches=tf.equal(tf.argmax(y_pred,1),tf.argmax(y_true,1))
            #argmax(input, axis=None, name=None, dimension=None) Returns the index with the largest value across axis of a tensor
            
            acc=tf.reduce_mean(tf.cast(matches,tf.float32))
            print(sess.run(acc,feed_dict={x:mnist.test.images,y_true:mnist.test.labels,hold_prob:1.0}))
            # during testing we don't want to dropout any of the neurons. So, we write hold_prob:1.0 , meaning that every neuron will be held at its 
            # position and none will be dropped out
            print('\n')





