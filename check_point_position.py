import math

def vector_subtract(p, o):
    """ 点oから点pへのベクトルを計算する """
    return (p[0] - o[0], p[1] - o[1])

def dot_product(v1, v2):
    """ ベクトルv1とv2の内積を計算する """
    return v1[0] * v2[0] + v1[1] * v2[1]

def vector_magnitude(v):
    """ ベクトルvの大きさを計算する """
    return math.sqrt(v[0]**2 + v[1]**2)

def is_angle_rop_larger(o, r, p, q):
    """ 角ROPが角ROQより大きいかを判定する """
    # ベクトルOR, OP, OQを計算
    vector_or = vector_subtract(r, o)
    vector_op = vector_subtract(p, o)
    vector_oq = vector_subtract(q, o)
    
    # ベクトルORとOP、ORとOQの内積を計算
    dot_or_op = dot_product(vector_or, vector_op)
    dot_or_oq = dot_product(vector_or, vector_oq)
    
    # ベクトルOR, OP, OQの大きさを計算
    mag_or = vector_magnitude(vector_or)
    mag_op = vector_magnitude(vector_op)
    mag_oq = vector_magnitude(vector_oq)
    
    # cos(角ROP)とcos(角ROQ)を計算する
    cos_rop = dot_or_op / (mag_or * mag_op)
    cos_roq = dot_or_oq / (mag_or * mag_oq)
    
    # 角度が大きいほどcosが小さくなるので、cos値を比較
    return cos_rop < cos_roq

# 2つのベクトルの外積を計算する関数
def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def check_point_position(p1, p2, p3, p4):
    # 直線 p1-p2 と点 p が左側にあるかどうかを判定
    def is_point_on_left_of_line(p1, p2, p):
        return cross_product(p1, p2, p) > 0

    # 点 p4 が直線L1(p1, p2) と直線L2(p3) で分けられている中で p1, p3側にあるか判定
    if is_point_on_left_of_line(p1, p2, p4) == is_point_on_left_of_line(p1, p3, p4):
        return True  # p4はp1とp3側にあります
    else:
        return False  # p4は反対側にあります