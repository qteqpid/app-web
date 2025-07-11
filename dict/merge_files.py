#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

def parse_t4_sort_file(filename):
    """解析t_4_sort.json文件，它看起来不是标准JSON格式"""
    words = []
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式匹配每个JSON对象
    pattern = r'\{[^}]+\}'
    matches = re.findall(pattern, content)
    
    for match in matches:
        try:
            # 清理匹配的字符串，确保是有效的JSON
            cleaned = match.strip()
            if cleaned.endswith(','):
                cleaned = cleaned[:-1]
            
            word = json.loads(cleaned)
            if 'character' in word:
                words.append(word)
        except json.JSONDecodeError as e:
            print(f"解析错误: {e}, 内容: {match[:50]}...")
            continue
    
    return words

def merge_and_sort_files():
    """合并t_4_sort.json和add.json文件"""
    
    # 读取t_4_sort.json
    print("正在读取 t_4_sort.json...")
    t4_data = parse_t4_sort_file('t_4_sort.json')
    print(f"t_4_sort.json 解析到 {len(t4_data)} 个单词")
    
    # 读取add.json
    print("正在读取 add.json...")
    with open('add.json', 'r', encoding='utf-8') as f:
        add_data = json.load(f)
    print(f"add.json 包含 {len(add_data)} 个单词")
    
    # 合并数据
    all_words = t4_data + add_data
    print(f"合并后总共有 {len(all_words)} 个单词")
    
    # 去重（按character去重，保留第一个出现的）
    unique_words = []
    seen_characters = set()
    
    for word in all_words:
        if word['character'] not in seen_characters:
            unique_words.append(word)
            seen_characters.add(word['character'])
        else:
            print(f"发现重复单词: {word['character']}")
    
    print(f"去重后剩余 {len(unique_words)} 个单词")
    
    # 按character字典序排序
    unique_words.sort(key=lambda x: x['character'].lower())
    
    # 重新编号
    for i, word in enumerate(unique_words):
        word['id'] = i + 1
    
    # 写入合并后的文件
    output_filename = 't_4_sort_merged.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write('[\n')
        for i, word in enumerate(unique_words):
            line = json.dumps(word, ensure_ascii=False, separators=(',', ':'))
            if i < len(unique_words) - 1:
                line += ','
            f.write(line + '\n')
        f.write(']\n')
    
    print(f"合并完成！结果已保存到 {output_filename}")
    print(f"最终包含 {len(unique_words)} 个唯一单词")
    
    # 显示一些统计信息
    print("\n统计信息:")
    print(f"- 原始 t_4_sort.json: {len(t4_data)} 个单词")
    print(f"- 新增 add.json: {len(add_data)} 个单词")
    print(f"- 重复单词: {len(all_words) - len(unique_words)} 个")
    print(f"- 最终结果: {len(unique_words)} 个单词")
    
    # 显示前10个单词作为示例
    print("\n前10个单词示例:")
    for i, word in enumerate(unique_words[:10]):
        print(f"{i+1}. {word['character']} - {word['phrase']}")

if __name__ == "__main__":
    merge_and_sort_files() 