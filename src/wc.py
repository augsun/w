# -*- coding: utf-8 -*-
# ! python3


import http
import os
import shutil
import urllib.request
import http.client
import urllib3
import re
import time


class Wc():
    root_dir: str = os.path.dirname(os.path.dirname(__file__))
    local_path: str = root_dir + "/WeChatMac.dmg"
    remote_url: str = "https://dldir1.qq.com/weixin/mac/WeChatMac.dmg"
    attach_dir_path: str = "/Volumes/微信\ WeChat"
    attach_app_path: str = attach_dir_path + "/WeChat.app"
    temp_dir_path: str = root_dir + "/_temp"

    @classmethod
    def do(cls):
        # 是否在运行中
        pid: int = cls.get_wechat_pid()
        if pid:
            print("\nWeChat already running!")
            return

        # 准备
        ready: bool = cls.prepare()
        if not ready:
            return

        # 如果已挂载, 先卸载
        print("")
        info: str = os.popen("hdiutil info").read()
        if "微信 WeChat" in info:
            os.system("hdiutil detach " + cls.attach_dir_path)
        os.system("hdiutil attach " + cls.local_path)

        # 打开
        os.system("open " + cls.attach_app_path)

    # 下载或更新
    @classmethod
    def prepare(cls) -> bool:
        # 还没下载, 则直接下载
        if not os.path.exists(cls.local_path):
            ret: bool = cls.download(save_path=cls.local_path)
            return ret

        # 检查是否有新版本
        read_response: http.client.HTTPResponse = urllib.request.urlopen(cls.remote_url)
        if read_response.status != 200:
            return True
        remote_size: int = int(read_response.headers["content-length"])
        local_size: int = os.path.getsize(cls.local_path)
        if remote_size == local_size:
            return True

        # 有新版本
        print("\nNew version found, will be updated!")

        # 准备目录
        temp_download_dir: str = cls.temp_dir_path + "/download"
        cache_path: str = temp_download_dir + "/" + os.path.basename(cls.remote_url)
        if os.path.exists(cache_path):
            os.remove(cache_path)
        if not os.path.exists(temp_download_dir):
            os.makedirs(temp_download_dir)

        # 下载
        ret: bool = cls.download(save_path=cache_path)
        if not ret:
            return False

        # 备份旧版本
        temp_backup_dir: str = cls.temp_dir_path + "/backup"
        backup_path: str = temp_backup_dir + "/" + os.path.basename(cls.local_path)
        if os.path.exists(backup_path):
            os.remove(backup_path)
        else:
            if not os.path.exists(temp_backup_dir):
                os.makedirs(temp_backup_dir)
        shutil.move(src=cls.local_path, dst=backup_path)
        shutil.move(src=cache_path, dst=cls.local_path)
        return True

    @classmethod
    def download(cls, save_path: str) -> bool:
        print("")
        manager = urllib3.PoolManager()
        response: urllib3.response.HTTPResponse = manager.request('GET', cls.remote_url, preload_content=False)
        if response.status != 200:
            print("Download failed!")
            return False
        file_size = int(response.headers['Content-Length'])

        downloaded: int = 0
        last_print: time = time.time()
        with open(save_path, 'wb') as fp:
            for chunk in response.stream():
                downloaded += fp.write(chunk)
                now = time.time()
                if now - last_print >= 0.2:
                    cls.show_download_progress(downloaded=downloaded, file_size=file_size)
                    last_print = time.time()
            cls.show_download_progress(downloaded=file_size, file_size=file_size)
            response.release_conn()
        print("")
        return True

    @classmethod
    def show_download_progress(cls, downloaded: float, file_size: int):
        progress: float = downloaded / file_size
        KB_size: int = 1024
        MB_size: int = 1024 * KB_size
        GB_size: int = 1024 * MB_size

        measure: str = ""
        file_size_show: int = 0
        if file_size > GB_size:
            file_size_show = file_size / GB_size
            measure = "GB"
        elif file_size > MB_size:
            file_size_show = file_size / MB_size
            measure = "MB"
        elif file_size > KB_size:
            file_size_show = file_size / KB_size
            measure = "KB"

        ch_total: int = 50
        progress_round: int = round(progress * ch_total)
        prg_a: str = "█" * progress_round
        prg_b: str = "░" * (ch_total - progress_round)

        tip: str = "\r" \
            + "Downloading... [%s%s]" % (prg_a, prg_b) \
            + " [%.2f %%] [%.2f %s / %.2f %s]" % (progress * 100, file_size_show * progress, measure, file_size_show, measure)
        print(tip, end="")

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
