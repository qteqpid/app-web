#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from pypinyin import pinyin, Style

def get_pinyin_for_character(char):
    """获取单个汉字的拼音"""
    try:
        # 使用 pypinyin 获取拼音
        pinyin_list = pinyin(char, style=Style.TONE)
        if pinyin_list and pinyin_list[0]:
            return pinyin_list[0][0]
        else:
            return ""
    except Exception as e:
        print(f"获取拼音失败 {char}: {e}")
        return ""

def convert_zh_to_json():
    """将 zh 文件转换为 JSON 格式"""
    
    print("🚀 开始转换 zh 文件为 JSON 格式...")
    print()
    
    # 读取 zh 文件
    print("📖 正在读取 zh 文件...")
    zh_data = []
    
    try:
        with open('zh', 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and '：' in line:  # 使用中文冒号
                    # 分割汉字和组词
                    parts = line.split('：', 1)
                    if len(parts) == 2:
                        character = parts[0].strip()
                        phrase = parts[1].strip()
                        
                        # 获取拼音
                        pinyin_text = get_pinyin_for_character(character)
                        
                        zh_data.append({
                            'character': character,
                            'phrase': phrase,
                            'pinyin': pinyin_text,
                            'sentence': ''  # 留空
                        })
                    else:
                        print(f"⚠️  第 {line_num} 行格式错误: {line}")
                elif line and ':' in line:  # 也支持英文冒号
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        character = parts[0].strip()
                        phrase = parts[1].strip()
                        
                        # 获取拼音
                        pinyin_text = get_pinyin_for_character(character)
                        
                        zh_data.append({
                            'character': character,
                            'phrase': phrase,
                            'pinyin': pinyin_text,
                            'sentence': ''  # 留空
                        })
                    else:
                        print(f"⚠️  第 {line_num} 行格式错误: {line}")
                elif line:
                    print(f"⚠️  第 {line_num} 行缺少冒号: {line}")
    except FileNotFoundError:
        print("❌ 错误: 找不到 zh 文件")
        return
    except Exception as e:
        print(f"❌ 读取 zh 文件时出错: {e}")
        return
    
    print(f"✅ 从 zh 文件读取到 {len(zh_data)} 个汉字")
    print()
    
    # 添加 ID 字段
    for i, entry in enumerate(zh_data):
        entry['id'] = i + 1
    
    # 保存为 JSON 文件
    output_filename = 'zh_characters.json'
    print(f"💾 正在保存为 {output_filename}...")
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(zh_data, f, ensure_ascii=False, indent=2)
        print("✅ 文件保存成功")
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")
        return
    
    print()
    print("🎉 转换完成!")
    print(f"📁 输出文件: {output_filename}")
    print(f"📊 总共转换: {len(zh_data)} 个汉字")
    
    # 显示一些示例
    print("\n📝 转换示例:")
    for i in range(min(10, len(zh_data))):
        entry = zh_data[i]
        print(f"  {entry['id']:3d}. {entry['character']} ({entry['pinyin']}): {entry['phrase']}")
    
    # 检查是否有拼音获取失败的字符
    failed_pinyin = [entry for entry in zh_data if not entry['pinyin']]
    if failed_pinyin:
        print(f"\n⚠️  有 {len(failed_pinyin)} 个字符的拼音获取失败:")
        for entry in failed_pinyin[:5]:  # 只显示前5个
            print(f"  {entry['character']}")
        if len(failed_pinyin) > 5:
            print(f"  ... 还有 {len(failed_pinyin) - 5} 个")

if __name__ == "__main__":
    convert_zh_to_json() 