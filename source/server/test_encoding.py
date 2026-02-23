"""
编码测试脚本
验证Windows控制台UTF-8输出是否正常
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入编码修复工具
try:
    from app.utils.encoding_fix import fix_console_encoding, safe_print
    fix_console_encoding()
    print("Encoding fix loaded successfully")
except Exception as e:
    print(f"Failed to load encoding fix: {e}")

# 测试输出
print("\n" + "="*60)
print("Encoding Test - UTF-8 Chinese Characters")
print("="*60)

# 测试中文输出
print("\nTest 1: Basic Chinese characters")
print("Success - 成功")
print("Failed - 失败")
print("Testing - 测试")

# 测试特殊符号
print("\nTest 2: Special symbols")
try:
    print("Check mark - ✓")
    print("Cross mark - ✗")
except UnicodeEncodeError as e:
    print(f"UnicodeEncodeError: {e}")
    print("Using safe_print instead:")
    safe_print("Check mark - ✓")
    safe_print("Cross mark - ✗")

# 测试混合输出
print("\nTest 3: Mixed output")
print("[OK] Test passed - 测试通过")
print("[FAIL] Test failed - 测试失败")

# 测试Python版本和编码
print("\n" + "="*60)
print("System Information")
print("="*60)
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Default encoding: {sys.getdefaultencoding()}")
print(f"stdout encoding: {sys.stdout.encoding}")
print(f"stderr encoding: {sys.stderr.encoding}")
print(f"filesystem encoding: {sys.getfilesystemencoding()}")

print("\n" + "="*60)
print("Test completed - 测试完成")
print("="*60)
