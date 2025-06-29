# 跳一跳AI批量测试系统使用指南

## 概述
这是一个全功能的跳一跳游戏AI测试系统，支持批量自动游戏测试、AI推荐算法评估和结果分析。

## 核心文件说明

### 1. `batch_ai_test.py` - 批量测试脚本
**核心功能**：让AI进行多次游戏，记录和分析表现

**配置参数**（文件顶部）：
```python
GEMINI_API_KEY = "your_api_key_here"  # 设置您的Gemini API Key
AI_AGENT_URL = "http://localhost:5000"  # AI Agent服务地址
TOTAL_GAMES = 50  # 总游戏次数
USE_AI_MODE = True  # True=使用AI推荐, False=仅使用物理计算
```

**使用方法**：
1. 在文件顶部设置您的Gemini API Key
2. 确保AI Agent服务已启动（运行`python ai_agent.py`）
3. 运行：`python batch_ai_test.py`

### 2. `ai_agent.py` - AI推荐服务
**功能**：提供HTTP API接口，支持AI推荐和物理计算双模式

**启动方法**：`python ai_agent.py`
**服务地址**：http://localhost:5000

### 3. `jump_game.html` - 游戏前端界面
**功能**：交互式游戏界面，支持手动游戏和AI推荐

**使用方法**：直接在浏览器中打开

### 4. 结果分析工具

#### `simple_viewer.py` - 快速结果查看器
- 无需额外依赖
- 快速查看测试结果统计
- 显示最佳/最差游戏表现
- 使用：`python simple_viewer.py`

#### `analyze_results.py` - 详细分析器
- 需要matplotlib依赖
- 生成可视化图表
- 详细性能分析报告
- 使用：`python analyze_results.py`

## 快速开始

### 方法一：一键启动（推荐）
```bash
# 1. 安装依赖
install_dependencies.bat

# 2. 启动完整系统
start_full_game.bat

# 3. 运行批量测试
run_batch_test.bat
```

### 方法二：手动启动
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动AI服务
python ai_agent.py

# 3. 设置API Key并运行批量测试
# 编辑 batch_ai_test.py 设置 GEMINI_API_KEY
python batch_ai_test.py

# 4. 查看结果
python simple_viewer.py
python analyze_results.py
```

## 输出文件说明

### 批量测试输出
- `ai_game_results_YYYYMMDD_HHMMSS.txt` - 简要文本报告
- `ai_detailed_log_YYYYMMDD_HHMMSS.json` - 详细JSON日志

### 分析结果输出
- `analysis_report_YYYYMMDD_HHMMSS.txt` - 分析报告
- `success_rate_comparison.png` - 成功率对比图
- `accuracy_distribution.png` - 精度分布图
- `power_distribution.png` - 推荐力度分布图
- `performance_trend.png` - 性能趋势图

## 配置选项

### AI模式 vs 物理计算模式
- **AI模式**：使用Gemini AI进行智能推荐
- **物理计算模式**：使用简单物理公式计算

### 游戏物理参数详解

```python
# 物理运动参数
GRAVITY = 0.5           # 重力加速度 - 每帧垂直速度增量
VX_MULTIPLIER = 2.0     # 水平速度倍率 - 控制水平飞行距离
VY_MULTIPLIER = -3.0    # 垂直速度倍率 - 控制跳跃高度（负值向上）

# 游戏对象尺寸
PLAYER_SIZE = 30        # 玩家角色大小（像素）
PLATFORM_HEIGHT = 20    # 平台高度（像素）
PLATFORM_WIDTH = 100    # 平台宽度（像素）
```

**参数含义解释**：

- **GRAVITY (重力)**：每个时间步长内垂直速度的增量，模拟重力效果
- **VX_MULTIPLIER (水平倍率)**：跳跃力度转换为水平速度的系数
  - 计算：水平速度 = 力度 × VX_MULTIPLIER
- **VY_MULTIPLIER (垂直倍率)**：跳跃力度转换为垂直速度的系数
  - 计算：垂直速度 = 力度 × VY_MULTIPLIER（负值表示向上）

**运动公式**：
```
每帧更新：
x = x + vx          # 水平匀速运动
y = y + vy          # 垂直位置更新
vy = vy + GRAVITY   # 垂直速度受重力影响
```

## 常见问题

### Q: 如何获取Gemini API Key？
A: 访问 https://makersuite.google.com/app/apikey 申请

### Q: AI服务连接失败怎么办？
A: 确保先运行 `python ai_agent.py` 启动AI服务

### Q: 批量测试运行很慢？
A: 可以减少TOTAL_GAMES数量或调整API调用延迟

### Q: 没有生成图表？
A: 安装matplotlib：`pip install matplotlib`

### Q: 如何修改测试参数？
A: 编辑 `batch_ai_test.py` 文件顶部的配置区域

## 系统架构

```
前端界面 (jump_game.html)
    ↓ HTTP API
AI服务 (ai_agent.py) ← 批量测试 (batch_ai_test.py)
    ↓ Gemini API
Google AI服务
    ↓ 结果输出
分析工具 (simple_viewer.py / analyze_results.py)
```

## 技术栈
- **前端**：HTML5 Canvas + JavaScript
- **后端**：Python Flask + Google Generative AI
- **数据分析**：Python + Matplotlib
- **通信协议**：HTTP REST API

## 扩展建议
1. 支持更多AI模型（Claude、GPT等）
2. 增加更复杂的游戏场景
3. 实现在线排行榜功能
4. 添加AI训练和优化功能
5. 支持多人同时测试

---
**提示**：首次运行建议使用较小的TOTAL_GAMES值（如10-20）进行测试，确认系统正常后再增加测试轮数。
