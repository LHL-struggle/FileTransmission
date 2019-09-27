'''
文件描述信息结构为：文件名（300B,右边填充空格，utf-8编码）+文件大小（15B右边填充空格）
'''

from socket import *
import hashlib
import os
import time
import json
def md5(file_path):
    m = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break
            m.update(data)
    return m.hexdigest().upper()       # 大写

def passwd_md5(passwd):
    m = hashlib.md5()
    m.update(passwd)
    return m.hexdigest().upper()       # 大写

# 将字符串转换为字典
di = json.load(open("client_IP_filepath.json"))
# 欲存放的文件路径
copy_path = di["copy_path"]
# 服务器IP
servers_address = tuple(eval(di["servers_address"]))

# 校验用户名是否存在
def check_user():
    # 创建客户端套接字
    client_socket = socket(AF_INET, SOCK_STREAM)
    # 绑定本机地址与固定端口号
    # 连接到服务器
    client_socket.connect(servers_address)
    req = json.load(open("client.json"))  # 将字符串转换为字典
    # 校验要注册的用户名是否已存在
    # op = 3 表示在校验要注册的用户名是否已存在
    req_3 = {"op": 3, "args": {"uname": req["args"]["uname"]}}      # 用户名

    # 将字典转换为字符串在转为二进制
    req_3 = json.dumps(req_3).encode()     # 文件内容
    # 求取文件大小，再将大小转换为字符型，宽度为15，不足用空格填充，最后转换为字节型
    len_req_3 = str(len(req_3)).ljust(15).encode()
    # 发送文件大小
    client_socket.send(len_req_3)
    # 发送文件内容
    client_socket.send(req_3)

    # "error_code": 0 0表示不存在，1表示存在
    # 将接收的消息转换为字符型，且删除右边的的空白符合
    data = client_socket.recv(15).decode().rstrip()
    if len(data) > 0:
        # 所要接收数据的大小
        len_data = int(data)
        len_recv = 0
        req_recv = ''
        # 当接收的数据小于数据大小就一直接收
        while len_recv < len_data:
            r_recv = client_socket.recv(len_data-len_recv).decode()
            if len(r_recv) == 0:
                break
            len_recv += len(r_recv)   # 已接收的数据大小
            req_recv += r_recv        # 已接收的数据
        # 将接收到的数据转换为字典
        req_recv = dict(eval(req_recv))
        if req_recv["error_code"]:
            print('用户已存在')
            client_socket.close()
            return 0
        else:
            client_socket.close()
            print('用户不存在')
            return 1

# 注册用户
def register_user():
    # 创建客户端套接字
    client_socket = socket(AF_INET, SOCK_STREAM)

    # 服务器的地址与端口号
    # servers_address = ('169.254.183.225', 9999)
    # 连接到服务器
    client_socket.connect(servers_address)
    # 注册新用户
    # 注册信息
    req = json.load(open("client.json"))  # 将字符串转换为字典
    req["args"]["passwd"] = passwd_md5(req["args"]["passwd"].encode())  # 密码的MD5值
    # 将字典转换为字符串在转为二进制
    req = json.dumps(req).encode()              # 文件内容
    # 求取文件大小，再将大小转换为字符型，宽度为15，不足用空格填充，最后转换为字节型
    len_req = str(len(req)).ljust(15).encode()
    # 发送注册文件大小
    client_socket.send(len_req)
    # 发送注册文件内容
    client_socket.send(req)
    # {"op": 2,"error_code": 0  # 0表示注册成功，1表示注册失败}
    # 将接收的消息转换为字符型，且删除右边的的空白符合
    data_2 = client_socket.recv(15).decode().rstrip()
    if len(data_2) > 0:
        # 所要接收数据的大小
        len_data_2 = int(data_2)
        len_recv_2 = 0
        req_recv_2 = ''
        # 当接收的数据小于数据大小就一直接收
        while len_recv_2 < len_data_2:
            r_recv_2 = client_socket.recv(len_data_2 - len_recv_2).decode()
            if len(r_recv_2) == 0:
                break
            len_recv_2 += len(r_recv_2)  # 已接收的数据大小
            req_recv_2 += r_recv_2  # 已接收的数据
        # 将接收到的数据转换为字典
        req_recv_2 = dict(eval(req_recv_2))
        if req_recv_2["error_code"]:
            print('注册失败')
        else:
            print('注册成功')

# 登陆并下载
def  login_user():
    # 创建客户端套接字
    client_socket = socket(AF_INET, SOCK_STREAM)
    # 连接到服务器
    client_socket.connect(servers_address)
    # 登陆信息
    req = json.load(open("client.json"))  # 将字符串转换为字典
    req_uname = req["args"]["uname"]
    req_md5 = passwd_md5(req["args"]["passwd"].encode())  # 密码的MD5值
    req = {"op": 1, "args": {"uname": req_uname, "passwd": req_md5}}
    # 将字典转换为字符串在转为二进制
    req = json.dumps(req).encode()  # 文件内容
    # 求取文件大小，再将大小转换为字符型，宽度为15，不足用空格填充，最后转换为字节型
    len_req = str(len(req)).ljust(15).encode()
    # 发送登录文件大小
    client_socket.send(len_req)
    # 发送登陆文件内容
    client_socket.send(req)
    # 将接收的消息转换为字符型，且删除右边的的空白符合
    data_2 = client_socket.recv(15).decode().rstrip()
    if len(data_2) > 0:
        # 所要接收数据的大小
        len_data_2 = int(data_2)
        len_recv_2 = 0
        req_recv_2 = ''
        # 当接收的数据小于数据大小就一直接收
        while len_recv_2 < len_data_2:
            r_recv_2 = client_socket.recv(len_data_2 - len_recv_2).decode()
            if len(r_recv_2) == 0:
                break
            len_recv_2 += len(r_recv_2)  # 已接收的数据大小
            req_recv_2 += r_recv_2  # 已接收的数据
        # 将接收到的数据转换为字典
        req_recv_2 = dict(eval(req_recv_2))
        # {"op": 1,"error_code": 0  # 0表示登录成功，1表示登录失败}
        if req_recv_2["error_code"]:
            print('登录失败')
            client_socket.close()
        else:
            print('登录成功')
            # 文件夹的数目和文件数目
            Num_dir, Num_file = 0, 0
            # 文件总大小
            Full_file_size = 0
            # 开始拷贝时间
            start_time = time.time()
            while 1:
                # 拷贝进度
                new_data, old_data = 0, 0
                # 接收服务器返回的文件名称与大小,删除文件名右边的空白符，得取文件名

                file_1, recv_1 = 300, 0
                file_path_name = b''
                a = 0
                while 1:
                    recv_file_path_name = client_socket.recv(file_1 - recv_1)
                    # 当接收文件为空，跳出整个循环
                    if len(recv_file_path_name) == 0:
                        a = 1
                        break
                    recv_1 += len(recv_file_path_name)  # 接收文件大小
                    file_path_name += recv_file_path_name
                    if recv_1 == 300:
                        break
                if a == 1:
                    break
                file_path_name = file_path_name.decode().rstrip()

                # 如果是从Linux中传输过来的文件就将'/'换为'\\'
                file_path_name = file_path_name.replace('/', '\\')
                # 文件安放路径
                receive_file_path = copy_path + '\\' + file_path_name
                # 文件名
                file_name = file_path_name.split('\\')[-1]
                file_path_index = len(receive_file_path)-len(file_name)-1
                # 获取目录

                # # 此法有漏洞，当文件名与目录名相同时，他会同时将文件名还有目录名都删除
                # # file_path = receive_file_path.replace(file_name, '')

                file_path = receive_file_path[0:file_path_index]
                # 删除文件名大小值右边的空白符，得取文件大小
                # file_size = int((client_socket.recv(15).decode()).rstrip())
                file_size_1, re_file_size_1 = 15, 0
                file_size = b''
                while 1:
                    re_file_size = client_socket.recv(file_size_1-re_file_size_1)
                    re_file_size_1 += len(re_file_size)
                    file_size += re_file_size   # 文件内容
                    if re_file_size_1 == 15:
                        break
                file_size = int(file_size.decode().rstrip())
                # 文件夹总大小
                if file_size != -1:
                    Full_file_size += file_size

                # 源文件的MD5值
                file_md5_1, re_file_md5_1 = 32, 0
                file_md5 = b''
                # 源文件的MD5值
                while 1:
                    re_file_md5 = client_socket.recv(file_md5_1-re_file_md5_1)
                    re_file_md5_1 += len(re_file_md5)     # 接收文件大小
                    file_md5 += re_file_md5               # 接收文件内容
                    if re_file_md5_1 == 32:
                        break
                file_md5 = file_md5.decode().rstrip()
                print('文件名：%s； 文件大小：%s； md5: %s' % (file_name, file_size, file_md5))
                # 如果file_size == -1则表示为空目录
                if file_size == -1:
                    if not os.path.exists(receive_file_path):
                        os.makedirs(receive_file_path)  # 创建空目录
                        Num_dir += 1
                        print('创建了空目录%s\n' % receive_file_path)
                        continue  # 跳出此次循环

                # 判断路径是否存在,如果不存在则创建文件夹
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                    print('创建了:%s' % file_path)

                # 已拷贝文件大小
                copy_size = 0
                while 1:
                    # 接收服务器返回的信息
                    '''
                    注意TCP并不是以包的形式发的，他是以字节流的形式发送的所以可能会出现粘包问题
                    注意recv接收值为理想接收值但实际上却并不一定能够接收这么多，官方建议最多只能接收8k的数据
                    解决办法：recv接收的文件大小设为：源文件大小 - 已拷贝文件大小，在循环接收，直到文件接收完毕，跳出循环接收
                    '''
                    receive_file = client_socket.recv(file_size - copy_size)
                    if len(receive_file) == 0:
                        # 如果是空文件，则创建一个空的文件
                        open(receive_file_path, "ab").close()
                        break
                    # 已拷贝文件大小
                    copy_size += len(receive_file)
                    # 写入拷贝的内容
                    with open(receive_file_path, "ab") as f:
                        f.write(receive_file)
                    new_data = int(copy_size * 100 / file_size)
                    # 文件拷贝进度
                    if new_data - old_data >= 5:
                        old_data = new_data
                        print('拷贝完成:%%%d' % old_data)
                    # 如果文件拷贝大小等于要拷贝的文件大小，则提示数据传输完成，跳出循环，
                    if copy_size == file_size:
                        break
                print('数据传输已完成：', copy_size)
                # 比对源文件的MD5值与拷贝文件的MD5值是否一致
                if md5(receive_file_path) == file_md5:
                    Num_file += 1
                    print('%s拷贝文件与源文件一致\n' % file_name)
                else:
                    print('%s拷贝文件与源文件不一致，拷贝失败' % file_name)
                    break
            # 拷贝结束时间
            end_time = time.time()
            use_time = end_time - start_time
            # 关闭客户端套接字
            client_socket.close()
            print('拷贝空文件夹数目:%d个，文件数目:%d个，拷贝文件总大小:%sM, 拷贝速度:%7.4fm/s, 拷贝用时:%ds' % (Num_dir, Num_file, float(Full_file_size / 1000000), float(Full_file_size / 1000000) / use_time, use_time))

print('1:校验用户名是否存在\n2:注册用户\n3:登录并下载文件\n0:结束')
while True:
    o = input('请选择使用功能:')
    if o == '1':
        check_user()
    if o == '2':
        if check_user():  # check_user() 用户名存在返回0，不存在返回1
            register_user()
    if o == '3':
        login_user()
    if o == '0':
        break



