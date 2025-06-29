"""
跳一跳游戏 - 结果分析脚本
分析批量测试的结果，生成图表和统计报告
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import statistics

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False


class ResultAnalyzer:
    def __init__(self, detailed_log_file="ai_detailed_log.json"):
        self.log_file = detailed_log_file
        self.data = None

    def load_data(self):
        """加载测试数据"""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            print(f"✅ 成功加载数据: {len(self.data['results'])} 场游戏")
            return True
        except FileNotFoundError:
            print(f"❌ 找不到文件: {self.log_file}")
            print("请先运行 batch_ai_test.py 生成测试数据")
            return False
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return False

    def generate_score_distribution_chart(self):
        """生成得分分布图"""
        if not self.data:
            return

        scores = [r["score"] for r in self.data["results"]]

        plt.figure(figsize=(12, 8))

        # 子图1: 得分直方图
        plt.subplot(2, 2, 1)
        plt.hist(scores, bins=20, alpha=0.7, color="skyblue", edgecolor="black")
        plt.title("得分分布直方图")
        plt.xlabel("得分")
        plt.ylabel("游戏数量")
        plt.grid(True, alpha=0.3)

        # 子图2: 得分趋势图
        plt.subplot(2, 2, 2)
        game_ids = [r["game_id"] for r in self.data["results"]]
        plt.plot(game_ids, scores, "o-", alpha=0.7, markersize=3)
        plt.title("得分趋势图")
        plt.xlabel("游戏序号")
        plt.ylabel("得分")
        plt.grid(True, alpha=0.3)

        # 子图3: 箱线图
        plt.subplot(2, 2, 3)
        plt.boxplot(scores)
        plt.title("得分箱线图")
        plt.ylabel("得分")
        plt.grid(True, alpha=0.3)

        # 子图4: 得分区间统计
        plt.subplot(2, 2, 4)
        score_ranges = {
            "0-50": len([s for s in scores if 0 <= s <= 50]),
            "51-100": len([s for s in scores if 51 <= s <= 100]),
            "101-200": len([s for s in scores if 101 <= s <= 200]),
            "201+": len([s for s in scores if s > 200]),
        }

        ranges = list(score_ranges.keys())
        counts = list(score_ranges.values())
        colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"]

        plt.pie(counts, labels=ranges, autopct="%1.1f%%", colors=colors, startangle=90)
        plt.title("得分区间分布")

        plt.tight_layout()
        plt.savefig("score_analysis.png", dpi=300, bbox_inches="tight")
        plt.show()
        print("📊 得分分析图表已保存: score_analysis.png")

    def generate_jump_analysis_chart(self):
        """生成跳跃分析图"""
        if not self.data:
            return

        # 提取跳跃数据
        all_jumps = []
        for game in self.data["results"]:
            for jump in game["jumps"]:
                jump["game_id"] = game["game_id"]
                all_jumps.append(jump)

        powers = [j["recommended_power"] for j in all_jumps]
        successes = [j["success"] for j in all_jumps]
        success_rate_by_power = {}

        # 按力度区间统计成功率
        for power_range in range(0, 101, 10):
            range_powers = [p for p in powers if power_range <= p < power_range + 10]
            range_successes = [
                successes[i]
                for i, p in enumerate(powers)
                if power_range <= p < power_range + 10
            ]

            if range_successes:
                success_rate_by_power[f"{power_range}-{power_range+9}"] = sum(
                    range_successes
                ) / len(range_successes)

        plt.figure(figsize=(15, 10))

        # 子图1: 推荐力度分布
        plt.subplot(2, 3, 1)
        plt.hist(powers, bins=20, alpha=0.7, color="lightgreen", edgecolor="black")
        plt.title("AI推荐力度分布")
        plt.xlabel("推荐力度")
        plt.ylabel("次数")
        plt.grid(True, alpha=0.3)

        # 子图2: 成功率vs推荐力度
        plt.subplot(2, 3, 2)
        power_ranges = list(success_rate_by_power.keys())
        success_rates = list(success_rate_by_power.values())
        plt.bar(range(len(power_ranges)), success_rates, alpha=0.7, color="orange")
        plt.title("不同力度区间的成功率")
        plt.xlabel("力度区间")
        plt.ylabel("成功率")
        plt.xticks(range(len(power_ranges)), power_ranges, rotation=45)
        plt.grid(True, alpha=0.3)

        # 子图3: 每场游戏的跳跃次数
        plt.subplot(2, 3, 3)
        jump_counts = [len(g["jumps"]) for g in self.data["results"]]
        plt.hist(jump_counts, bins=15, alpha=0.7, color="lightcoral", edgecolor="black")
        plt.title("每场游戏跳跃次数分布")
        plt.xlabel("跳跃次数")
        plt.ylabel("游戏数量")
        plt.grid(True, alpha=0.3)

        # 子图4: 成功跳跃vs失败跳跃
        plt.subplot(2, 3, 4)
        total_successes = sum(successes)
        total_failures = len(successes) - total_successes
        plt.pie(
            [total_successes, total_failures],
            labels=["成功", "失败"],
            autopct="%1.1f%%",
            colors=["#90EE90", "#FFB6C1"],
            startangle=90,
        )
        plt.title("总体跳跃成功率")

        # 子图5: 游戏长度趋势
        plt.subplot(2, 3, 5)
        game_ids = [g["game_id"] for g in self.data["results"]]
        plt.plot(game_ids, jump_counts, "o-", alpha=0.7, markersize=3)
        plt.title("游戏长度趋势")
        plt.xlabel("游戏序号")
        plt.ylabel("跳跃次数")
        plt.grid(True, alpha=0.3)

        # 子图6: 力度vs距离散点图
        plt.subplot(2, 3, 6)
        distances = []
        for jump in all_jumps:
            px, py = jump["player_pos"]
            tx = (jump["target_platform"][0] + jump["target_platform"][2]) / 2
            distance = abs(tx - px)
            distances.append(distance)

        plt.scatter(distances, powers, alpha=0.5, s=10)
        plt.title("推荐力度 vs 目标距离")
        plt.xlabel("目标距离")
        plt.ylabel("推荐力度")
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("jump_analysis.png", dpi=300, bbox_inches="tight")
        plt.show()
        print("📊 跳跃分析图表已保存: jump_analysis.png")

    def generate_performance_report(self):
        """生成性能报告"""
        if not self.data:
            return

        results = self.data["results"]

        # 基础统计
        scores = [r["score"] for r in results]
        jumps_counts = [r["jumps_count"] for r in results]
        success_rates = [r["success_rate"] for r in results]

        # 计算各种指标
        report = {
            "basic_stats": {
                "total_games": len(results),
                "ai_mode": results[0]["ai_mode"],
                "test_time": self.data["timestamp"],
            },
            "score_stats": {
                "mean": statistics.mean(scores),
                "median": statistics.median(scores),
                "std": statistics.stdev(scores) if len(scores) > 1 else 0,
                "min": min(scores),
                "max": max(scores),
                "q1": np.percentile(scores, 25),
                "q3": np.percentile(scores, 75),
            },
            "jump_stats": {
                "mean_jumps": statistics.mean(jumps_counts),
                "median_jumps": statistics.median(jumps_counts),
                "max_jumps": max(jumps_counts),
                "min_jumps": min(jumps_counts),
            },
            "success_stats": {
                "overall_success_rate": statistics.mean(success_rates),
                "best_success_rate": max(success_rates),
                "worst_success_rate": min(success_rates),
            },
        }

        # 保存报告
        with open("performance_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 生成文本报告
        with open("performance_report.txt", "w", encoding="utf-8") as f:
            f.write("🎮 跳一跳游戏 AI性能报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"测试时间: {report['basic_stats']['test_time']}\n")
            f.write(f"游戏总数: {report['basic_stats']['total_games']}\n")
            f.write(
                f"AI模式: {'启用' if report['basic_stats']['ai_mode'] else '物理计算'}\n\n"
            )

            f.write("📊 得分统计:\n")
            f.write(f"  平均得分: {report['score_stats']['mean']:.1f}\n")
            f.write(f"  中位数得分: {report['score_stats']['median']:.1f}\n")
            f.write(f"  标准差: {report['score_stats']['std']:.1f}\n")
            f.write(f"  最高得分: {report['score_stats']['max']}\n")
            f.write(f"  最低得分: {report['score_stats']['min']}\n")
            f.write(f"  25%分位数: {report['score_stats']['q1']:.1f}\n")
            f.write(f"  75%分位数: {report['score_stats']['q3']:.1f}\n\n")

            f.write("🎯 跳跃统计:\n")
            f.write(f"  平均跳跃次数: {report['jump_stats']['mean_jumps']:.1f}\n")
            f.write(f"  中位数跳跃次数: {report['jump_stats']['median_jumps']:.1f}\n")
            f.write(f"  最多跳跃次数: {report['jump_stats']['max_jumps']}\n")
            f.write(f"  最少跳跃次数: {report['jump_stats']['min_jumps']}\n\n")

            f.write("✅ 成功率统计:\n")
            f.write(
                f"  总体成功率: {report['success_stats']['overall_success_rate']:.2%}\n"
            )
            f.write(
                f"  最佳成功率: {report['success_stats']['best_success_rate']:.2%}\n"
            )
            f.write(
                f"  最差成功率: {report['success_stats']['worst_success_rate']:.2%}\n"
            )

        print("📋 性能报告已生成:")
        print("   - performance_report.json (详细数据)")
        print("   - performance_report.txt (文本报告)")

        return report

    def run_analysis(self):
        """运行完整分析"""
        print("📈 开始分析测试结果...")

        if not self.load_data():
            return

        print(f"🎮 分析 {len(self.data['results'])} 场游戏的数据")
        print(
            f"🤖 AI模式: {'启用' if self.data['results'][0]['ai_mode'] else '物理计算'}"
        )
        print()

        # 生成各种分析
        self.generate_score_distribution_chart()
        self.generate_jump_analysis_chart()
        report = self.generate_performance_report()

        print("\n🎉 分析完成!")
        print("📊 生成的文件:")
        print("   - score_analysis.png (得分分析图)")
        print("   - jump_analysis.png (跳跃分析图)")
        print("   - performance_report.json (性能数据)")
        print("   - performance_report.txt (性能报告)")


if __name__ == "__main__":
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("❌ 需要安装额外依赖:")
        print("   pip install matplotlib numpy")
        exit(1)

    analyzer = ResultAnalyzer()
    analyzer.run_analysis()
