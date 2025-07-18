import sys
import logging
import importlib
from pathlib import Path

import extutils

_logger = logging.getLogger(__name__)

# 常量定义
ROOT_DIR: Path = Path(__file__).parent.parent.parent.resolve()
ENV_DIR: Path = ROOT_DIR / "ExternalEnvironment"
PYTHON_DIR: Path = ENV_DIR / "Python313" / "Windows"
PYTHON_EXE: Path = PYTHON_DIR / "python.exe"
SITE_PACKAGES_DIR: Path = PYTHON_DIR / "Lib" / "site-packages"
REQUIREMENTS_FILE: Path = ENV_DIR / "scripts" / "requirements.txt"

def check_modules():
    """检查所有必需的Python模块是否可用"""
    # 需要检查的模块列表（使用实际导入名称）
    required_modules = [
        "autogen",           # ag2
        "autogen.agentchat.contrib.gpt_assistant_agent",  # autogen-ext
        "pandas",
        "PyQt6",
        "PyQt6.QtWebEngineCore",  # PyQt6-WebEngine
        "cv2",                # opencv-python
        "cryptography"
    ]
    
    missing_modules = []
    
    for module_name in required_modules:
        try:
            # 尝试导入模块
            importlib.import_module(module_name)
        except ImportError as e:
            # 处理模块未找到的情况
            missing_modules.append(f"{module_name} (未安装: {str(e)}")
        except Exception as e:
            # 处理其他导入错误（如依赖问题、版本冲突等）
            missing_modules.append(f"{module_name} (导入失败: {str(e)}")
    
    return missing_modules

def install_python_dependencies() -> None:
    """安装Python依赖到指定目录

    异常:
        RuntimeError: 当依赖安装失败时抛出
    """
    try:
        # 验证requirements文件存在性
        if not extutils.check_file_exists(REQUIREMENTS_FILE):
            raise FileNotFoundError(f"Requirements file not found: {REQUIREMENTS_FILE}")

        # 创建目标目录
        extutils.create_directory(SITE_PACKAGES_DIR)

        _logger.info(f"[DEPLOY] Installing Python dependencies to {SITE_PACKAGES_DIR}")

        extutils.run_command(
            [
                str(PYTHON_EXE),
                "-m",
                "pip",
                "install",
                "-r",
                str(REQUIREMENTS_FILE),
                "--target",
                str(SITE_PACKAGES_DIR),
                "--upgrade",
            ],
            cwd=ROOT_DIR,
        )
    except Exception as e:
        _logger.error(f"[DEPLOY_ERROR] Failed to install dependencies: {str(e)}")
        raise RuntimeError("Python dependency installation failed") from e
    
def main() -> None:
    missing_modules = check_modules()
    for miss_module in missing_modules:
        _logger.info(f"Missing module: [{miss_module}]")

    if len(missing_modules) != 0:
        """主部署流程"""
        try:
            # 确保环境目录存在
            extutils.create_directory(ENV_DIR)

            # 安装Python依赖
            install_python_dependencies()

            _logger.info("[SUCCESS] Environment setup completed")

        except Exception as e:
            _logger.critical(f"[FATAL] Deployment failed: {str(e)}")
            raise
    else:
        _logger.info("Environment already setup completed")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
    main()
