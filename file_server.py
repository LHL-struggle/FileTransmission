#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
import threading
import hashlib
import json
import user_reg_login



def get_file_md5(file_path):
    m = hashlib.md5()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break    
            m.update(data)
    
    return m.hexdigest().upper()

# 发送单个文件
def send_one_file(sock_conn, file_abs_path):
    '''
    函数功能：将一个文件发送给客户端
    参数描述：
        sock_conn 套接字对象
        file_abs_path 待发送的文件的绝对路径
    '''
    file_name = file_abs_path[len(dest_file_parent_path):]
    if file_name[0] == '\\' or file_name[0] == '/':
        file_name = file_name[1:]

    file_size = os.path.getsize(file_abs_path)
    file_md5 = get_file_md5(file_abs_path)

    file_name = file_name.encode()
    file_name += b' ' * (300 - len(file_name))
    file_size = "{:<15}".format(file_size).encode()

    file_desc_info = file_name + file_size + file_md5.encode()

    sock_conn.send(file_desc_info)
    with open(file_abs_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break
            sock_conn.send(data)

# 发空文件夹
def send_empty_dir(sock_conn, dir_abs_path):
    '''
    函数功能：将一个空文件夹发送给客户端
    参数描述：
        sock_conn 套接字对象
        dir_abs_path 待发送的空文件夹的绝对路径
    '''
    file_name = dir_abs_path[len(dest_file_parent_path):]
    if file_name[0] == '\\' or file_name[0] == '/':
        file_name = file_name[1:]

    file_size = -1
    file_md5 = " " * 32

    file_name = file_name.encode()
    file_name += b' ' * (300 - len(file_name))
    file_size = "{:<15}".format(file_size).encode()

    file_desc_info = file_name + file_size + file_md5.encode()
    sock_conn.send(file_desc_info)

# 发送文件夹
def send_dir(sock_conn):
    '''
    发送非空文件夹
    '''
    for root, dirs, files in os.walk(dest_file_abs_path):
        if len(dirs) == 0 and len(files) == 0:
            send_empty_dir(sock_conn, root)
            continue

        for f in files:
            file_abs_path = os.path.join(root, f)
            print(file_abs_path)
            send_one_file(sock_conn, file_abs_path)


def user_service_thread(sock_conn):
    # 将接收的消息转换为字符型，且删除右边的的空白符合
    data_len = sock_conn.recv(15).decode().rstrip()
    print(data_len)
    if len(data_len) > 0:
        data_len = int(data_len)

        # 接收变量
        recv_size = 0
        json_data = ""
        while recv_size < data_len:
            tmp = sock_conn.recv(data_len - recv_size).decode()
            if len(tmp) == 0:
                break
            json_data += tmp
            recv_size += len(tmp)
        print(json_data)
        # 此处有修改
        req = json.loads(json_data)  # 将字符串转换为字典

        # 登录校验
        if req["op"] == 1:
            # 登录校验
            rsp = {"op": 1, "error_code": 0}      # 表示登录成功
            '''
                check_uname_pwd(user_name, password)
                函数功能：校验用户名和密码是否合法
                函数参数：
                user_name 待校验的用户名
                password 待校验的密码
                返回值：校验通过返回0，校验失败返回1
                '''
            if user_reg_login.check_uname_pwd(req["args"]["uname"], req["args"]["passwd"]):
                # 登录失败
                print('登录失败')
                rsp["error_code"] = 1
            rsp_1 = rsp
            # 将字典转换为字符串在转换为二进制
            rsp = json.dumps(rsp).encode()

            # 求取发送数据的大小，左对齐，宽度15，不足以空白补齐，在转换为二进制
            data_len = "{:<15}".format(len(rsp)).encode()
            # 发送数据大小
            sock_conn.send(data_len)
            # 发送数据
            sock_conn.send(rsp)

            # 如果登录校验成功，则向客户端发送文件
            # 此处有修改
            if not rsp_1["error_code"]:
                send_dir(sock_conn)
            # 关闭连接
            sock_conn.close()

        # 用户注册
        elif req["op"] == 2:
            rsp = {"op": 2, "error_code": 0}       # 0表注册成功

            if not user_reg_login.user_reg(req["args"]["uname"], req["args"]["passwd"], req["args"]["phone"], req["args"]["email"]):
                rsp["error_code"] = 1       # 1表注册失败

            # 将校验字典转化为字符串，并转为二进制
            rsp = json.dumps(rsp).encode()
            # 求取校验字典的大小，左对齐，宽度15，不足以空白补齐，在转换为二进制
            data_len = "{:<15}".format(len(rsp)).encode()
            # 发送数据大小
            sock_conn.send(data_len)
            # 发送数据
            sock_conn.send(rsp)
            # 关闭套接字
            sock_conn.close()
        # 校验用户名是否存在
        elif req["op"] == 3:
            rsp = {"op": 3, "error_code": 0}     # 0表示不存在
            # check_user_name(user_name)返回值：校验通过返回0，校验失败返回非零（格式错误返回1，用户名已存在返回2）
            ret = user_reg_login.check_user_name(req["args"]["uname"])
            if ret == 2:
                rsp["error_code"] = 1   # 1表示存在
                print(rsp["error_code"])
            # 将校验字典转化为字符串，并转为二进制
            rsp = json.dumps(rsp).encode()
            # 求取校验字典的大小，左对齐，宽度15，不足以空白补齐，在转换为二进制
            data_len = "{:<15}".format(len(rsp)).encode()
            # 发送数据大小
            sock_conn.send(data_len)
            # 发送数据
            sock_conn.send(rsp)
            # 关闭套接字
            sock_conn.close()            

di = json.load(open("client_IP_filepath.json"))
dest_file_abs_path = di["dest_file_abs_path"]
dest_file_parent_path = os.path.dirname(dest_file_abs_path)
dest_file_name = os.path.basename(dest_file_abs_path)


sock_listen = socket.socket()

# 将字符串转换为字典
di = json.load(open("client_IP_filepath.json"))
# 从字典中提取IP，并转换为元组
server_IP = tuple(eval(di["server_IP"]))
sock_listen.bind(server_IP)
sock_listen.listen(5)

while True:
    sock_conn, client_addr = sock_listen.accept()
    print(client_addr, "已连接！")
    threading.Thread(target=user_service_thread, args=(sock_conn, )).start()

sock_listen.close()