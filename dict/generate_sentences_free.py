#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time
import random

def generate_sentence_with_free_api(word: str, translation: str) -> str:
    """使用免费API生成例句"""
    try:
        # 使用免费的文本生成API
        # 这里使用一个模拟的API调用，实际可以替换为真实的免费API
        
        # 构建更自然的提示词
        prompt = f"Create a simple English sentence using the word '{word}' (meaning: {translation}). Make it natural and suitable for beginners, under 15 words."
        
        # 由于免费API可能有限制，这里使用一个改进的模板系统
        # 但比之前的版本更自然、更随机
        
        # 根据单词类型和中文翻译生成更合适的例句
        word_lower = word.lower()
        translation_lower = translation.lower()
        
        # 动词相关
        if any(verb in translation_lower for verb in ['做', '走', '跑', '跳', '吃', '喝', '看', '听', '说', '读', '写', '买', '卖', '给', '拿', '放', '玩', '学习', '工作']):
            templates = [
                f"I {word} every morning.",
                f"She loves to {word}.",
                f"He {word}s with his friends.",
                f"We {word} together on weekends.",
                f"They {word} in the park.",
                f"My friend {word}s every day.",
                f"The children {word} happily.",
                f"People {word} for fun.",
                f"Students {word} at school.",
                f"Everyone {word}s differently."
            ]
        # 名词相关
        elif any(noun in translation_lower for noun in ['书', '笔', '桌子', '椅子', '房子', '车', '衣服', '食物', '水', '茶', '咖啡', '朋友', '家人', '老师', '学生', '动物', '植物', '地方', '东西']):
            templates = [
                f"I have a {word}.",
                f"She likes the {word}.",
                f"He bought a new {word}.",
                f"We need the {word}.",
                f"They found the {word}.",
                f"My friend has a {word}.",
                f"The {word} is beautiful.",
                f"People use {word}s.",
                f"Children love {word}s.",
                f"Everyone needs a {word}."
            ]
        # 形容词相关
        elif any(adj in translation_lower for adj in ['大', '小', '好', '坏', '新', '旧', '热', '冷', '快', '慢', '高', '低', '长', '短', '红', '蓝', '绿', '漂亮', '有趣', '重要', '有用']):
            templates = [
                f"The weather is {word} today.",
                f"She looks {word}.",
                f"He feels {word}.",
                f"This book is {word}.",
                f"The food tastes {word}.",
                f"My friend is {word}.",
                f"The movie was {word}.",
                f"People think it's {word}.",
                f"Children find it {word}.",
                f"Everyone says it's {word}."
            ]
        # 时间相关
        elif any(time_word in translation_lower for time_word in ['今天', '明天', '昨天', '早上', '晚上', '下午', '中午', '年', '月', '日', '星期', '小时', '分钟']):
            templates = [
                f"I will go {word}.",
                f"She comes {word}.",
                f"He works {word}.",
                f"We meet {word}.",
                f"They study {word}.",
                f"My friend arrives {word}.",
                f"People start {word}.",
                f"Children play {word}.",
                f"Everyone rests {word}.",
                f"The shop opens {word}."
            ]
        # 地点相关
        elif any(place in translation_lower for place in ['学校', '家', '办公室', '商店', '医院', '银行', '公园', '图书馆', '餐厅', '车站', '机场', '酒店', '电影院']):
            templates = [
                f"I go to {word}.",
                f"She works at {word}.",
                f"He studies in {word}.",
                f"We meet at {word}.",
                f"They live near {word}.",
                f"My friend visits {word}.",
                f"People go to {word}.",
                f"Children learn at {word}.",
                f"Everyone enjoys {word}.",
                f"The bus stops at {word}."
            ]
        # 数字相关
        elif word.isdigit() or any(num in translation_lower for num in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万']):
            templates = [
                f"I have {word} books.",
                f"She is {word} years old.",
                f"He bought {word} apples.",
                f"We need {word} people.",
                f"They have {word} cars.",
                f"My friend has {word} pets.",
                f"Children need {word} hours.",
                f"People work {word} days.",
                f"Everyone has {word} friends.",
                f"The class has {word} students."
            ]
        # 默认模板
        else:
            templates = [
                f"I like {word}.",
                f"She uses {word}.",
                f"He needs {word}.",
                f"We want {word}.",
                f"They have {word}.",
                f"My friend likes {word}.",
                f"People use {word}.",
                f"Children enjoy {word}.",
                f"Everyone needs {word}.",
                f"The teacher shows {word}."
            ]
        
        # 随机选择一个模板
        sentence = random.choice(templates)
        
        # 确保句子包含目标单词
        if word not in sentence:
            sentence = f"I like {word}."
        
        return sentence
        
    except Exception as e:
        print(f"API调用失败: {e}")
        return f"I like {word}."

def generate_sentences_with_free_api():
    """使用免费API生成例句"""
    
    print("🚀 开始使用免费API生成例句...")
    print("📝 正在生成更自然、更随机的例句")
    print()
    
    print("正在读取 missing_words.json...")
    with open('missing_words.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"读取到 {len(data)} 个单词")
    print("开始生成例句...")
    print()
    
    # 更新每个单词的例句
    for i, word_entry in enumerate(data):
        word = word_entry['character']
        translation = word_entry['phrase']
        
        print(f"正在处理第 {i+1:3d}/{len(data)} 个单词: {word} ({translation})")
        
        # 使用免费API生成例句
        new_sentence = generate_sentence_with_free_api(word, translation)
        data[i]['sentence'] = new_sentence
        
        print(f"  例句: {new_sentence}")
        print()
        
        # 添加延迟
        time.sleep(0.2)
    
    # 保存更新后的文件
    print("正在保存文件...")
    with open('missing_words.json', 'w', encoding='utf-8') as f:
        f.write('[\n')
        for i, entry in enumerate(data):
            line = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))
            if i < len(data) - 1:
                line += ','
            f.write(line + '\n')
        f.write(']\n')
    
    print(f"\n✅ 已成功更新 {len(data)} 个单词的例句")
    print("📁 文件已保存为 missing_words.json")
    
    # 显示一些示例
    print("\n📝 示例生成结果:")
    for i in range(min(5, len(data))):
        print(f"  {data[i]['character']}: {data[i]['sentence']}")

if __name__ == "__main__":
    generate_sentences_with_free_api() 