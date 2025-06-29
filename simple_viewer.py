"""
跳一跳游戏 - 简化结果查看器
不依赖matplotlib，生成文本格式的分析报告
"""

import json
import statistics
from datetime import datetime


class SimpleResultViewer:
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

    def generate_text_charts(self, values, title, width=50):
        """生成简单的文本图表"""
        if not values:
            return f"{title}: 无数据"

        min_val = min(values)
        max_val = max(values)

        if max_val == min_val:
            return f"{title}: 所有值都是 {min_val}"

        # 创建直方图
        bins = 10
        bin_width = (max_val - min_val) / bins
        histogram = [0] * bins

        for value in values:
            bin_index = min(int((value - min_val) / bin_width), bins - 1)
            histogram[bin_index] += 1

        max_count = max(histogram)
        scale = width / max_count if max_count > 0 else 1

        chart = f"\n{title} 分布图:\n"
        chart += "=" * (width + 20) + "\n"

        for i, count in enumerate(histogram):
            start_val = min_val + i * bin_width
            end_val = start_val + bin_width
            bar_length = int(count * scale)
            bar = "█" * bar_length
            chart += f"{start_val:6.1f}-{end_val:6.1f} |{bar:<{width}} {count:3d}\n"

        chart += "=" * (width + 20) + "\n"
        return chart

    def analyze_scores(self):
        """分析得分数据"""
        if not self.data:
            return

        scores = [r["score"] for r in self.data["results"]]

        print("\n📊 得分分析")
        print("=" * 60)

        # 基础统计
        print(f"总游戏数: {len(scores)}")
        print(f"平均得分: {statistics.mean(scores):.1f}")
        print(f"中位数得分: {statistics.median(scores):.1f}")
        print(f"最高得分: {max(scores)}")
        print(f"最低得分: {min(scores)}")

        if len(scores) > 1:
            print(f"标准差: {statistics.stdev(scores):.1f}")

        # 分位数
        import numpy as np

        q1 = np.percentile(scores, 25)
        q3 = np.percentile(scores, 75)
        print(f"25%分位数: {q1:.1f}")
        print(f"75%分位数: {q3:.1f}")

        # 得分区间统计
        score_ranges = {
            "0-50": len([s for s in scores if 0 <= s <= 50]),
            "51-100": len([s for s in scores if 51 <= s <= 100]),
            "101-200": len([s for s in scores if 101 <= s <= 200]),
            "201+": len([s for s in scores if s > 200]),
        }

        print(f"\n得分区间分布:")
        for range_name, count in score_ranges.items():
            percentage = (count / len(scores)) * 100
            bar = "▓" * int(percentage / 2)
            print(f"  {range_name:>6}: {count:3d} 场 ({percentage:5.1f}%) {bar}")

        # 生成得分分布图
        print(self.generate_text_charts(scores, "得分"))

    def analyze_jumps(self):
        """分析跳跃数据"""
        if not self.data:
            return

        print("\n🎯 跳跃分析")
        print("=" * 60)

        # 提取跳跃数据
        all_jumps = []
        jump_counts = []

        for game in self.data["results"]:
            jump_counts.append(len(game["jumps"]))
            for jump in game["jumps"]:
                all_jumps.append(jump)

        powers = [j["recommended_power"] for j in all_jumps]
        successes = [j["success"] for j in all_jumps]

        print(f"总跳跃次数: {len(all_jumps)}")
        print(f"成功跳跃: {sum(successes)}")
        print(f"失败跳跃: {len(successes) - sum(successes)}")
        print(f"总体成功率: {sum(successes) / len(successes):.2%}")

        print(f"\n每场游戏跳跃次数:")
        print(f"  平均: {statistics.mean(jump_counts):.1f}")
        print(f"  中位数: {statistics.median(jump_counts):.1f}")
        print(f"  最多: {max(jump_counts)}")
        print(f"  最少: {min(jump_counts)}")

        # 推荐力度统计
        print(f"\nAI推荐力度:")
        print(f"  平均力度: {statistics.mean(powers):.1f}")
        print(f"  中位数力度: {statistics.median(powers):.1f}")
        print(f"  最大力度: {max(powers)}")
        print(f"  最小力度: {min(powers)}")

        # 按力度区间统计成功率
        print(f"\n不同力度区间的成功率:")
        for power_range in range(0, 101, 20):
            range_powers = [
                i for i, p in enumerate(powers) if power_range <= p < power_range + 20
            ]
            if range_powers:
                range_successes = [successes[i] for i in range_powers]
                success_rate = sum(range_successes) / len(range_successes)
                bar = "▓" * int(success_rate * 20)
                print(
                    f"  {power_range:2d}-{power_range+19:2d}: {success_rate:.2%} {bar}"
                )

        # 生成推荐力度分布图
        print(self.generate_text_charts(powers, "推荐力度"))

    def analyze_ai_performance(self):
        """分析AI性能"""
        if not self.data:
            return

        print("\n🤖 AI性能分析")
        print("=" * 60)

        ai_mode = self.data["results"][0]["ai_mode"] if self.data["results"] else False
        print(f"AI模式: {'启用' if ai_mode else '物理计算模式'}")

        # 游戏质量评估
        scores = [r["score"] for r in self.data["results"]]
        success_rates = [r["success_rate"] for r in self.data["results"]]

        # 高质量游戏定义: 得分 > 100 且成功率 > 80%
        high_quality_games = [
            r
            for r in self.data["results"]
            if r["score"] > 100 and r["success_rate"] > 0.8
        ]

        print(
            f"高质量游戏: {len(high_quality_games)}/{len(self.data['results'])} "
            f"({len(high_quality_games)/len(self.data['results']):.1%})"
        )

        # 稳定性分析
        if len(scores) > 1:
            cv_score = statistics.stdev(scores) / statistics.mean(scores)
            cv_success = statistics.stdev(success_rates) / statistics.mean(
                success_rates
            )
            print(
                f"得分变异系数: {cv_score:.3f} ({'稳定' if cv_score < 0.5 else '不稳定'})"
            )
            print(
                f"成功率变异系数: {cv_success:.3f} ({'稳定' if cv_success < 0.3 else '不稳定'})"
            )

        # 学习效果分析（前后对比）
        if len(scores) >= 10:
            first_half = scores[: len(scores) // 2]
            second_half = scores[len(scores) // 2 :]

            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            improvement = (second_avg - first_avg) / first_avg * 100

            print(f"\n学习效果分析:")
            print(f"  前半段平均得分: {first_avg:.1f}")
            print(f"  后半段平均得分: {second_avg:.1f}")
            print(f"  改进幅度: {improvement:+.1f}%")

            if improvement > 5:
                print("  🎉 显示出学习效果!")
            elif improvement < -5:
                print("  ⚠️  性能有所下降")
            else:
                print("  ➡️  性能基本稳定")

    def generate_summary_report(self):
        """生成总结报告"""
        if not self.data:
            return

        scores = [r["score"] for r in self.data["results"]]
        success_rates = [r["success_rate"] for r in self.data["results"]]

        # 评级系统
        avg_score = statistics.mean(scores)
        avg_success_rate = statistics.mean(success_rates)

        score_grade = (
            "优秀"
            if avg_score >= 150
            else "良好" if avg_score >= 100 else "一般" if avg_score >= 50 else "较差"
        )

        success_grade = (
            "优秀"
            if avg_success_rate >= 0.9
            else (
                "良好"
                if avg_success_rate >= 0.8
                else "一般" if avg_success_rate >= 0.7 else "较差"
            )
        )

        print("\n📋 总结报告")
        print("=" * 60)
        print(f"测试时间: {self.data['timestamp']}")
        print(f"游戏总数: {len(self.data['results'])}")
        print(f"AI模式: {'启用' if self.data['results'][0]['ai_mode'] else '物理计算'}")
        print(f"平均得分: {avg_score:.1f} ({score_grade})")
        print(f"平均成功率: {avg_success_rate:.1%} ({success_grade})")
        print(f"最高得分: {max(scores)}")

        # 综合评级
        if score_grade == "优秀" and success_grade == "优秀":
            overall_grade = "优秀"
            emoji = "🏆"
        elif score_grade in ["优秀", "良好"] and success_grade in ["优秀", "良好"]:
            overall_grade = "良好"
            emoji = "🥈"
        elif score_grade != "较差" or success_grade != "较差":
            overall_grade = "一般"
            emoji = "🥉"
        else:
            overall_grade = "需要改进"
            emoji = "📈"

        print(f"\n{emoji} 综合评级: {overall_grade}")

        # 保存简要报告
        with open("simple_report.txt", "w", encoding="utf-8") as f:
            f.write(f"跳一跳游戏 AI测试简要报告\n")
            f.write(f"测试时间: {self.data['timestamp']}\n")
            f.write(f"游戏总数: {len(self.data['results'])}\n")
            f.write(f"平均得分: {avg_score:.1f} ({score_grade})\n")
            f.write(f"平均成功率: {avg_success_rate:.1%} ({success_grade})\n")
            f.write(f"综合评级: {overall_grade}\n")

        print(f"\n💾 简要报告已保存: simple_report.txt")

    def run_analysis(self):
        """运行完整分析"""
        print("📈 跳一跳游戏 - 结果分析器")
        print("=" * 60)

        if not self.load_data():
            return

        try:
            import numpy as np
        except ImportError:
            print("⚠️  numpy未安装，部分功能受限")

        self.analyze_scores()
        self.analyze_jumps()
        self.analyze_ai_performance()
        self.generate_summary_report()

        print("\n🎉 分析完成!")


if __name__ == "__main__":
    viewer = SimpleResultViewer()
    viewer.run_analysis()
