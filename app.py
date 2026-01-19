import webview
import requests
import os
import json

class Api:
    def run_unlock(self, app_id):
        target_id = str(app_id).strip()
        if not target_id: return "❌ 请输入 ID"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # --- 核心：100% 还原蔡工具的路径算法 ---
        # 1245620 -> prefix 就是 12
        prefix = target_id[:2] if len(target_id) > 2 else "0"
        
        # 蔡工具源码里定义的顶级进货源（对齐他的 CDN 镜像）
        sources = [
            # 1. 蔡的整合索引库 (agg 类型)
            {"name": "Cysaw/StLoader", "type": "agg", "url": "https://cdn.jsdmirror.com/gh/pvzcxw/cai-install_stloader@main/data.json"},
            
            # 2. Github-1 (Auiowu) - 这里的结构是 flat
            {"name": "Github-1 (Auiowu)", "type": "raw", "url": f"https://cdn.jsdmirror.com/gh/Auiowu/ManifestAutoUpdate@master/manifests/{target_id}.json"},
            
            # 3. Github-2/3 (SAC/Furcate) - 这里必须用分片路径算法 {prefix}/{id}.json
            {"name": "Github-2 (SAC)", "type": "raw", "url": f"https://cdn.jsdmirror.com/gh/SteamAutoCracks/ManifestHub@main/data/{prefix}/{target_id}.json"},
            {"name": "Github-3 (Furcate/SWA)", "type": "raw", "url": f"https://cdn.jsdmirror.com/gh/SteamManifestArchives/ManifestHub@main/data/{prefix}/{target_id}.json"}
        ]

        game_data = None
        hit_source = ""

        # 执行蔡工具同款轮询
        for src in sources:
            try:
                res = requests.get(src["url"], headers=headers, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    # 如果是聚合库，从里面捞 ID
                    if src["type"] == "agg":
                        if target_id in data:
                            game_data = data[target_id]
                            hit_source = src["name"]
                            break
                    # 如果是原始库，下载下来的直接就是该游戏数据
                    else:
                        game_data = data
                        hit_source = src["name"]
                        break
            except:
                continue

        if not game_data:
            return f"❌ 找不到 ID: {target_id}。\n(算法已对齐蔡工具，若仍找不到说明该 ID 暂无公开秘钥)"

        # --- 写入 SteamTools ---
        try:
            st_path = os.path.join(os.getenv('APPDATA'), "SteamTools", "Manifests")
            if not os.path.exists(st_path): os.makedirs(st_path)

            # 蔡工具的 JSON 兼容层：处理列表和字典两种格式
            depots = []
            if isinstance(game_data, dict):
                if 'depots' in game_data:
                    depots = game_data['depots']
                else:
                    # 针对 Furcate 这种 {"depotID": {"manifest": "...", "key": "..."}} 的解析
                    for d_id, info in game_data.items():
                        if isinstance(info, dict) and ('manifest' in info or 'manifest_id' in info):
                            depots.append({
                                'depot_id': d_id,
                                'manifest_id': info.get('manifest') or info.get('manifest_id'),
                                'key': info.get('key', '')
                            })

            for d in depots:
                if d.get('depot_id') and (d.get('manifest_id') or d.get('manifest')):
                    f_path = os.path.join(st_path, f"{d['depot_id']}.manifest")
                    m_id = d.get('manifest_id') or d.get('manifest')
                    with open(f_path, "w", encoding="utf-8") as f:
                        f.write(f"DepotID: {d['depot_id']}\nManifestID: {m_id}\nKey: {d.get('key', '')}\n")

            return f"✅ 成功复刻蔡工具逻辑！\n来源：{hit_source}\n注入清单：{len(depots)} 个文件。"
        except Exception as e:
            return f"❌ 写入失败: {str(e)}"

# start 代码保持不变
