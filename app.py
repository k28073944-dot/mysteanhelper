import webview
import requests
import os
import json

# 蔡工具最核心的三个数据存放地址（使用镜像加速）
SOURCES = [
    "https://fastly.jsdelivr.net/gh/pvzcxw/cai-install_stloader@main/data.json",
    "https://fastly.jsdelivr.net/gh/pvzcxw/Cai-install-Web-GUI@main/data/games.json",
    "https://fastly.jsdelivr.net/gh/pvzcxw/Cai-install-Web-GUI@main/data/manifest_db.json"
]

class Api:
    def __init__(self):
        self.cache_db = {}

    def load_database(self):
        """启动时预加载，确保连接畅通"""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        for url in SOURCES:
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    self.cache_db.update(res.json())
            except:
                continue
        return len(self.cache_db)

    def run_unlock(self, app_id):
        """执行入库核心逻辑"""
        try:
            target_id = str(app_id).strip()
            
            # 1. 检查本地缓存库
            if not self.cache_db:
                self.load_database()
            
            game_data = self.cache_db.get(target_id)
            if not game_data:
                return f"❌ 搜遍了所有库，都没找到 AppID: {target_id}"

            # 2. 定位 SteamTools 清单目录
            # 路径通常是: C:/Users/用户名/AppData/Roaming/SteamTools/Manifests
            st_path = os.path.join(os.getenv('APPDATA'), "SteamTools", "Manifests")
            if not os.path.exists(st_path):
                os.makedirs(st_path)

            # 3. 提取清单并写入 (下载秘钥过程)
            depots = game_data.get('depots', [])
            if not depots:
                return "❌ 该游戏数据不完整，没有清单信息。"

            for d in depots:
                did = d.get('depot_id')
                mid = d.get('manifest_id')
                key = d.get('key')
                
                if did and mid:
                    # 构造文件
                    file_name = f"{did}.manifest"
                    file_path = os.path.join(st_path, file_name)
                    # 写入 SteamTools 标准格式
                    content = f"DepotID: {did}\nManifestID: {mid}\nKey: {key}\n"
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

            game_name = game_data.get('name', '未知游戏')
            return f"✅ 入库成功！\n游戏：{game_name}\n清单：已写入 {len(depots)} 个文件\n操作：请完全退出并重启 Steam。"

        except Exception as e:
            return f"程序出错: {str(e)}"

def start():
    api = Api()
    # 启动后台预加载
    api.load_database()
    window = webview.create_window(
        'Steam 极简入库助手 (测试版)', 
        'index.html', 
        js_api=api,
        width=420,
        height=400,
        resizable=False
    )
    webview.start()

if __name__ == '__main__':
    start()
