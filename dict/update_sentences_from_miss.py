#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

def update_sentences_from_miss():
    """从 miss.result 文件更新 dict_en_level_2.json 中的例句"""
    
    print("🚀 开始从 miss.result 更新例句...")
    print()
    
    # 读取 miss.result 文件
    print("📖 正在读取 miss.result...")
    miss_data = {}
    
    try:
        with open('miss.result', 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and ':' in line:
                    # 分割单词和例句
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        word = parts[0].strip()
                        sentence = parts[1].strip()
                        miss_data[word] = sentence
                    else:
                        print(f"⚠️  第 {line_num} 行格式错误: {line}")
                elif line:
                    print(f"⚠️  第 {line_num} 行缺少冒号: {line}")
    except FileNotFoundError:
        print("❌ 错误: 找不到 miss.result 文件")
        return
    except Exception as e:
        print(f"❌ 读取 miss.result 时出错: {e}")
        return
    
    print(f"✅ 从 miss.result 读取到 {len(miss_data)} 个单词-例句对")
    print()
    
    # 读取 dict_en_level_2.json 文件
    print("📖 正在读取 dict_en_level_2.json...")
    try:
        with open('dict_en_level_2.json', 'r', encoding='utf-8') as f:
            dict_data = json.load(f)
    except FileNotFoundError:
        print("❌ 错误: 找不到 dict_en_level_2.json 文件")
        return
    except Exception as e:
        print(f"❌ 读取 dict_en_level_2.json 时出错: {e}")
        return
    
    print(f"✅ 从 dict_en_level_2.json 读取到 {len(dict_data)} 个单词")
    print()
    
    # 备份原文件
    backup_filename = f"dict_en_level_2_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"💾 正在备份原文件为 {backup_filename}...")
    try:
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(dict_data, f, ensure_ascii=False, indent=2)
        print("✅ 备份完成")
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return
    
    print()
    
    # 统计信息
    updated_count = 0
    not_found_count = 0
    already_has_sentence_count = 0
    
    # 更新例句
    print("🔄 开始更新例句...")
    for i, entry in enumerate(dict_data):
        word = entry['character']
        current_sentence = entry.get('sentence', '')
        
        # 检查是否在 miss.result 中有对应的例句
        if word in miss_data:
            new_sentence = miss_data[word]
            
            # 如果当前句子为空，则更新
            if not current_sentence.strip():
                dict_data[i]['sentence'] = new_sentence
                updated_count += 1
                print(f"✅ 更新: {word} -> {new_sentence}")
            else:
                already_has_sentence_count += 1
                print(f"⏭️  跳过: {word} (已有例句)")
        else:
            not_found_count += 1
            if not current_sentence.strip():
                print(f"❌ 未找到: {word} (无例句)")
    
    print()
    print("📊 更新统计:")
    print(f"  ✅ 成功更新: {updated_count} 个单词")
    print(f"  ⏭️  已有例句: {already_has_sentence_count} 个单词")
    print(f"  ❌ 未找到例句: {not_found_count} 个单词")
    print()
    
    # 保存更新后的文件
    print("💾 正在保存更新后的文件...")
    try:
        with open('dict_en_level_2.json', 'w', encoding='utf-8') as f:
            json.dump(dict_data, f, ensure_ascii=False, indent=2)
        print("✅ 文件保存成功")
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")
        return
    
    print()
    print("🎉 例句更新完成!")
    print(f"📁 原文件已备份为: {backup_filename}")
    print(f"📁 更新后的文件: dict_en_level_2.json")
    
    # 显示一些示例
    print("\n📝 更新示例:")
    example_count = 0
    for entry in dict_data:
        if entry.get('sentence', '').strip() and example_count < 5:
            print(f"  {entry['character']}: {entry['sentence']}")
            example_count += 1

if __name__ == "__main__":
    update_sentences_from_miss() 