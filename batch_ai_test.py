"""
跳一跳游戏 - AI批量测试脚本
通过AI Agent服务进行多次游戏，记录和分析结果
"""

# ====== 配置区域 ======
GEMINI_API_KEY = "your_api_key_here"  # 在这里设置您的Gemini API Key
AI_AGENT_URL = "http://localhost:5000"  # AI Agent服务地址
TOTAL_GAMES = 50  # 总游戏次数
USE_AI_MODE = True  # True=使用AI推荐, False=仅使用物理计算
OUTPUT_FILE = "ai_game_results.txt"  # 结果输出文件
DETAILED_LOG = "ai_detailed_log.json"  # 详细日志文件

import requests
import json
import time
import random
import math
from datetime import datetime
import statistics


class GameSimulator:
    def __init__(self, api_key=None, ai_agent_url=AI_AGENT_URL):
        # 游戏物理参数
        self.GRAVITY = 0.5
        self.VX_MULTIPLIER = 2.0
        self.VY_MULTIPLIER = -3.0
        self.PLAYER_SIZE = 30
        self.PLATFORM_HEIGHT = 20
        self.PLATFORM_WIDTH = 100
        self.CANVAS_WIDTH = 800
        self.CANVAS_HEIGHT = 600

        # AI Agent配置
        self.ai_agent_url = ai_agent_url
        self.api_key = api_key
        self.ai_enabled = False

        # 尝试连接AI Agent服务并设置API Key
        if self.check_ai_service():
            if api_key and api_key != "your_api_key_here":
                self.ai_enabled = self.set_api_key(api_key)
                if self.ai_enabled:
                    print("✅ AI模式已启用")
                else:
                    print("⚠️  API Key设置失败，使用物理计算模式")
            else:
                print("🔧 未设置API Key，使用物理计算模式")
        else:
            print("❌ 无法连接AI Agent服务，使用物理计算模式")

    def check_ai_service(self):
        """检查AI Agent服务是否可用"""
        try:
            response = requests.get(f"{self.ai_agent_url}/api/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def set_api_key(self, api_key):
        """设置API Key"""
        try:
            response = requests.post(
                f"{self.ai_agent_url}/api/set_api_key",
                json={"api_key": api_key},
                timeout=10,
            )
            return response.status_code == 200
        except Exception:
            return False

    def calculate_physics_recommendation(self, player_pos, target_platform):
        """基于物理计算的推荐算法"""
        px, py = player_pos
        plat_left, plat_top, plat_right = target_platform

        # 目标平台中心
        target_x = (plat_left + plat_right) / 2
        target_y = plat_top

        # 计算距离
        dx = target_x - px
        dy = target_y - py

        # 基础力度估算
        distance = math.sqrt(dx * dx + dy * dy)
        base_power = min(100, max(0, distance / 3))

        # 根据高度差调整
        if dy < 0:  # 需要向上跳
            height_adjustment = abs(dy) / 2
            base_power += height_adjustment
        else:  # 向下跳
            base_power -= dy / 4

        return max(0, min(100, int(base_power)))

    def get_ai_recommendation(self, player_pos, target_platform):
        """获取AI推荐的跳跃力度"""
        if not self.ai_enabled and USE_AI_MODE:
            # 如果要求使用AI但AI不可用，尝试使用物理计算
            return self.calculate_physics_recommendation(player_pos, target_platform)
        elif not USE_AI_MODE:
            # 如果明确要求使用物理计算模式
            return self.calculate_physics_recommendation(player_pos, target_platform)

        # 使用AI Agent服务获取推荐
        try:
            request_data = {
                "player_pos": list(player_pos),
                "target_platform": list(target_platform),
                "physics_params": [
                    self.VX_MULTIPLIER,
                    self.VY_MULTIPLIER,
                    self.GRAVITY,
                ],
            }

            response = requests.post(
                f"{self.ai_agent_url}/api/get_recommendation",
                json=request_data,
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("recommended_power", 50)
            else:
                print(f"AI推荐请求失败: {response.status_code}")
                return self.calculate_physics_recommendation(
                    player_pos, target_platform
                )

        except Exception as e:
            print(f"AI推荐失败: {e}")
            # 使用物理计算作为备用
            return self.calculate_physics_recommendation(player_pos, target_platform)

    def simulate_jump(self, power, player_pos, target_platform):
        """模拟跳跃过程，返回是否成功着陆"""
        px, py = player_pos
        plat_left, plat_top, plat_right = target_platform

        # 初始速度
        vx = power * self.VX_MULTIPLIER
        vy = power * self.VY_MULTIPLIER

        # 模拟物理运动
        x, y = px, py
        max_steps = 200  # 防止无限循环

        for step in range(max_steps):
            # 更新位置
            x += vx
            y += vy

            # 应用重力
            vy += self.GRAVITY

            # 检查是否掉出屏幕
            if y > self.CANVAS_HEIGHT + 50:
                return False, (x, y), step

            # 检查碰撞（仅在下落过程中）
            if vy > 0:
                player_left = x - self.PLAYER_SIZE / 2
                player_right = x + self.PLAYER_SIZE / 2
                player_bottom = y + self.PLAYER_SIZE / 2

                # 检查矩形重叠
                if (
                    player_right >= plat_left
                    and player_left <= plat_right
                    and player_bottom >= plat_top
                    and player_bottom <= plat_top + self.PLATFORM_HEIGHT
                ):

                    # 精细判定
                    vertical_distance = abs(player_bottom - plat_top)
                    horizontal_in_bounds = x >= plat_left and x <= plat_right

                    if vertical_distance <= 10 and horizontal_in_bounds:
                        return True, (x, plat_top - self.PLAYER_SIZE / 2), step

        return False, (x, y), max_steps

    def generate_platform(self, last_platform):
        """生成下一个平台"""
        min_distance = 80
        max_distance = 200
        distance = min_distance + random.random() * (max_distance - min_distance)

        return {
            "x": last_platform["x"] + distance,
            "y": 280 + random.random() * 80,  # 随机高度
            "width": self.PLATFORM_WIDTH,
            "height": self.PLATFORM_HEIGHT,
        }

    def play_single_game(self, game_id):
        """进行单次游戏"""
        # 初始化游戏状态
        player = {"x": 100, "y": 300}
        platforms = [
            {
                "x": 50,
                "y": 320,
                "width": self.PLATFORM_WIDTH,
                "height": self.PLATFORM_HEIGHT,
            }
        ]

        # 添加第一个目标平台
        platforms.append(self.generate_platform(platforms[0]))

        current_platform_index = 0
        score = 0
        jumps = []

        max_jumps = 100  # 防止无限循环

        for jump_count in range(max_jumps):
            target_platform = platforms[current_platform_index + 1]

            # 获取AI推荐
            player_pos = (player["x"], player["y"])
            target_pos = (
                target_platform["x"],
                target_platform["y"],
                target_platform["x"] + target_platform["width"],
            )

            recommended_power = self.get_ai_recommendation(player_pos, target_pos)

            # 模拟跳跃
            success, final_pos, steps = self.simulate_jump(
                recommended_power, player_pos, target_pos
            )

            jump_data = {
                "jump_number": jump_count + 1,
                "player_pos": player_pos,
                "target_platform": target_pos,
                "recommended_power": recommended_power,
                "success": success,
                "final_pos": final_pos,
                "steps": steps,
            }
            jumps.append(jump_data)

            if success:
                # 成功着陆
                player["x"], player["y"] = final_pos
                current_platform_index += 1
                score += 10

                # 生成新平台
                platforms.append(self.generate_platform(platforms[-1]))

                # 相机滚动效果
                if player["x"] > self.CANVAS_WIDTH / 2:
                    offset = player["x"] - self.CANVAS_WIDTH / 2
                    player["x"] = self.CANVAS_WIDTH / 2
                    for platform in platforms:
                        platform["x"] -= offset
            else:
                # 跳跃失败，游戏结束
                break

        return {
            "game_id": game_id,
            "score": score,
            "jumps_count": len(jumps),
            "success_rate": (
                sum(1 for jump in jumps if jump["success"]) / len(jumps) if jumps else 0
            ),
            "jumps": jumps,
            "ai_mode": self.ai_enabled,
        }


def run_batch_games():
    """运行批量游戏测试"""
    print("🎮 跳一跳游戏 - AI批量测试开始")
    print("=" * 50)
    print(f"📊 测试配置:")
    print(f"   总游戏数: {TOTAL_GAMES}")
    print(f"   AI模式: {'启用' if USE_AI_MODE else '仅物理计算'}")
    print(f"   AI服务地址: {AI_AGENT_URL}")
    print("=" * 50)

    # 初始化游戏模拟器
    simulator = GameSimulator(GEMINI_API_KEY)

    # 存储所有游戏结果
    all_results = []
    successful_games = 0

    start_time = time.time()

    for game_num in range(1, TOTAL_GAMES + 1):
        print(f"🎯 进行第 {game_num}/{TOTAL_GAMES} 场游戏...")

        try:
            result = simulator.play_single_game(game_num)
            all_results.append(result)

            if result["success_rate"] > 0:
                successful_games += 1

            print(
                f"   得分: {result['score']}, 跳跃次数: {result['jumps_count']}, "
                f"成功率: {result['success_rate']:.2%}, AI模式: {result['ai_mode']}"
            )

            # 每10轮显示总体进度
            if game_num % 10 == 0:
                current_success_rate = successful_games / game_num * 100
                print(
                    f"📈 进度: {game_num}/{TOTAL_GAMES} | 累计成功率: {current_success_rate:.1f}%"
                )

            # 短暂延迟，避免API调用过于频繁
            if simulator.ai_enabled:
                time.sleep(0.2)

        except Exception as e:
            print(f"   ❌ 游戏 {game_num} 失败: {e}")
            continue

    end_time = time.time()

    # 分析结果
    analyze_results(all_results, end_time - start_time)

    # 保存结果
    save_results(all_results)


def analyze_results(results, total_time):
    """分析游戏结果"""
    print("\n" + "=" * 50)
    print("📊 游戏结果分析")
    print("=" * 50)

    if not results:
        print("❌ 没有有效的游戏结果")
        return

    scores = [r["score"] for r in results]
    jumps_counts = [r["jumps_count"] for r in results]
    success_rates = [r["success_rate"] for r in results]

    print(f"🎮 总游戏数: {len(results)}")
    print(f"⏱️  总耗时: {total_time:.1f} 秒")
    print(f"🤖 AI模式: {'启用' if results[0]['ai_mode'] else '物理计算'}")
    print()

    print("📈 得分统计:")
    print(f"   平均得分: {statistics.mean(scores):.1f}")
    print(f"   最高得分: {max(scores)}")
    print(f"   最低得分: {min(scores)}")
    print(f"   得分中位数: {statistics.median(scores):.1f}")
    if len(scores) > 1:
        print(f"   得分标准差: {statistics.stdev(scores):.1f}")
    print()

    print("🎯 跳跃统计:")
    print(f"   平均跳跃次数: {statistics.mean(jumps_counts):.1f}")
    print(f"   最多跳跃次数: {max(jumps_counts)}")
    print(f"   最少跳跃次数: {min(jumps_counts)}")
    print()

    print("✅ 成功率统计:")
    print(f"   平均成功率: {statistics.mean(success_rates):.2%}")
    print(f"   最高成功率: {max(success_rates):.2%}")
    print(f"   最低成功率: {min(success_rates):.2%}")

    # 得分分布
    score_ranges = {
        "0-50": len([s for s in scores if 0 <= s <= 50]),
        "51-100": len([s for s in scores if 51 <= s <= 100]),
        "101-200": len([s for s in scores if 101 <= s <= 200]),
        "201+": len([s for s in scores if s > 200]),
    }

    print("\n📊 得分分布:")
    for range_name, count in score_ranges.items():
        percentage = (count / len(scores)) * 100
        print(f"   {range_name}: {count} 场 ({percentage:.1f}%)")


def save_results(results):
    """保存结果到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 动态生成文件名
    output_file = f"ai_game_results_{timestamp}.txt"
    detailed_log = f"ai_detailed_log_{timestamp}.json"

    # 保存简要结果到文本文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"跳一跳AI批量测试结果\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"测试配置:\n")
        f.write(f"  总游戏数: {len(results)}\n")
        f.write(f"  AI模式: {'启用' if USE_AI_MODE else '仅物理计算'}\n")
        f.write(f"  AI服务地址: {AI_AGENT_URL}\n")
        f.write(
            f"  Gemini API Key: {'已设置' if GEMINI_API_KEY != 'your_api_key_here' else '未设置'}\n\n"
        )

        # 统计摘要
        scores = [r["score"] for r in results]
        success_rates = [r["success_rate"] for r in results]
        successful_games = len([r for r in results if r["success_rate"] > 0])

        f.write(f"测试结果摘要:\n")
        f.write(
            f"  成功游戏数: {successful_games}/{len(results)} ({successful_games/len(results)*100:.1f}%)\n"
        )
        f.write(f"  平均得分: {statistics.mean(scores):.1f}\n")
        f.write(f"  最高得分: {max(scores)}\n")
        f.write(f"  最低得分: {min(scores)}\n")
        f.write(f"  平均成功率: {statistics.mean(success_rates):.2%}\n\n")

        # 详细游戏记录
        f.write(f"详细游戏记录:\n")
        f.write("-" * 50 + "\n")
        for result in results:
            f.write(f"游戏 {result['game_id']:3d}: ")
            f.write(f"得分={result['score']:3d}, ")
            f.write(f"跳跃={result['jumps_count']:2d}, ")
            f.write(f"成功率={result['success_rate']:.2%}, ")
            f.write(f"AI模式={'是' if result['ai_mode'] else '否'}\n")

    # 保存详细日志到JSON文件
    detailed_data = {
        "summary": {
            "timestamp": datetime.now().isoformat(),
            "total_games": len(results),
            "successful_games": len([r for r in results if r["success_rate"] > 0]),
            "use_ai_mode": USE_AI_MODE,
            "ai_agent_url": AI_AGENT_URL,
            "api_key_set": GEMINI_API_KEY != "your_api_key_here",
        },
        "config": {
            "gravity": GameSimulator(None).GRAVITY,
            "vx_multiplier": GameSimulator(None).VX_MULTIPLIER,
            "vy_multiplier": GameSimulator(None).VY_MULTIPLIER,
            "player_size": GameSimulator(None).PLAYER_SIZE,
            "platform_height": GameSimulator(None).PLATFORM_HEIGHT,
            "platform_width": GameSimulator(None).PLATFORM_WIDTH,
            "canvas_width": GameSimulator(None).CANVAS_WIDTH,
            "canvas_height": GameSimulator(None).CANVAS_HEIGHT,
        },
        "results": results,
    }

    with open(detailed_log, "w", encoding="utf-8") as f:
        json.dump(detailed_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 结果已保存:")
    print(f"   简要结果: {output_file}")
    print(f"   详细日志: {detailed_log}")

    return output_file, detailed_log


if __name__ == "__main__":
    print("=" * 60)
    print("🎮 跳一跳AI批量测试系统")
    print("=" * 60)

    # 检查AI Agent服务状态
    try:
        response = requests.get(f"{AI_AGENT_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ AI Agent服务已连接: {AI_AGENT_URL}")
        else:
            print(f"⚠️  AI Agent服务响应异常: {response.status_code}")
    except Exception:
        print(f"❌ 无法连接AI Agent服务: {AI_AGENT_URL}")
        print("💡 提示: 请先运行 'python ai_agent.py' 启动AI服务")

    # 检查API Key设置
    if GEMINI_API_KEY == "your_api_key_here":
        print("⚠️  未设置Gemini API Key - 将使用物理计算模式")
        print("💡 提示: 在文件顶部设置GEMINI_API_KEY可启用AI模式")
    else:
        print("✅ Gemini API Key已设置")

    print(f"\n📊 当前配置:")
    print(f"   测试轮数: {TOTAL_GAMES}")
    print(f"   AI模式: {'启用' if USE_AI_MODE else '仅物理计算'}")
    print(f"   服务地址: {AI_AGENT_URL}")

    print("\n" + "=" * 60)

    try:
        # 运行批量测试
        output_file, detailed_log = run_batch_games()

        print("\n🎉 批量测试完成!")
        print(f"\n📁 输出文件:")
        print(f"   📄 简要报告: {output_file}")
        print(f"   📋 详细日志: {detailed_log}")

        print(f"\n🔍 后续分析:")
        print(f"   运行 'python simple_viewer.py' 快速查看结果")
        print(f"   运行 'python analyze_results.py' 生成详细图表分析")

    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback

        traceback.print_exc()
