@echo off
chcp 65001 >nul
echo ========================================
echo   Desktop Pet - 一键打包脚本
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python 3.8+
    pause
    exit /b 1
)
echo OK
echo.

echo [2/4] 安装依赖...
pip install -r requirements.txt
echo.

echo [3/4] 处理图片背景...
python process_images.py
echo.

echo [4/4] 打包EXE...
pyinstaller desktop_pet.spec --clean
echo.

echo ========================================
echo   打包完成！
echo   输出: dist\DesktopPet.exe
echo ========================================
pause
