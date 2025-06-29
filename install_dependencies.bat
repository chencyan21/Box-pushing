@echo off
echo ========================================
echo      环境安装脚本
echo ========================================
echo.

echo 正在安装必要的Python包...
echo.

echo [1/3] 更新pip...
python -m pip install --upgrade pip

echo.
echo [2/3] 安装Flask和相关依赖...
pip install flask==2.3.3
pip install flask-cors==4.0.0

echo.
echo [3/3] 安装Google Generative AI...
pip install google-generativeai==0.3.2

echo.
echo ========================================
echo ✅ 环境安装完成！
echo ========================================
echo.
echo 现在您可以运行 start_full_game.bat 来启动游戏
echo.
pause
