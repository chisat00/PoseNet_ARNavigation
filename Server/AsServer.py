import caffe
import numpy as np
import cv2
import socket
import json
import xml.etree.ElementTree as ET
import struct
caffe_root = '/home/lemon/work/caffe-posenet-master'  # Change to your directory to caffe-posenet
import sys
sys.path.append('/home/lemon/work/caffe-posenet-master/python') ####
import lmdb
import os
import sys

folder_path = '/home/lemon/work/caffe-posenet-master/posenet/scripts/real_lmdb/'
files = os.listdir(folder_path)
# caffe setting
model_file = '/home/lemon/work/caffe-posenet-master/posenet/models/for_real.prototxt'
weights_file = '/home/lemon/work/caffe-posenet-master/posenet/models_iter_30000.caffemodel'
caffe.set_mode_gpu()
# net = caffe.Net(model_file,weights_file,caffe.TEST)

#build a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Host = '192.168.43.168' #need to change!!!!
server_socket.bind((Host, 8888))
server_socket.listen(20)
# print("waitng for connection...") # help to debug...

# new_socket, client_ip_port = server_socket.accept()
# print("connection is ok...") # help to debug...
## delete used...
# print "delecting used data..."
# for file in files:
#     t = os.path.join(folder_path, file)
#     print('delecting : ', t)
#     os.remove(t)

while(1):
    if not server_socket: break
    print("waitng for connection...") # help to debug...
    new_socket, client_ip_port = server_socket.accept()
    print("connection is ok...") # help to debug...
    #receive data

    received = b''
    times_mod = ''
    times_mod = new_socket.recv(8)
    # times = str(times)
    # times = times.decode('utf-8')
    #print(times)
    #print(type(times))
    # into int
    times = times_mod[:4]
    mod = times_mod[4:8]
    times = struct.unpack('<HH', times)[0]
    mod = struct.unpack('<HH', mod)[0]
    print('times: ', times)
    print('mod: ', mod)

    counter = 0
    for _ in range(times):
        counter += 1
        chunk = new_socket.recv(1024)
        received += chunk
    chunk = new_socket.recv(mod)
    received += chunk
    
    print "receive times: ", counter
    print "data received......"# help to debug...

    #    step 1: change received data into image
    arr =  np.frombuffer(received, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    # cv2.imshow("ttt", img)
    # cv2.waitKey()

    # rotate
    h, w = img.shape[:2]
    center = (w//2, h//2)
    m = cv2.getRotationMatrix2D(center, 0, 1.0) #####
    img = cv2.warpAffine(img, m, (w, h))

    #cv2.imshow("ttt", img)
    #cv2.waitKey()
    print "trans into img successfully..."

    ### delete used...
    # print "delecting used data..."
    # for file in files:
    #     t = os.path.join(folder_path, file)
    #     print('delecting : ', t)
    #     os.remove(t)
    ####
    env = lmdb.open('/home/lemon/work/caffe-posenet-master/posenet/scripts/real_lmdb', map_size=int(1e12))
    count = 0
    useless = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)

    X = img
    X = cv2.resize(X, (455, 256))
    X = np.transpose(X, (2, 0, 1))
    im_dat = caffe.io.array_to_datum(np.array(X).astype(np.uint8))
    im_dat.float_data.extend(useless)
    str_id = '{:0>10d}'.format(count)
    with env.begin(write=True) as txn:
        print("open is ok...")
        # print(im_dat)
        txn.put(str_id, im_dat.SerializeToString())
    
    # txn.commit()
    env.close()
    print 'create lmdb suceesfully...'

    # init the net
    #
    net = caffe.Net(model_file,weights_file,caffe.TEST)
    #

    net.forward()

    pose_q= net.blobs['cls3_fc_wpqr'].data
    pose_x= net.blobs['cls3_fc_xyz'].data

    ###########
    pose_q = pose_q.ravel()
    pose_x = pose_x.ravel()
    
    res = []
    for item in pose_x:
        res.append(item)
    for item in pose_q:
        res.append(item)


    pose = res

####################################################################################
    # step 3: send pose to client
    root = ET.Element("root")
    for it in pose:
        child = ET.SubElement(root, 'item')
        child.text = str(it)
    pose_stream = ET.tostring(root, encoding='utf-8')
    # print(pose_stream) ############################# 
    print(pose)
    new_socket.sendall(pose_stream)
    print("pose has been sended...\n\n") # help to debug...

    # show img...
    # cv2.imshow("ttt", img)
    # cv2.waitKey()    
    del net # delect used net
    new_socket.close()

server_socket.close()
