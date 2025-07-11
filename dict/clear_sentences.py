#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def clear_sentences():
    """清空missing_words.json中的sentence字段"""
    
    print("正在读取 missing_words.json...")
    with open('missing_words.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"读取到 {len(data)} 个单词")
    
    # 清空每个单词的sentence字段
    for i, word_entry in enumerate(data):
        data[i]['sentence'] = ""
        print(f"已清空第 {i+1:3d}/{len(data)} 个单词的例句: {word_entry['character']}")
    
    # 保存更新后的文件
    print("\n正在保存文件...")
    with open('missing_words.json', 'w', encoding='utf-8') as f:
        f.write('[\n')
        for i, entry in enumerate(data):
            line = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))
            if i < len(data) - 1:
                line += ','
            f.write(line + '\n')
        f.write(']\n')
    
    print(f"\n✅ 已成功清空 {len(data)} 个单词的例句")
    print("📁 文件已保存为 missing_words.json")

if __name__ == "__main__":
    clear_sentences() 