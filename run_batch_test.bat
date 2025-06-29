@echo off
echo ========================================
echo    跳一跳游戏 - AI批量测试启动器
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.7+
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/3] 安装依赖包...
pip install google-generativeai matplotlib numpy >nul 2>&1
if errorlevel 1 (
    echo ⚠️  部分依赖安装可能失败，继续运行...
) else (
    echo ✅ 依赖包检查完成
)

echo.
echo [3/3] 运行批量测试...
echo.
echo ⚠️  注意事项:
echo    1. 请在 batch_ai_test.py 文件顶部设置您的 Gemini API Key
echo    2. 测试可能需要较长时间，请耐心等待
echo    3. 测试结果将保存在当前目录下
echo.

set /p confirm="是否开始批量测试? (y/n): "
if /i "%confirm%" neq "y" (
    echo 测试已取消
    pause
    exit /b 0
)

echo.
echo 🚀 开始AI批量测试...
echo.

python batch_ai_test.py

echo.
echo ========================================
echo 📊 是否运行结果分析?
echo ========================================
set /p analyze="是否生成分析图表和报告? (y/n): "
if /i "%analyze%" equ "y" (
    echo.
    echo 📈 生成分析报告...
    python analyze_results.py
)

echo.
echo 🎉 批量测试完成!
echo 📁 结果文件:
echo    - ai_game_results.txt (简要结果)
echo    - ai_detailed_log.json (详细日志)
if /i "%analyze%" equ "y" (
    echo    - score_analysis.png (得分分析图)
    echo    - jump_analysis.png (跳跃分析图)
    echo    - performance_report.txt (性能报告)
)
echo.
pause
