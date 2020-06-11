'''
@author: dingcui
@contact: dingcui@bupt.edu.cn
@file: demo.py.py
@time: 2020/6/11 11:39
'''

# 参考https://blog.csdn.net/weixin_42052081/article/details/89108966

import numpy as np

# 邻接图矩阵表征
A = np.matrix([
    [0, 1, 0, 0],
    [0, 0, 1, 1],
    [0, 1, 0, 0],
    [1, 0, 1, 0]
], dtype=float)

# 接下来抽取出特征,基于每个节点的索引为其生成两个整数特征

X = np.matrix([[i, -i] for i in range(A.shape[0])], dtype=float)

# 得到邻接矩阵A,输入特征的集合为X,对其运用传播规则:f(X, A) = AX

#print(A * X)

# 得到的每个节点的表征(每一行)现在是其相邻节点特征的和,图卷积层将每个节点表示为其相邻节点的聚合

# 问题1:节点的聚合表征不包含自己的特征
# 解决方法:增加自环,将邻接矩阵与单位矩阵相加
I = np.matrix(np.eye(A.shape[0]))
A_hat = A + I

# 问题2:度大的节点其特征表征中将具有较大的值,度小的节点将具有较小的值,会导致提督爆炸或梯度消失,也会影响随机梯度下降算法
# 解决方法:对特征表征进行归一化处理
#   通过将邻接矩阵A与度矩阵D逆 相乘,对其进行变换,从而通过节点的度对特征表征进行归一化.
#   传播规则:f(X, A) = D⁻¹AX
D = np.array(np.sum(A,axis=0))[0]
D = np.matrix(np.diag(D))

print(D**-1*A)
#打印后可以观察到,矩阵每一行的权重都除以该行对应的节点的度

#D_hat 是 A_hat = A + I 对应的度矩阵
D_hat = np.array(np.sum(A_hat,axis=0))[0]
D_hat = np.matrix(np.diag(D_hat))

#应用权重
W = np.matrix([[1,-1],
               [-1,1]])

print(D_hat**-1*A_hat*X*W)

#如果想减小特征表征的维度,可以减小权重W的规模
W = np.matrix([[1],
               [-1]])

print(D_hat**-1*A_hat*X*W)

#添加激活函数:relu
def relu(x):
    return (abs(x)+x)/2

W = np.matrix([[1,-1],
               [-1,1]])

print(relu(D_hat**-1*A_hat*X*W))

