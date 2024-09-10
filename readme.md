###
Server.py为服务端文件，在配置好caffe环境，可正确运行的基础上，运行AsServer.py文件；此外，以for_real.prototxt作为实际部署的模型配置，models_iter_30000.caffemodel作为网络参数。

###
Relatived为模型训练相关文件，按此设置配置参数

###
Client为Unity源代码，结合ARCore，发送图像，接收定位信息，实现AR导航

###
caffe-posenet-master为原论文作者的PoseNet模型，
参考：
Kendall, A., Grimes, M., & Cipolla, R. (2015). PoseNet: A convolutional network for real-time 6-dof camera relocalization. IEEE International Conference on Computer Vision, 2938–2946. https://doi.org/10.1109/ICCV.2015.336
