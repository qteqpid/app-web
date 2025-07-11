#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time
import random
import urllib.parse

class FreeSentenceGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def generate_with_rapidapi(self, word: str, translation: str) -> str:
        """使用RapidAPI的免费文本生成服务"""
        try:
            # 使用RapidAPI上的免费文本生成API
            url = "https://text-generator-api.p.rapidapi.com/generate"
            
            headers = {
                "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",  # 需要注册获取免费密钥
                "X-RapidAPI-Host": "text-generator-api.p.rapidapi.com"
            }
            
            payload = {
                "prompt": f"Generate a simple English sentence using the word '{word}' (meaning: {translation}). Keep it under 15 words for beginners.",
                "max_tokens": 30
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                sentence = result.get('generated_text', '').strip()
                if sentence and len(sentence) > 5:
                    return self.clean_sentence(sentence)
            
            return ""
            
        except Exception as e:
            print(f"RapidAPI调用失败: {e}")
            return ""
    
    def generate_with_huggingface_free(self, word: str, translation: str) -> str:
        """使用Hugging Face的免费推理API"""
        try:
            # 使用Hugging Face的免费推理端点
            url = "https://api-inference.huggingface.co/models/gpt2"
            
            headers = {
                "Authorization": "Bearer hf_xxx"  # 需要注册获取免费token
            }
            
            payload = {
                "inputs": f"Generate a simple English sentence using '{word}' (meaning: {translation}):",
                "parameters": {
                    "max_new_tokens": 25,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    sentence = generated_text.split(':', 1)[-1].strip()
                    return self.clean_sentence(sentence)
            
            return ""
            
        except Exception as e:
            print(f"Hugging Face免费API调用失败: {e}")
            return ""
    
    def generate_with_ai21_free(self, word: str, translation: str) -> str:
        """使用AI21的免费API"""
        try:
            url = "https://api.ai21.com/studio/v1/j1-jumbo/complete"
            
            headers = {
                "Authorization": "Bearer YOUR_AI21_KEY",  # 需要注册获取免费密钥
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": f"Generate a simple English sentence using the word '{word}' (meaning: {translation}). Keep it under 15 words for beginners:",
                "numResults": 1,
                "maxTokens": 25,
                "temperature": 0.7
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                completions = result.get('completions', [])
                if completions:
                    sentence = completions[0].get('data', {}).get('text', '').strip()
                    return self.clean_sentence(sentence)
            
            return ""
            
        except Exception as e:
            print(f"AI21 API调用失败: {e}")
            return ""
    
    def generate_with_web_scraping(self, word: str, translation: str) -> str:
        """通过网页抓取获取例句"""
        try:
            # 尝试从在线词典网站获取例句
            search_urls = [
                f"https://dictionary.cambridge.org/dictionary/english/{word}",
                f"https://www.merriam-webster.com/dictionary/{word}",
                f"https://www.collinsdictionary.com/dictionary/english/{word}"
            ]
            
            for url in search_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        # 这里需要解析HTML来提取例句
                        # 简化版本：返回基于模板的例句
                        return self.generate_template_sentence(word, translation)
                except:
                    continue
            
            return ""
            
        except Exception as e:
            print(f"网页抓取失败: {e}")
            return ""
    
    def generate_with_community_api(self, word: str, translation: str) -> str:
        """使用社区维护的免费API"""
        try:
            # 使用一些社区维护的免费文本生成API
            apis = [
                {
                    "url": "https://api.text-generator.com/generate",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"},
                    "data": {
                        "prompt": f"Simple English sentence with '{word}':",
                        "max_length": 50
                    }
                }
            ]
            
            for api in apis:
                try:
                    response = self.session.request(
                        api["method"], 
                        api["url"], 
                        json=api["data"], 
                        headers=api["headers"], 
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        sentence = result.get('text', '').strip()
                        if sentence:
                            return self.clean_sentence(sentence)
                            
                except Exception as e:
                    print(f"社区API调用失败: {e}")
                    continue
            
            return ""
            
        except Exception as e:
            print(f"社区API调用失败: {e}")
            return ""
    
    def generate_template_sentence(self, word: str, translation: str) -> str:
        """使用改进的模板生成例句（备用方案）"""
        # 更丰富的模板库
        templates = [
            # 基础句型
            f"I like {word}.",
            f"She uses {word}.",
            f"He needs {word}.",
            f"We want {word}.",
            f"They have {word}.",
            
            # 带修饰语的句型
            f"I really like {word}.",
            f"She often uses {word}.",
            f"He always needs {word}.",
            f"We sometimes want {word}.",
            f"They usually have {word}.",
            
            # 带时间地点的句型
            f"I like {word} every day.",
            f"She uses {word} at home.",
            f"He needs {word} at school.",
            f"We want {word} on weekends.",
            f"They have {word} in the morning.",
            
            # 带形容词的句型
            f"I like the {word}.",
            f"She uses a {word}.",
            f"He needs the {word}.",
            f"We want a {word}.",
            f"They have the {word}.",
            
            # 更复杂的句型
            f"My friend likes {word}.",
            f"The teacher shows {word}.",
            f"Children enjoy {word}.",
            f"People use {word}.",
            f"Everyone needs {word}.",
            
            # 动词变化
            f"I am using {word}.",
            f"She is looking at {word}.",
            f"He is working with {word}.",
            f"We are studying {word}.",
            f"They are playing with {word}.",
            
            # 过去时
            f"I used {word} yesterday.",
            f"She bought {word} last week.",
            f"He found {word}.",
            f"We saw {word}.",
            f"They made {word}.",
            
            # 将来时
            f"I will use {word}.",
            f"She will buy {word}.",
            f"He will need {word}.",
            f"We will want {word}.",
            f"They will have {word}."
        ]
        
        # 根据单词类型选择更合适的模板
        word_lower = word.lower()
        translation_lower = translation.lower()
        
        # 动词相关
        if any(verb in translation_lower for verb in ['做', '走', '跑', '跳', '吃', '喝', '看', '听', '说', '读', '写', '买', '卖', '给', '拿', '放', '玩', '学习', '工作']):
            verb_templates = [
                f"I {word} every morning.",
                f"She loves to {word}.",
                f"He {word}s with his friends.",
                f"We {word} together.",
                f"They {word} in the park.",
                f"My friend {word}s every day.",
                f"The children {word} happily.",
                f"People {word} for fun.",
                f"Students {word} at school.",
                f"Everyone {word}s differently."
            ]
            templates.extend(verb_templates)
        
        # 形容词相关
        elif any(adj in translation_lower for adj in ['大', '小', '好', '坏', '新', '旧', '热', '冷', '快', '慢', '高', '低', '长', '短', '红', '蓝', '绿', '漂亮', '有趣', '重要', '有用']):
            adj_templates = [
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
            templates.extend(adj_templates)
        
        # 名词相关
        elif any(noun in translation_lower for noun in ['书', '笔', '桌子', '椅子', '房子', '车', '衣服', '食物', '水', '茶', '咖啡', '朋友', '家人', '老师', '学生', '动物', '植物', '地方', '东西']):
            noun_templates = [
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
            templates.extend(noun_templates)
        
        # 随机选择一个模板
        sentence = random.choice(templates)
        
        # 确保句子包含目标单词
        if word not in sentence:
            sentence = f"I like {word}."
        
        return sentence
    
    def clean_sentence(self, sentence: str) -> str:
        """清理和格式化句子"""
        # 移除多余的引号和标点
        sentence = sentence.strip('"').strip("'").strip()
        
        # 确保句子以句号结尾
        if not sentence.endswith('.'):
            sentence += '.'
        
        # 确保首字母大写
        if sentence and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]
        
        return sentence
    
    def generate_sentence(self, word: str, translation: str) -> str:
        """尝试多种免费方法生成例句"""
        methods = [
            ('RapidAPI', lambda: self.generate_with_rapidapi(word, translation)),
            ('Hugging Face Free', lambda: self.generate_with_huggingface_free(word, translation)),
            ('AI21 Free', lambda: self.generate_with_ai21_free(word, translation)),
            ('Web Scraping', lambda: self.generate_with_web_scraping(word, translation)),
            ('Community API', lambda: self.generate_with_community_api(word, translation))
        ]
        
        for method_name, method_func in methods:
            print(f"  尝试使用 {method_name}...")
            result = method_func()
            if result:
                print(f"  ✅ {method_name} 生成成功")
                return result
            else:
                print(f"  ❌ {method_name} 生成失败")
        
        # 如果所有免费方法都失败，使用改进的模板
        print("  🔄 使用改进模板生成")
        return self.generate_template_sentence(word, translation)

def generate_sentences_with_free_alternatives():
    """使用免费替代方案生成例句"""
    
    print("🚀 开始使用免费替代方案生成例句...")
    print("📝 尝试多种免费API和服务")
    print("💡 提示: 某些API可能需要注册获取免费密钥")
    print()
    
    generator = FreeSentenceGenerator()
    
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
        
        # 使用免费替代方案生成例句
        new_sentence = generator.generate_sentence(word, translation)
        data[i]['sentence'] = new_sentence
        
        print(f"  例句: {new_sentence}")
        print()
        
        # 添加延迟
        time.sleep(0.5)
    
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
    generate_sentences_with_free_alternatives() 