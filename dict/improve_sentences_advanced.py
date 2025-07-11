#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time
import random
import os

def generate_sentence_with_openai(word, translation):
    """使用OpenAI API生成例句"""
    try:
        # 这里使用一个免费的API服务来模拟OpenAI
        # 实际使用时需要替换为真实的API密钥
        api_key = os.getenv('OPENAI_API_KEY', '')
        
        if not api_key:
            # 如果没有API密钥，使用备用方案
            return generate_sentence_fallback(word, translation)
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant that generates simple English sentences for language learners. Keep sentences under 15 words, use simple vocabulary, and make them suitable for beginners.'
                },
                {
                    'role': 'user',
                    'content': f'Generate a simple English sentence using the word "{word}" (meaning: {translation}). The sentence should be natural and easy to understand.'
                }
            ],
            'max_tokens': 50,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            sentence = result['choices'][0]['message']['content'].strip()
            # 清理句子，移除引号等
            sentence = sentence.strip('"').strip("'")
            return sentence
        else:
            print(f"API调用失败: {response.status_code}")
            return generate_sentence_fallback(word, translation)
            
    except Exception as e:
        print(f"API调用出错: {e}")
        return generate_sentence_fallback(word, translation)

def generate_sentence_fallback(word, translation):
    """更丰富、更随机的例句生成"""
    import random
    word_lower = word.lower()
    translation_lower = translation.lower()

    # 常用主语、修饰语、地点、时间
    subjects = ["I", "You", "He", "She", "We", "They", "My friend", "The teacher", "A child", "People"]
    adverbs = ["quickly", "happily", "carefully", "every day", "sometimes", "at home", "at school", "in the morning", "after lunch", "on weekends", "with friends", "together", "for fun", "at the park", "in the city", "at night", "in summer", "in winter", "on the table", "in the bag", "at the shop", "in the kitchen", "on the bus", "in the garden", "at the zoo"]
    verbs = ["see", "like", "use", "find", "buy", "have", "need", "want", "enjoy", "make", "bring", "take", "eat", "drink", "play with", "look at", "talk about", "read about", "write about", "draw", "watch", "visit", "meet"]
    templates = [
        "{subj} {verb} the {word} {adv}.",
        "{subj} {verb} a {word} {adv}.",
        "{subj} {verb} {word} {adv}.",
        "{subj} {verb} the {word}.",
        "{subj} {verb} a {word}.",
        "{subj} {verb} {word}.",
        "{subj} always {verb} {word} {adv}.",
        "{subj} sometimes {verb} {word} {adv}.",
        "Yesterday, {subj} {verb} the {word}.",
        "On weekends, {subj} {verb} {word}.",
        "At school, {subj} {verb} the {word}.",
        "In the morning, {subj} {verb} a {word}.",
        "After lunch, {subj} {verb} {word}.",
        "{subj} wants to {verb} the {word} {adv}.",
        "{subj} is happy with the {word}.",
        "{subj} is looking for a {word}.",
        "{subj} is talking about the {word}.",
        "{subj} is playing with the {word} {adv}.",
        "{subj} is reading about {word}.",
        "{subj} is writing about {word}.",
        "{subj} is drawing a {word}.",
        "{subj} is watching the {word}.",
        "{subj} is visiting the {word}.",
        "{subj} is meeting a {word}.",
        "{subj} thinks the {word} is great.",
        "{subj} thinks the {word} is interesting.",
        "{subj} thinks the {word} is important.",
        "{subj} thinks the {word} is fun.",
        "{subj} thinks the {word} is useful."
    ]
    # 形容词模板
    adj_templates = [
        "The {word} is very {adj}.",
        "{subj} thinks the {word} is {adj}.",
        "{subj} saw a {adj} {word} {adv}.",
        "{subj} has a {adj} {word}.",
        "{subj} wants a {adj} {word}."
    ]
    # 形容词库
    adjectives = ["big", "small", "new", "old", "nice", "good", "bad", "funny", "happy", "sad", "interesting", "important", "beautiful", "delicious", "famous", "friendly", "useful", "wonderful", "amazing", "cool"]

    # 随机选择模板
    if any(adj in translation_lower for adj in ["的", "大", "小", "好", "坏", "新", "旧", "有趣", "重要", "漂亮", "美味", "著名", "友好", "有用", "棒", "酷"]):
        template = random.choice(adj_templates)
        adj = random.choice(adjectives)
        sentence = template.format(word=word, subj=random.choice(subjects), adj=adj, adv=random.choice(adverbs))
    else:
        template = random.choice(templates)
        sentence = template.format(word=word, subj=random.choice(subjects), verb=random.choice(verbs), adv=random.choice(adverbs))

    # 句首大写，句尾句号
    sentence = sentence[0].upper() + sentence[1:]
    if not sentence.endswith('.'):
        sentence += '.'
    return sentence

def improve_sentences_advanced():
    """使用高级方法改进missing_words.json中的例句"""
    
    print("正在读取 missing_words.json...")
    with open('missing_words.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"读取到 {len(data)} 个单词")
    print("开始生成改进的例句...")
    
    # 更新每个单词的例句
    for i, word_entry in enumerate(data):
        word = word_entry['character']
        translation = word_entry['phrase']
        
        print(f"正在处理第 {i+1:3d}/{len(data)} 个单词: {word} ({translation})")
        
        # 尝试使用API生成例句，如果失败则使用备用方案
        try:
            new_sentence = generate_sentence_with_openai(word, translation)
        except:
            new_sentence = generate_sentence_fallback(word, translation)
        
        data[i]['sentence'] = new_sentence
        
        print(f"  例句: {new_sentence}")
        
        # 添加延迟以避免API限制
        time.sleep(0.2)
    
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
    
    print(f"\n✅ 已成功更新 {len(data)} 个单词的例句")
    print("📁 文件已保存为 missing_words.json")
    
    # 显示一些示例
    print("\n📝 示例改进:")
    for i in range(min(5, len(data))):
        print(f"  {data[i]['character']}: {data[i]['sentence']}")

if __name__ == "__main__":
    improve_sentences_advanced() 