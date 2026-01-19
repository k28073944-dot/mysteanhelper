import webview
import requests
import os
import json

class Api:
    def run_unlock(self, app_id):
        target_id = str(app_id).strip()
        if not target_id: return "❌ 请输入有效的 AppID"
        
        # 模拟浏览器，防止被 GitHub 拦截
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # --- 完整对齐蔡工具的 10 个进货源 ---
        sources = [
            {"name": "Cysaw 主力库", "type": "agg", "url": "https://cdn.jsdmirror.com/gh/pvzcxw/Cai-install-Web-GUI@main/data/games.json"},
            {"name": "StLoader 库", "type": "agg", "url": "https://cdn.jsdmirror.com/gh/pvzcxw/cai-install_stloader@main/data.json"},
            {"name": "Github-1 (Auiowu)", "type": "raw", "url": "https://cdn.jsdmirror.com/gh/Auiowu/ManifestAutoUpdate@master/manifests/"},
            {"name": "Github-2 (SAC)", "type": "raw", "url": "https://cdn.jsdmirror.com/gh/SteamAutoCracks/ManifestHub@main/data/"},
            {"name": "Github-3 (Furcate/SWA)", "type": "raw", "url": "https://cdn.jsdmirror.com/gh/SteamManifestArchives/ManifestHub@main/data/"},
            {"name": "Onekey 适配库", "type": "raw", "url": "https://cdn.jsdmirror.com/gh/Onekey-Unlocker/onekey-unlocker@main/data/"},
            {"name": "Gitee 镜像", "type": "agg", "url": "https://gitee.com/pvzcxw/Cai-install-Web-GUI/raw/main/data/games.json"},
            {"name": "备份源 A", "type": "raw", "url": "https://cdn.jsdmirror.com/gh/SteamDB-Mirror/Manifests@main/data/"},
            {"name": "备份源 B", "type": "agg", "url": "https://fastly.jsdelivr.net/gh/pvzcxw/Cai-install-Web-GUI@main/data/manifest_db.json"},
            {"name": "备用 CDN 源", "type": "agg", "url": "https://cdn.jsdmirror.com/gh/pvzcxw/Cai-install-Web-GUI@main/data/games.json"}
        ]

        game_data = None
        hit_source = ""

        # 核心逻辑：自动轮询 10 个仓库
        for src in sources:
            try:
                # 拼接地址：聚合库直接请求，独立库拼 ID.json
                test_url = src["url"] if src["type"] == "agg" else f"{src['url']}{target_id}.json"
                print(f"尝试从 {src['name']} 获取数据...")
                
                res = requests.get(test_url, headers=headers, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    
                    # 聚合库（大 JSON）需要查 Key
                    if src["type"] == "agg":
                        if target_id in data:
                            game_data = data[target_id]
                            hit_source = src["name"]
                            break
                    # 独立库直接就是数据
                    else:
                        game_data = data
                        hit_source = src["name"]
                        break
            except:
                continue

        if not game_data:
            return f"❌ 搜遍了蔡工具的所有 10 个源都没找到 ID: {target_id}\n(可能该游戏尚未被收录)"

        # --- 写入 SteamTools 目录 ---
        try:
            st_path = os.path.join(os.getenv('APPDATA'), "SteamTools", "Manifests")
            if not os.path.exists(st_path):
                os.makedirs(st_path)

            # 解析 Depot 数据（兼容多种 JSON 嵌套格式）
            depots_to_write = []
            if isinstance(game_data, dict):
                if 'depots' in game_data:
                    depots_to_write = game_data['depots']
                else:
                    # 处理 Furcate/SWA 那种直接以 ID 为键的字典格式
                    for d_id, info in game_data.items():
                        if isinstance(info, dict) and 'manifest' in info:
                            depots_to_write.append({
                                'depot_id': d_id,
                                'manifest_id': info['manifest'],
                                'key': info.get('key', '')
                            })

            if not depots_to_write:
                return "❌ 找到游戏但清单数据为空，无法入库。"

            # 执行写入操作
            for d in depots_to_write:
                did, mid, key = d.get('depot_id'), d.get('manifest_id'), d.get('key')
                if did and mid:
                    file_path = os.path.join(st_path, f"{did}.manifest")
                    content = f"DepotID: {did}\nManifestID: {mid}\nKey: {key}\n"
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

            game_name = game_data.get('name', f"AppID {target_id}")
            return f"✅ 同步成功！\n游戏：{game_name}\n来源：{hit_source}\n清单：已注入 {len(depots_to_write)} 个文件。\n\n请重启 Steam 后直接点击安装。"

        except Exception as e:
            return f"❌ 写入文件时出错: {str(e)}"

def start():
    api = Api()
    webview.create_window(
        'Steam 全源入库神器 (蔡工具全量版)', 
        'index.html', 
        js_api=api, 
        width=420, 
        height=480
    )
    webview.start()

if __name__ == '__main__':
    start()
