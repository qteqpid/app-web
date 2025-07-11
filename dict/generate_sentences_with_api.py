#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time
import os
from typing import Optional

class SentenceGenerator:
    def __init__(self):
        # 可以配置不同的API
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        
    def generate_with_openai(self, word: str, translation: str) -> Optional[str]:
        """使用OpenAI API生成例句"""
        if not self.openai_api_key:
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant that generates simple, natural English sentences for language learners. Keep sentences under 15 words, use simple vocabulary, and make them suitable for beginners. Return only the sentence, no explanations.'
                    },
                    {
                        'role': 'user',
                        'content': f'Generate a simple English sentence using the word "{word}" (meaning: {translation}). The sentence should be natural and easy to understand for beginners.'
                    }
                ],
                'max_tokens': 50,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                sentence = result['choices'][0]['message']['content'].strip()
                # 清理句子
                sentence = sentence.strip('"').strip("'").strip()
                if sentence.endswith('.'):
                    return sentence
                else:
                    return sentence + '.'
            else:
                print(f"OpenAI API错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return None
    
    def generate_with_huggingface(self, word: str, translation: str) -> Optional[str]:
        """使用Hugging Face API生成例句"""
        if not self.huggingface_api_key:
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.huggingface_api_key}',
                'Content-Type': 'application/json'
            }
            
            # 使用文本生成模型
            data = {
                'inputs': f'Generate a simple English sentence using the word "{word}" (meaning: {translation}):',
                'parameters': {
                    'max_new_tokens': 30,
                    'temperature': 0.7,
                    'do_sample': True
                }
            }
            
            response = requests.post(
                'https://api-inference.huggingface.co/models/gpt2',
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # 提取生成的句子部分
                    sentence = generated_text.split(':', 1)[-1].strip()
                    sentence = sentence.strip('"').strip("'").strip()
                    if sentence and len(sentence) > 5:
                        if not sentence.endswith('.'):
                            sentence += '.'
                        return sentence
            else:
                print(f"Hugging Face API错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Hugging Face API调用失败: {e}")
            return None
    
    def generate_with_anthropic(self, word: str, translation: str) -> Optional[str]:
        """使用Anthropic Claude API生成例句"""
        if not self.anthropic_api_key:
            return None
            
        try:
            headers = {
                'x-api-key': self.anthropic_api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 50,
                'messages': [
                    {
                        'role': 'user',
                        'content': f'Generate a simple English sentence using the word "{word}" (meaning: {translation}). Keep it under 15 words and suitable for beginners. Return only the sentence.'
                    }
                ]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                sentence = result['content'][0]['text'].strip()
                sentence = sentence.strip('"').strip("'").strip()
                if sentence and len(sentence) > 5:
                    if not sentence.endswith('.'):
                        sentence += '.'
                    return sentence
            else:
                print(f"Anthropic API错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Anthropic API调用失败: {e}")
            return None
    
    def generate_with_free_api(self, word: str, translation: str) -> Optional[str]:
        """使用免费API生成例句（备用方案）"""
        try:
            # 使用免费的文本生成API
            prompt = f"Generate a simple English sentence using '{word}' (meaning: {translation}). Keep it under 15 words for beginners."
            
            # 这里可以替换为其他免费的API
            # 例如：使用一些开放的文本生成服务
            
            # 暂时返回一个简单的模板，实际使用时需要替换为真实API
            return f"I like {word}."
            
        except Exception as e:
            print(f"免费API调用失败: {e}")
            return None
    
    def generate_sentence(self, word: str, translation: str) -> str:
        """尝试多种API生成例句"""
        # 按优先级尝试不同的API
        apis = [
            ('OpenAI', lambda: self.generate_with_openai(word, translation)),
            ('Hugging Face', lambda: self.generate_with_huggingface(word, translation)),
            ('Anthropic', lambda: self.generate_with_anthropic(word, translation)),
            ('Free API', lambda: self.generate_with_free_api(word, translation))
        ]
        
        for api_name, api_func in apis:
            print(f"  尝试使用 {api_name} API...")
            result = api_func()
            if result:
                print(f"  ✅ {api_name} 生成成功")
                return result
            else:
                print(f"  ❌ {api_name} 生成失败")
        
        # 如果所有API都失败，返回默认例句
        return f"I like {word}."

def generate_sentences_with_api():
    """使用API生成例句"""
    
    print("🚀 开始使用语言模型API生成例句...")
    print("📝 请确保已设置相应的API密钥环境变量")
    print("   - OPENAI_API_KEY")
    print("   - HUGGINGFACE_API_KEY") 
    print("   - ANTHROPIC_API_KEY")
    print()
    
    # 检查API密钥
    generator = SentenceGenerator()
    if not any([generator.openai_api_key, generator.huggingface_api_key, generator.anthropic_api_key]):
        print("⚠️  警告: 未检测到API密钥，将使用备用方案")
        print("💡 提示: 设置API密钥可获得更好的例句质量")
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
        
        # 使用API生成例句
        new_sentence = generator.generate_sentence(word, translation)
        data[i]['sentence'] = new_sentence
        
        print(f"  例句: {new_sentence}")
        print()
        
        # 添加延迟以避免API限制
        time.sleep(1.0)
    
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
    generate_sentences_with_api() 