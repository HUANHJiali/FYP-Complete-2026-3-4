"""
编码处理工具
解决Windows控制台UTF-8输出乱码问题
"""
import sys
import io


def fix_console_encoding():
    """
    修复Windows控制台编码问题
    确保UTF-8字符能正确输出
    """
    # Windows平台特殊处理
    if sys.platform == 'win32':
        try:
            # 设置标准输出为UTF-8
            if sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            if sys.stderr.encoding != 'utf-8':
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass  # 如果失败，继续使用默认编码

    # 设置环境变量
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def safe_print(text):
    """
    安全打印函数，处理编码异常
    
    Args:
        text: 要打印的文本
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果UTF-8编码失败，尝试GBK
        try:
            print(text.encode('gbk', errors='replace').decode('gbk'))
        except Exception:
            # 如果还是失败，使用ASCII兼容模式
            print(text.encode('ascii', errors='replace').decode('ascii'))


def test_result(test_name, success, message=''):
    """
    格式化测试结果输出（ASCII兼容）
    
    Args:
        test_name: 测试名称
        success: 是否成功
        message: 附加消息
    """
    status = '[OK]' if success else '[FAIL]'
    output = f"{status} {test_name}"
    if message:
        output += f" - {message}"
    
    safe_print(output)


# 自动修复编码（模块加载时执行）
fix_console_encoding()
