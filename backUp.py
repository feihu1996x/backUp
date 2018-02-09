#!/usr/bin/python3

"""
@file: backUp.py
@brief: 将本地文件（夹）打包上传至阿里云OSS
@author: feihu1996.cn
@date: 18-02-07
@version: 1.0
"""

import os
import shutil
import tarfile
import time
import logging
import traceback
import sys

import oss2

# 请到https://github.com/feihu1996x/sendMail下载sendMail模块，并将其添加至python模块查找路径中
from sendMail import sendMail

# 请在settings.py中配置您的邮件信息
from settings import mailConfig

logging.basicConfig(level=logging.DEBUG,format="%(asctime)s-%(levelname)s-%(message)s")

mailer = sendMail.Sendmail(**mailConfig)

class Backup:
    def __init__(self, accessKeyId, accessKeySecret, endpoint, bucket_name, localFilePath):
        self.accessKeyId = accessKeyId
        self.accessKeySecret = accessKeySecret
        self.endpoint = endpoint
        self.bucket_name = bucket_name

        try:
            self.auth =  oss2.Auth(self.accessKeyId, self.accessKeySecret)
            self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        except:
            e = traceback.format_exc()
            logging.debug(e)
            logging.debug("正在发送debug邮件...")
            mailer.sendMail(receiverList=["邮件发送方列表,如xxx@example.com"], msgPlain=e, subject="debug", mailType="plain")
            logging.debug("debug邮件发送成功")
            sys.exit(1)

        # 将要备份的本地打包文件名
        self.localFile = self.__getLocalFile(localFilePath)
        # 将要上传至云端的打包文件名
        self.remoteFile = self.localFile

    def backUp(self):
        try:
            result = self.bucket.put_object_from_file( self.remoteFile, self.localFile)
        except:
            e = traceback.format_exc()
            logging.debug(e)
            logging.debug("正在发送debug邮件...")
            mailer.sendMail(receiverList=["邮件发送方列表,如xxx@example.com"], msgPlain=e, subject="debug", mailType="plain")
            logging.debug("debug邮件发送成功")
            sys.exit(1)

        try:
            logs = 'http status: {0}'.format(result.status)+'\n'+'request_id: {0}'.format(result.request_id)+'\n'+'ETag: {0}'.format(result.etag)+'\n'+'date: {0}'.format(result.headers['date'])
            logging.debug(logs)
            logging.debug("正在发送请求日志...")
            mailer.sendMail(receiverList=["邮件发送方列表,如xxx@example.com"], msgPlain=logs, subject="oss请求日志", mailType="plain")
            logging.debug("请求日志发送成功")        
        except:
            e = traceback.format_exc()
            logging.debug(e)
            logging.debug("正在发送debug邮件...")
            mailer.sendMail(receiverList=["邮件发送方列表,如xxx@example.com"], msgPlain=e, subject="debug", mailType="plain")
            logging.debug("debug邮件发送成功")
            sys.exit(1)

        os.remove(self.localFile)

    def __getLocalFile(self, localFilePath):
        """
        根据localFilePath生成本地打包文件
        """
        try:
            localFileName = localFilePath.split("/")[-1]+"-backup"+"-"+str(round(time.time()))+".tar.gz"
            tar = tarfile.open(localFileName, "w:gz")
            tar.add(localFilePath)
            tar.close()
        except:
            e = traceback.format_exc()
            logging.debug(e)
            logging.debug("正在发送debug邮件...")
            mailer.sendMail(receiverList=["邮件发送方列表,如xxx@example.com"], msgPlain=e, subject="debug", mailType="plain")
            logging.debug("debug邮件发送成功")
            sys.exit(1)
            
        return localFileName

if __name__ == "__main__":
	# 实例化Backup对象
	backup = Backup("你的accessKeyId", "你的accessKeySecret", "你的endpoint", "你的bucket_name", "将要上传的本地文件(夹)的绝对路径")
	
	# 执行上传操作
	backup.backUp()