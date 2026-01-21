import webview
import os
import json

class Api:
    def sync_to_steam(self, data_json):
        try:
            # 接收从蔡工具源拉取的原始清单列表
            manifests = json.loads(data_json)
            # 蔡工具指定的注入路径
            path = os.path.join(os.getenv('APPDATA'), "SteamTools", "Manifests")
            if not os.path.exists(path): os.makedirs(path)

            for m in manifests:
                did, mid, key = str(m['did']), str(m['mid']), str(m.get('key', ''))
                # 严格遵守蔡工具写入格式：DepotID\nManifestID\nKey
                with open(os.path.join(path, f"{did}.manifest"), "w", encoding="utf-8") as f:
                    f.write(f"DepotID: {did}\nManifestID: {mid}\nKey: {key}\n")
            
            return f"✅ 同步成功！已注入 {len(manifests)} 个文件。请重启 Steam。"
        except Exception as e:
            return f"❌ 致命错误: {str(e)}"

def start():
    # 纯净外壳，不带多余逻辑
    webview.create_window('Steam 全库一键同步', 'index.html', js_api=Api(), width=400, height=480)
    webview.start()

if __name__ == '__main__':
    start()
