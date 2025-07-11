#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def sort_and_renumber():
    """将 dict_en_level_2.json 按字典序排序并重新编号"""
    
    print("🚀 开始按字典序排序并重新编号 dict_en_level_2.json...")
    
    # 读取 dict_en_level_2.json
    print("📖 读取 dict_en_level_2.json...")
    with open('dict_en_level_2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"  读取到 {len(data)} 个单词")
    
    # 按 character 字段排序（字典序）
    print("🔄 按字典序排序...")
    sorted_data = sorted(data, key=lambda x: x['character'].lower())
    
    # 重新编号
    print("🔢 重新编号...")
    for i, word_entry in enumerate(sorted_data, 1):
        word_entry['id'] = i
        print(f"  {i:4d}. {word_entry['character']}")
    
    # 创建备份
    backup_filename = 'dict_en_level_2_sorted_backup.json'
    print(f"\n📋 创建备份文件: {backup_filename}")
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 保存排序后的文件
    print("💾 保存排序后的文件...")
    with open('dict_en_level_2.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 排序和重新编号完成!")
    print(f"📁 原文件已备份为: {backup_filename}")
    print(f"📁 排序后的文件: dict_en_level_2.json")
    
    # 显示统计信息
    print(f"\n📊 统计信息:")
    print(f"  总单词数: {len(sorted_data)}")
    print(f"  第一个单词: {sorted_data[0]['character']} (ID: {sorted_data[0]['id']})")
    print(f"  最后一个单词: {sorted_data[-1]['character']} (ID: {sorted_data[-1]['id']})")
    
    # 显示排序后的示例
    print(f"\n📝 排序后示例 (前10个):")
    for i, word_entry in enumerate(sorted_data[:10]):
        print(f"  {word_entry['id']:4d}. {word_entry['character']}: {word_entry['phrase']}")
    
    print(f"\n📝 排序后示例 (后10个):")
    for i, word_entry in enumerate(sorted_data[-10:]):
        print(f"  {word_entry['id']:4d}. {word_entry['character']}: {word_entry['phrase']}")

if __name__ == "__main__":
    sort_and_renumber() 