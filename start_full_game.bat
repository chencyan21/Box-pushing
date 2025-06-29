@echo off
echo ========================================
echo    跳一跳游戏 - AI Agent 启动器
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.7+
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/4] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖包安装失败
    pause
    exit /b 1
)
echo ✅ 依赖包安装完成

echo.
echo [3/4] 启动AI Agent服务器...
echo 🚀 正在启动Python后端服务器...
echo 📡 服务器地址: http://localhost:5000
echo.
echo ⚠️  请保持此窗口打开，否则AI功能将无法使用
echo ⚠️  要停止服务器，请按 Ctrl+C
echo.

start "" "jump_game.html"
echo [4/4] 游戏已在浏览器中打开

echo.
echo ========================================
echo 🎮 游戏使用说明:
echo 1. 在游戏界面输入您的Gemini API Key
echo 2. 点击 "AI自动跳跃" 按钮体验AI功能
echo 3. 如需手动跳跃，输入力度后点击 "跳跃"
echo ========================================
echo.

python ai_agent.py
