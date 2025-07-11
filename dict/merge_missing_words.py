#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def merge_missing_words():
    """将 missing_words.json 合并到 dict_en_level_2.json"""
    
    print("🚀 开始合并 missing_words.json 到 dict_en_level_2.json...")
    
    # 读取 dict_en_level_2.json
    print("📖 读取 dict_en_level_2.json...")
    with open('dict_en_level_2.json', 'r', encoding='utf-8') as f:
        dict_en_level_2 = json.load(f)
    
    print(f"  读取到 {len(dict_en_level_2)} 个单词")
    
    # 读取 missing_words.json
    print("📖 读取 missing_words.json...")
    with open('missing_words.json', 'r', encoding='utf-8') as f:
        missing_words = json.load(f)
    
    print(f"  读取到 {len(missing_words)} 个单词")
    
    # 创建现有单词的集合（用于去重）
    existing_words = set()
    for word_entry in dict_en_level_2:
        existing_words.add(word_entry['character'].lower())
    
    print(f"  现有单词集合大小: {len(existing_words)}")
    
    # 找到最大ID
    max_id = max(word_entry['id'] for word_entry in dict_en_level_2) if dict_en_level_2 else 0
    print(f"  当前最大ID: {max_id}")
    
    # 合并单词
    new_words = []
    skipped_count = 0
    
    for word_entry in missing_words:
        word = word_entry['character'].lower()
        
        if word in existing_words:
            print(f"  ⚠️  跳过重复单词: {word_entry['character']}")
            skipped_count += 1
            continue
        
        # 创建新的单词条目，更新ID
        new_entry = {
            'id': max_id + 1,
            'character': word_entry['character'],
            'phrase': word_entry['phrase'],
            'pinyin': word_entry['pinyin'],
            'sentence': word_entry['sentence']
        }
        
        new_words.append(new_entry)
        existing_words.add(word)
        max_id += 1
        
        print(f"  ✅ 添加新单词: {word_entry['character']} (ID: {new_entry['id']})")
    
    # 合并所有单词
    merged_data = dict_en_level_2 + new_words
    
    # 按ID排序
    merged_data.sort(key=lambda x: x['id'])
    
    # 保存合并后的文件
    print(f"\n💾 保存合并后的文件...")
    print(f"  原始单词数: {len(dict_en_level_2)}")
    print(f"  新增单词数: {len(new_words)}")
    print(f"  跳过重复数: {skipped_count}")
    print(f"  最终单词数: {len(merged_data)}")
    
    # 创建备份
    backup_filename = 'dict_en_level_2_backup.json'
    print(f"📋 创建备份文件: {backup_filename}")
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(dict_en_level_2, f, ensure_ascii=False, indent=2)
    
    # 保存合并后的文件
    with open('dict_en_level_2.json', 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 合并完成!")
    print(f"📁 原文件已备份为: {backup_filename}")
    print(f"📁 合并后的文件: dict_en_level_2.json")
    
    # 显示一些统计信息
    print(f"\n📊 统计信息:")
    print(f"  原始单词数: {len(dict_en_level_2)}")
    print(f"  新增单词数: {len(new_words)}")
    print(f"  跳过重复数: {skipped_count}")
    print(f"  最终单词数: {len(merged_data)}")
    
    # 显示新增单词的示例
    if new_words:
        print(f"\n📝 新增单词示例:")
        for i, word_entry in enumerate(new_words[:5]):
            print(f"  {word_entry['id']:3d}. {word_entry['character']}: {word_entry['phrase']}")
        if len(new_words) > 5:
            print(f"  ... 还有 {len(new_words) - 5} 个单词")

if __name__ == "__main__":
    merge_missing_words() 