#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

def read_missing_words(filename):
    """读取missing_words.txt中的单词"""
    words = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            if word and word not in ['', '-']:  # 过滤空行和单独的连字符
                words.append(word)
    return words

def generate_word_entry(word, id_num):
    """为单个单词生成JSON格式的条目"""
    # 简单的音标生成（这里使用占位符，实际应用中可能需要更复杂的音标生成）
    pinyin = f"|{word.lower()}|"
    
    # 生成简单的例句
    sentence = f"I like {word}."
    
    # 中文翻译（这里使用占位符，实际应用中需要真实的翻译）
    phrase = f"{word}的中文翻译"
    
    return {
        "id": id_num,
        "character": word,
        "phrase": phrase,
        "pinyin": pinyin,
        "sentence": sentence
    }

def main():
    print("正在读取 missing_words.txt...")
    missing_words = read_missing_words('missing_words.txt')
    print(f"读取到 {len(missing_words)} 个单词")
    
    # 生成JSON格式的单词条目
    word_entries = []
    for i, word in enumerate(missing_words, 1):
        entry = generate_word_entry(word, i)
        word_entries.append(entry)
    
    # 保存到JSON文件
    output_filename = 'missing_words.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write('[\n')
        for i, entry in enumerate(word_entries):
            line = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))
            if i < len(word_entries) - 1:
                line += ','
            f.write(line + '\n')
        f.write(']\n')
    
    print(f"已生成 {len(word_entries)} 个单词条目")
    print(f"结果已保存到 {output_filename}")
    
    # 显示前5个生成的条目作为示例
    print("\n前5个生成的条目示例:")
    for i, entry in enumerate(word_entries[:5]):
        print(f"{i+1}. {entry}")

if __name__ == "__main__":
    main() 