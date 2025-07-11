#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time
import random

def generate_sentence_with_api(word, translation):
    """使用在线API生成例句"""
    try:
        # 使用免费的API来生成例句
        # 这里使用一个简单的示例API，实际使用时可能需要替换为其他可用的API
        prompt = f"Generate a simple English sentence using the word '{word}' (meaning: {translation}). The sentence should be suitable for beginners, no more than 15 words, and use simple vocabulary."
        
        # 由于API调用可能有限制，这里先使用一些预设的例句模板
        sentence_templates = [
            f"I like {word}.",
            f"This is a {word}.",
            f"She has a {word}.",
            f"He uses {word}.",
            f"We need {word}.",
            f"They want {word}.",
            f"The {word} is good.",
            f"My {word} is here.",
            f"Can you see the {word}?",
            f"Do you have {word}?",
            f"I want to buy {word}.",
            f"She likes {word}.",
            f"He needs {word}.",
            f"We use {word}.",
            f"They make {word}."
        ]
        
        # 根据单词类型选择更合适的模板
        if word.endswith('ing'):
            templates = [
                f"I enjoy {word}.",
                f"She likes {word}.",
                f"He is {word}.",
                f"We are {word}.",
                f"They love {word}."
            ]
        elif word.endswith('ed'):
            templates = [
                f"I {word} yesterday.",
                f"She {word} last week.",
                f"He {word} the book.",
                f"We {word} together.",
                f"They {word} quickly."
            ]
        elif word in ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']:
            templates = [
                f"I go {word} school.",
                f"She is {word} home.",
                f"He works {word} office.",
                f"We study {word} library.",
                f"They live {word} city."
            ]
        else:
            templates = sentence_templates
        
        # 随机选择一个模板
        sentence = random.choice(templates)
        
        # 如果模板不合适，使用更通用的格式
        if sentence.count(word) == 0:
            sentence = f"I like {word}."
        
        return sentence
        
    except Exception as e:
        print(f"API调用失败: {e}")
        # 返回默认例句
        return f"I like {word}."

def improve_sentences():
    """改进missing_words.json中的例句"""
    
    print("正在读取 missing_words.json...")
    with open('missing_words.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"读取到 {len(data)} 个单词")
    
    # 更新每个单词的例句
    for i, word_entry in enumerate(data):
        word = word_entry['character']
        translation = word_entry['phrase']
        
        print(f"正在生成第 {i+1:3d}/{len(data)} 个单词的例句: {word}")
        
        # 生成新例句
        new_sentence = generate_sentence_with_api(word, translation)
        data[i]['sentence'] = new_sentence
        
        print(f"  {word} -> {new_sentence}")
        
        # 添加延迟以避免API限制
        time.sleep(0.1)
    
    # 保存更新后的文件
    with open('missing_words.json', 'w', encoding='utf-8') as f:
        f.write('[\n')
        for i, entry in enumerate(data):
            line = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))
            if i < len(data) - 1:
                line += ','
            f.write(line + '\n')
        f.write(']\n')
    
    print(f"\n已更新 {len(data)} 个单词的例句")
    print("文件已保存为 missing_words.json")

if __name__ == "__main__":
    improve_sentences() 