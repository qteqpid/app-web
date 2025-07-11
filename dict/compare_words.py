#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

def read_ket_list(filename):
    """读取ket.list.clean文件中的所有单词，支持多种分隔符"""
    words = set()
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                # 用逗号、斜杠、空格分割，允许多个空格
                parts = re.split(r'[\s,\/]+', line)
                for part in parts:
                    word = part.strip()
                    if word:
                        words.add(word)
    return words

def read_dict_json(filename):
    """读取dict_en_level_2.json文件中的单词"""
    words = set()
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            if 'character' in item:
                # 处理包含多个单词的character，如 "a(an)"
                char = item['character']
                if '(' in char and ')' in char:
                    # 提取括号前的单词
                    base_word = char.split('(')[0].strip()
                    words.add(base_word)
                else:
                    words.add(char)
    return words

def normalize_word(word):
    """标准化单词，去除特殊字符和空格"""
    word = word.strip()
    word = re.sub(r'[^\w\-]', '', word)  # 只保留字母、数字、下划线、连字符
    return word.lower()

def compare_files():
    print("正在读取 ket.list.clean...")
    ket_words = read_ket_list('ket.list.clean')
    print(f"ket.list.clean 拆分后包含 {len(ket_words)} 个单词")
    
    print("正在读取 dict_en_level_2.json...")
    dict_words = read_dict_json('dict_en_level_2.json')
    print(f"dict_en_level_2.json 包含 {len(dict_words)} 个单词")
    
    ket_normalized = {normalize_word(word) for word in ket_words}
    dict_normalized = {normalize_word(word) for word in dict_words}
    
    missing_words = ket_normalized - dict_normalized
    print(f"\nket.list.clean 中但不在 dict_en_level_2.json 中的单词共 {len(missing_words)} 个")
    missing_sorted = sorted(missing_words)
    print("前50个缺失的单词:")
    for i, word in enumerate(missing_sorted[:50]):
        print(f"{i+1:3d}. {word}")
    if len(missing_sorted) > 50:
        print(f"... 还有 {len(missing_sorted) - 50} 个单词")
    with open('missing_words.txt', 'w', encoding='utf-8') as f:
        for word in missing_sorted:
            f.write(word + '\n')
    print("\n完整缺失单词已保存到 missing_words.txt")
    print(f"覆盖率: {((len(ket_normalized) - len(missing_words)) / len(ket_normalized) * 100):.1f}%")

if __name__ == "__main__":
    compare_files() 