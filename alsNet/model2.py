import os
import sys
BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, '../utils'))
import tensorflow as tf
import numpy as np
import tf_util
from pointnet_util import pointnet_sa_module, pointnet_fp_module

def placeholder_inputs(batch_size, points_in, num_feat):
    pointclouds_pl = tf.placeholder(tf.float32, shape=(batch_size, points_in, num_feat), name='pointcloud_in')
    labels_pl = tf.placeholder(tf.int32, shape=(batch_size, points_in), name='labels')
    #smpws_pl = tf.placeholder(tf.float32, shape=(batch_size, num_point))
    return pointclouds_pl, labels_pl


def get_model(point_cloud, is_training, num_class, bn_decay=None):
    """ Semantic segmentation PointNet, input is BxNx3, output Bxnum_class """
    batch_size = point_cloud.get_shape()[0].value
    num_point = point_cloud.get_shape()[1].value
    end_points = {}
    l0_xyz = tf.slice(point_cloud, [0,0,0], [-1,-1,3])  # point coordinates
    l0_points = tf.slice(point_cloud, [0,0,3], [-1,-1,-1])  #point attributes
    end_points['l0_xyz'] = l0_xyz

    # Set Abstraction layers
    l1_xyz, l1_points, l1_indices = pointnet_sa_module(l0_xyz, l0_points, npoint=4096, radius=3, nsample=64, mlp=[64,64,64,128], pooling='max_and_avg', mlp2=None, group_all=False, is_training=is_training, bn_decay=bn_decay, scope='layer1')
    l2_xyz, l2_points, l2_indices = pointnet_sa_module(l1_xyz, l1_points, npoint=1024, radius=10, nsample=32, mlp=[128,128,128], pooling='max_and_avg', mlp2=None, group_all=False, is_training=is_training, bn_decay=bn_decay, scope='layer2')
    #l3_xyz, l3_points, l3_indices = pointnet_sa_module(l2_xyz, l2_points, npoint=512, radius=10, nsample=32, mlp=[128,128,256], pooling='max_and_avg', mlp2=None, group_all=False, is_training=is_training, bn_decay=bn_decay, scope='layer3')
    #l4_xyz, l4_points, l4_indices = pointnet_sa_module(l3_xyz, l3_points, npoint=256, radius=50, nsample=32, mlp=[256,256,512], pooling='max_and_avg', mlp2=None, group_all=False, is_training=is_training, bn_decay=bn_decay, scope='layer4')
    #l5_xyz, l5_points, l5_indices = pointnet_sa_module(l4_xyz, l4_points, npoint=100, radius=25, nsample=32, mlp=[512,512,1024], mlp2=None, group_all=False, is_training=is_training, bn_decay=bn_decay, scope='layer5')
    # debug line:
    # l4_points = tf.Print(l1_points, [l0_xyz, l0_points, l1_xyz, l1_points], 'ln-points', -1, 12)
    #end_points['l1_xyz'] = l1_xyz
    #end_points['l2_xyz'] = l2_xyz
    #end_points['l3_xyz'] = l3_xyz
    #end_points['l4_xyz'] = l4_xyz
    #end_points['l5_xyz'] = l5_xyz

    # Feature Propagation layers
    #l4_points = pointnet_fp_module(l4_xyz, l5_xyz, l4_points, l5_points, [512,512], is_training, bn_decay, scope='fa_layer0')
    #l3_points = pointnet_fp_module(l3_xyz, l4_xyz, l3_points, l4_points, [256,256], is_training, bn_decay, scope='fa_layer1')
    #l2_points = pointnet_fp_module(l2_xyz, l3_xyz, l2_points, l3_points, [256,256], is_training, bn_decay, scope='fa_layer2')
    l1_points = pointnet_fp_module(l1_xyz, l2_xyz, l1_points, l2_points, [128,128], is_training, bn_decay, scope='fa_layer3')
    l0_points = pointnet_fp_module(l0_xyz, l1_xyz, l0_points, l1_points, [128,128,128], is_training, bn_decay, scope='fa_layer4')

    # FC layers
    net = tf_util.conv1d(l0_points, 128, 1, padding='VALID', bn=True, is_training=is_training, scope='fc1', bn_decay=bn_decay)
    end_points['feats'] = net
    net = tf_util.dropout(net, keep_prob=0.7, is_training=is_training, scope='dp1')
    net = tf_util.conv1d(net, num_class, 1, padding='VALID', activation_fn=None, scope='fc2', name='net')

    return net, end_points


def get_loss(pred, label):
    """ pred: BxNxC,
        label: BxN,
        smpw: BxN """
    #classify_loss = tf.losses.sparse_softmax_cross_entropy(labels=label, logits=pred, scope='loss')
    classify_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=label, logits=pred, name='loss')
    tf.summary.scalar('classify_loss', classify_loss)
    return classify_loss
