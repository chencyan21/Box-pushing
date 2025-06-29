import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import math

app = Flask(__name__)
CORS(app)  # 允许跨域请求
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

class JumpAIAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

    def set_api_key(self, api_key):
        """设置API Key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

    def calculate_physics_recommendation(
        self, player_pos, target_platform, physics_params
    ):
        """
        基于物理计算的简单推荐算法（备用方案）
        """
        px, py = player_pos
        plat_left, plat_top, plat_right = target_platform
        vx_mul, vy_mul, gravity = physics_params

        # 目标平台中心
        target_x = (plat_left + plat_right) / 2
        target_y = plat_top

        # 计算水平和垂直距离
        dx = target_x - px
        dy = target_y - py

        # 使用抛物线运动公式估算
        # 假设最优角度约为45度，调整力度
        distance = math.sqrt(dx * dx + dy * dy)

        # 基础力度估算
        base_power = min(100, max(0, distance / 3))

        # 根据高度差调整
        if dy < 0:  # 需要向上跳
            height_adjustment = abs(dy) / 2
            base_power += height_adjustment
        else:  # 向下跳
            base_power -= dy / 4
        print(
            f"[物理计算推荐] 玩家({px},{py}) -> 平台中心({target_x:.1f},{target_y:.1f})，"
            f"dx={dx:.1f}, dy={dy:.1f}, distance={distance:.1f}，推荐力度={base_power:.1f}"
        )
        return max(0, min(100, int(base_power)))

    def get_ai_recommendation(self, player_pos, target_platform, physics_params):
        """
        获取AI推荐的跳跃力度
        """
        # 检查API Key是否有效（简单验证）
        if (
            not self.api_key
            or len(self.api_key) < 10
            or self.api_key.startswith("test_")
        ):
            print("使用物理计算模式（API Key无效或未设置）")
            return self.calculate_physics_recommendation(
                player_pos, target_platform, physics_params
            )

        px, py = player_pos
        plat_left, plat_top, plat_right = target_platform
        vx_mul, vy_mul, gravity = physics_params

        prompt = f"""你是一个跳一跳游戏的AI助手。根据以下物理参数和游戏状态，计算出最佳的跳跃力度。

=== 游戏参数详解 ===

【坐标系统】
- 玩家位置: ({px}, {py})
  * X坐标：水平位置，数值越大越靠右
  * Y坐标：垂直位置，数值越大越靠下（屏幕坐标系）
  
- 目标平台位置: 左边界={plat_left}, 顶部={plat_top}, 右边界={plat_right}
  * 左边界(L)：平台的最左侧X坐标
  * 顶部(T)：平台的最上方Y坐标（着陆目标高度）
  * 右边界(R)：平台的最右侧X坐标
  * 平台宽度：{plat_right - plat_left}像素
  * 平台中心X坐标：{(plat_left + plat_right) / 2}

【物理运动参数】
- 横向速度倍率 vx_multiplier = {vx_mul}
  * 含义：跳跃力度转换为水平速度的系数
  * 计算：水平初始速度 = 跳跃力度 × {vx_mul}
  * 影响：数值越大，相同力度下水平飞行距离越远
  
- 纵向速度倍率 vy_multiplier = {vy_mul}
  * 含义：跳跃力度转换为垂直速度的系数
  * 计算：垂直初始速度 = 跳跃力度 × {vy_mul}
  * 特点：负值表示向上运动（与屏幕坐标系相反）
  * 影响：绝对值越大，相同力度下跳跃高度越高
  
- 重力加速度 gravity = {gravity}
  * 含义：每个时间步长内，垂直速度的增量
  * 作用：使玩家在空中时持续向下加速
  * 影响：数值越大，抛物线弧度越陡峭

【距离分析】
- 水平距离：{(plat_left + plat_right) / 2 - px:.1f}像素（正值=需向右跳，负值=需向左跳）
- 垂直距离：{plat_top - py:.1f}像素（正值=需向下跳，负值=需向上跳）
- 直线距离：{math.sqrt(((plat_left + plat_right) / 2 - px)**2 + (plat_top - py)**2):.1f}像素

【物理运动方程】
每个时间步长内：
1. 水平位置更新：x = x + vx（匀速运动）
2. 垂直位置更新：y = y + vy
3. 垂直速度更新：vy = vy + gravity（重力加速）

【成功条件】
玩家必须在垂直下降过程中，在Y坐标接近平台顶部({plat_top})时，
X坐标落在平台范围内[{plat_left}, {plat_right}]。

请根据抛物线运动轨迹计算最佳跳跃力度（0-100整数）。

只需要输出推荐的跳跃力度数字，不需要其他解释。"""

        try:
            # 使用更简单的错误处理，不使用signal（Windows兼容）
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1, max_output_tokens=50
                ),
            )

            ai_response = response.text.strip()

            # 提取数字
            import re
            print(f"AI响应: {ai_response}")
            power_match = re.search(r"\d+", ai_response)
            if power_match:
                recommended_power = int(power_match.group())
                if 0 <= recommended_power <= 100:
                    return recommended_power

            # 如果AI返回无效结果，使用物理计算备用
            return self.calculate_physics_recommendation(
                player_pos, target_platform, physics_params
            )

        except Exception as e:
            print(f"AI推荐失败: {e}")
            # 使用物理计算作为备用
            return self.calculate_physics_recommendation(
                player_pos, target_platform, physics_params
            )


# 全局AI Agent实例
ai_agent = JumpAIAgent()


@app.route("/api/set_api_key", methods=["POST"])
def set_api_key():
    """设置API Key"""
    try:
        data = request.json
        api_key = data.get("api_key")

        if not api_key:
            return jsonify({"error": "API Key不能为空"}), 400

        ai_agent.set_api_key(api_key)
        return jsonify({"status": "success", "message": "API Key设置成功"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_recommendation", methods=["POST"])
def get_recommendation():
    """获取跳跃力度推荐"""
    try:
        data = request.json

        # 验证必需参数
        required_fields = ["player_pos", "target_platform", "physics_params"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必需参数: {field}"}), 400

        player_pos = data["player_pos"]  # [px, py]
        target_platform = data["target_platform"]  # [left, top, right]
        physics_params = data["physics_params"]  # [vx_mul, vy_mul, gravity]

        # 获取AI推荐
        recommended_power = ai_agent.get_ai_recommendation(
            player_pos, target_platform, physics_params
        )

        return jsonify(
            {
                "status": "success",
                "recommended_power": recommended_power,
                "using_ai": bool(ai_agent.api_key),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy", "ai_enabled": bool(ai_agent.api_key)})


@app.route("/", methods=["GET"])
def index():
    """根路径，提供使用说明和服务状态"""
    ai_status = "未启用"
    if ai_agent.api_key:
        ai_status = "已启用"

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>跳一跳 AI Agent 服务器</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }}
            .container {{ 
                max-width: 700px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                backdrop-filter: blur(10px);
            }}
            h1 {{ color: #fff; text-align: center; margin-bottom: 30px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
            .status {{ 
                text-align: center; 
                padding: 20px; 
                background: rgba(76, 175, 80, 0.2); 
                border-radius: 10px; 
                margin: 20px 0;
                border: 2px solid #4CAF50;
            }}
            .api-list {{ 
                background: rgba(255,255,255,0.1); 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0; 
            }}
            .instruction {{ 
                background: rgba(33, 150, 243, 0.2); 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                border: 2px solid #2196F3;
            }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ 
                padding: 8px 0; 
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }}
            li:last-child {{ border-bottom: none; }}
            code {{ 
                background: rgba(0,0,0,0.3); 
                padding: 2px 6px; 
                border-radius: 4px; 
                font-family: 'Courier New', monospace;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(45deg, #FF6B6B, #FF8E53);
                color: white;
                padding: 12px 24px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                margin: 10px;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            .button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }}
            .ai-status {{
                font-weight: bold;
                color: {'#4CAF50' if ai_agent.api_key else '#FF9800'};
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 跳一跳 AI Agent 服务器</h1>
            
            <div class="status">
                <h2>✅ 服务器运行正常</h2>
                <p>AI状态: <span class="ai-status">{ai_status}</span></p>
                <p>端口: 5000</p>
            </div>
            
            <div class="instruction">
                <h3>📋 如何使用</h3>
                <p><strong>方法一：使用启动脚本（推荐）</strong></p>
                <p>双击运行 <code>start_full_game.bat</code> 自动启动完整系统</p>
                
                <p><strong>方法二：手动启动</strong></p>
                <ol style="list-style-type: decimal; padding-left: 20px;">
                    <li>在文件资源管理器中打开 <code>jump_game.html</code> 文件</li>
                    <li>在游戏界面输入您的 Gemini API Key</li>
                    <li>点击 "AI自动跳跃" 按钮体验AI功能</li>
                </ol>
            </div>
            
            <div class="api-list">
                <h3>🔗 API端点</h3>
                <ul>
                    <li><strong>POST</strong> /api/set_api_key - 设置Gemini API Key</li>
                    <li><strong>POST</strong> /api/get_recommendation - 获取跳跃推荐</li>
                    <li><strong>GET</strong> /api/health - 健康检查</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p>💡 提示：此页面显示表明AI Agent服务器正在正常运行</p>
                <p>🎯 要开始游戏，请打开 jump_game.html 文件</p>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/favicon.ico")
def favicon():
    """处理favicon请求，避免404错误"""
    return "", 204


if __name__ == "__main__":
    print("🚀 跳一跳 AI Agent 服务器启动中...")
    print("📡 服务器地址: http://localhost:5000")
    print("🤖 API端点:")
    print("   POST /api/set_api_key - 设置Gemini API Key")
    print("   POST /api/get_recommendation - 获取跳跃推荐")
    print("   GET  /api/health - 健康检查")
    print("=" * 50)
    print("💡 提示：")
    print("   - 直接访问 http://localhost:5000 查看使用说明")
    print("   - 要开始游戏，请打开 jump_game.html 文件")
    print("   - 或者使用 start_full_game.bat 一键启动")
    print("=" * 50)

    app.run(debug=True, host="0.0.0.0", port=5000)
