#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
from datetime import datetime

def json_to_one_line(json_file_path):
    """将JSON文件重新整理为一行一个条目的格式（参考dict_zh.json）"""
    
    print(f"🚀 开始重新整理 {json_file_path} 为一行一个条目格式...")
    print()
    
    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"❌ 错误: 文件 {json_file_path} 不存在")
        return
    
    # 读取JSON文件
    print(f"📖 正在读取 {json_file_path}...")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 错误: 找不到文件 {json_file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        return
    
    print(f"✅ 成功读取JSON文件，包含 {len(data)} 个条目")
    print()
    
    # 生成输出文件名
    base_name = os.path.splitext(json_file_path)[0]
    output_filename = f"{base_name}_one_line.json"
    
    # 重新整理并保存
    print(f"💾 正在保存为 {output_filename}...")
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write('[\n')
            for i, entry in enumerate(data):
                # 使用紧凑格式，一行一个条目
                line = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))
                if i < len(data) - 1:
                    line += ','
                f.write('    ' + line + '\n')
            f.write(']\n')
        
        print("✅ 文件保存成功")
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")
        return
    
    print()
    print("🎉 重新整理完成!")
    print(f"📁 输出文件: {output_filename}")
    print(f"📊 总共整理: {len(data)} 个条目")
    
    # 显示一些示例
    print("\n📝 整理示例:")
    example_count = 0
    for entry in data:
        if example_count >= 5:
            break
        line = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))
        print(f"  {line}")
        example_count += 1
    
    if len(data) > 5:
        print(f"  ... 还有 {len(data) - 5} 个条目")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python3 json_to_one_line.py <json文件路径>")
        print("示例: python3 json_to_one_line.py dict_en_level_2.json")
        print("功能: 将JSON文件重新整理为一行一个条目的格式（参考dict_zh.json）")
        return
    
    json_file_path = sys.argv[1]
    json_to_one_line(json_file_path)

if __name__ == "__main__":
    main() 