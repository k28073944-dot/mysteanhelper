import webview
import requests
import json

# 蔡工具的公开数据源
DATA_URL = "https://raw.githubusercontent.com/pvzcxw/Cai-install-Web-GUI/main/data/games.json"

class Api:
    def search_game(self, app_id):
        """核心逻辑：去公开库匹配 AppID"""
        try:
            # 获取蔡工具的完整数据库
            res = requests.get(DATA_URL, timeout=10)
            if res.status_code != 200:
                return "错误：无法连接到公开清单库"
            
            db = res.json()
            # 尝试在数据库里寻找这个 AppID
            game = db.get(str(app_id))
            
            if not game:
                return f"库中暂时没有 AppID: {app_id} 的清单数据"

            # 提取基本信息
            name = game.get('name', '未知游戏')
            depots = game.get('depots', [])
            
            # 格式化显示给用户看
            info = f"【找到游戏】: {name}\n"
            info += f"【包含 Depot 数量】: {len(depots)}\n"
            info += "\n状态：已获取清单，可以执行入库。"
            return info
            
        except Exception as e:
            return f"程序运行出错：{str(e)}"

def start():
    api = Api()
    # 创建一个窗口，加载我们即将创建的 index.html
    window = webview.create_window(
        '我的 Steam 入库助手', 
        'index.html', 
        js_api=api,
        width=500,
        height=400
    )
    webview.start()

if __name__ == '__main__':
    start()
