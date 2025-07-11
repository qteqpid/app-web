#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def format_to_one_line():
    """将 dict_en_level_2.json 按一个单词一行的格式整理"""
    
    print("🚀 开始将 dict_en_level_2.json 转换为一行一个单词的格式...")
    
    # 读取 dict_en_level_2.json
    print("📖 读取 dict_en_level_2.json...")
    with open('dict_en_level_2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"  读取到 {len(data)} 个单词")
    
    # 创建输出文件名
    output_filename = 'dict_en_level_2_one_line.txt'
    
    # 写入一行一个单词的格式
    print(f"💾 写入文件: {output_filename}")
    with open(output_filename, 'w', encoding='utf-8') as f:
        for word_entry in data:
            # 格式: ID. character - phrase (pinyin) sentence
            line = f"{word_entry['id']}. {word_entry['character']} - {word_entry['phrase']} ({word_entry['pinyin']}) {word_entry['sentence']}"
            f.write(line + '\n')
    
    print(f"\n✅ 转换完成!")
    print(f"📁 输出文件: {output_filename}")
    
    # 显示统计信息
    print(f"\n📊 统计信息:")
    print(f"  总单词数: {len(data)}")
    print(f"  输出行数: {len(data)}")
    
    # 显示前10行示例
    print(f"\n📝 格式示例 (前10行):")
    with open(output_filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 10:
                print(f"  {line.strip()}")
            else:
                break
    
    # 显示后10行示例
    print(f"\n📝 格式示例 (后10行):")
    with open(output_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[-10:]:
            print(f"  {line.strip()}")

def format_simple_list():
    """创建简单的单词列表格式"""
    
    print("\n🔄 创建简单单词列表...")
    
    # 读取 dict_en_level_2.json
    with open('dict_en_level_2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建简单列表文件名
    simple_filename = 'dict_en_level_2_simple.txt'
    
    # 写入简单单词列表
    print(f"💾 写入简单列表: {simple_filename}")
    with open(simple_filename, 'w', encoding='utf-8') as f:
        for word_entry in data:
            # 只输出单词
            f.write(word_entry['character'] + '\n')
    
    print(f"✅ 简单列表创建完成!")
    print(f"📁 简单列表文件: {simple_filename}")
    
    # 显示前20个单词
    print(f"\n📝 简单列表示例 (前20个):")
    with open(simple_filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 20:
                print(f"  {i+1:4d}. {line.strip()}")
            else:
                break

if __name__ == "__main__":
    format_to_one_line()
    format_simple_list() 