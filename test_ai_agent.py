"""
AI Agent 测试脚本
用于验证AI Agent服务器是否正常工作
"""

import requests
import json
import time
import os
# 服务器配置
API_BASE = "http://localhost:5000/api"
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

def test_health():
    """测试服务器健康状态"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 服务器健康检查通过")
            print(f"   AI启用状态: {data.get('ai_enabled', False)}")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False


def test_recommendation():
    """测试推荐功能（不需要API Key的物理计算模式）"""
    try:
        test_data = {
            "player_pos": [100, 300],
            "target_platform": [250, 280, 350],
            "physics_params": [0.15, -0.25, 0.5],
        }

        response = requests.post(
            f"{API_BASE}/get_recommendation", json=test_data, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                power = data.get("recommended_power")
                using_ai = data.get("using_ai", False)
                mode = "AI模式" if using_ai else "物理计算模式"
                print(f"✅ 推荐功能测试通过")
                print(f"   推荐力度: {power}")
                print(f"   计算模式: {mode}")
                return True
            else:
                print(f"❌ 推荐失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 推荐测试失败: {e}")
        return False


def main():
    print("🧪 AI Agent 测试开始")
    print("=" * 40)

    # 测试1: 健康检查
    print("\n[测试1] 服务器健康检查...")
    health_ok = test_health()

    if not health_ok:
        print("\n❌ 服务器未启动或无法访问")
        print("请确保运行了: python ai_agent.py")
        return

    # 测试2: 推荐功能
    print("\n[测试2] 推荐功能测试...")
    rec_ok = test_recommendation()

    # 总结
    print("\n" + "=" * 40)
    if health_ok and rec_ok:
        print("🎉 所有测试通过！AI Agent 工作正常")
        print("\n💡 提示:")
        print("   - 可以在游戏中输入API Key启用AI模式")
        print("   - 即使没有API Key，也可以使用物理计算模式")
    else:
        print("⚠️  部分测试失败，请检查服务器状态")


if __name__ == "__main__":
    main()
