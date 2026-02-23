"""
前端登录测试辅助脚本
用于诊断前端登录问题
"""
import webbrowser
import time

print("="*60)
print("前端登录测试")
print("="*60)
print()
print("正在打开浏览器...")
print()

# 打开浏览器到登录页面
url = "http://localhost:8080"
webbrowser.open(url)

print(f"已打开: {url}")
print()
print("请按照以下步骤测试：")
print()
print("1. 测试账号：admin / 123456")
print("2. 测试账号：teacher / 123456")
print("3. 测试账号：student / 123456")
print()
print("如果登录失败：")
print("- 按F12打开开发者工具")
print("- 查看Console标签的错误信息")
print("- 查看Network标签的login请求")
print()
print("按回车键继续...")
input()

print()
print("请告诉我测试结果：")
print("1. 哪些账号可以登录？")
print("2. 哪些账号无法登录？")
print("3. 有什么错误信息？")
print()
