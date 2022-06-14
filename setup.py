# -*- coding: utf-8 -*-
# ! python3


import http
import os
import shutil
import urllib.request
import http.client
import urllib3
import re


class Worker():
    local_path: str = os.path.dirname(__file__) + "/WeChatMac.dmg"
    remote_url: str = "https://dldir1.qq.com/weixin/mac/WeChatMac.dmg"
    attach_dir_path: str = "/Volumes/微信\ WeChat"
    attach_app_path: str = attach_dir_path + "/WeChat.app"
    temp_dir_path: str = os.path.dirname(__file__) + "/_temp"

    @classmethod
    def do(cls):
        # 是否在运行中
        pid: int = cls.get_wechat_pid()
        if pid:
            return

        # 准备
        ready: bool = cls.prepare()
        if not ready:
            return

        # 如果已挂载, 先卸载
        info: str = os.popen("hdiutil info").read()
        if "微信 WeChat" in info:
            os.system("hdiutil detach " + cls.attach_dir_path)
        os.system("hdiutil attach " + cls.local_path)

        # 打开
        os.system("open " + cls.attach_app_path)

    # 下载或更新
    @classmethod
    def prepare(cls) -> bool:
        # 是否已下载
        if not os.path.exists(cls.local_path):
            ret: bool = cls.download(save_path=cls.local_path)
            return ret

        read_response: http.client.HTTPResponse = urllib.request.urlopen(cls.remote_url)
        if read_response.status != 200:
            return True
        remote_size: int = int(read_response.headers["content-length"])

        local_size: int = os.path.getsize(cls.local_path)
        if remote_size == local_size:
            return True

        cache_path: str = cls.temp_dir_path + "/download/" + os.path.basename(cls.remote_url)
        if os.path.exists(cache_path):
            os.remove(cache_path)
        ret: bool = cls.download(save_path=cache_path)
        if not ret:
            return True

        # 备份旧版本
        backup_path: str = cls.temp_dir_path + "/backup/" + os.path.basename(cls.local_path)
        if os.path.exists(backup_path):
            os.remove(backup_path)
        else:
            os.makedirs(os.path.dirname(backup_path))
        shutil.move(src=cls.local_path, dst=backup_path)

        shutil.move(src=cache_path, dst=cls.local_path)
        return True

    @classmethod
    def download(cls, save_path: str) -> bool:
        manager = urllib3.PoolManager()
        down_response: urllib3.response.HTTPResponse = manager.request("GET", cls.remote_url)
        if down_response.status != 200:
            return False

        save_dir_path: str = os.path.dirname(save_path)
        if not os.path.exists(save_dir_path):
            os.makedirs(save_dir_path)

        with open(save_path, "wb") as code:
            code.write(down_response.data)
        return True

    @classmethod
    def get_wechat_pid(clss) -> int:
        pid: int = None
        ret: str = os.popen("ps -x | grep WeChat").read()
        components: list[str] = ret.split("\n")
        for item in components:
            if "WeChat.app" in item:
                numbers: list[str] = re.findall(r"[1-9]+\.?[0-9]*", item)
                if len(numbers) > 0:
                    pid_str = numbers[0]
                    pid = int(pid_str)
                    break

        return pid


Worker.do()
