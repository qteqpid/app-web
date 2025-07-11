#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time
import random
import hashlib
import uuid
from urllib.parse import quote

class YoudaoSentenceGenerator:
    def __init__(self):
        # 有道词典API配置
        self.app_key = "your_app_key"  # 需要注册有道智云获取
        self.app_secret = "your_app_secret"
        self.base_url = "https://openapi.youdao.com/api"
        
        # 备用方案：使用有道词典网页版
        self.web_url = "https://dict.youdao.com/jsonapi"
        
    def generate_with_youdao_api(self, word: str, translation: str) -> str:
        """使用有道词典API生成例句"""
        try:
            # 构建API请求参数
            salt = str(uuid.uuid1())
            curtime = str(int(time.time()))
            sign_str = self.app_key + self.truncate(word) + salt + curtime + self.app_secret
            sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
            
            params = {
                'q': word,
                'from': 'en',
                'to': 'zh-CHS',
                'appKey': self.app_key,
                'salt': salt,
                'sign': sign,
                'signType': 'v3',
                'curtime': curtime,
                'vocabId': '1',
                'strict': 'true'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                # 提取例句
                if 'basic' in result and 'exam_type' in result['basic']:
                    examples = result['basic']['exam_type']
                    if examples and len(examples) > 0:
                        # 选择第一个英文例句
                        for example in examples:
                            if example.get('en'):
                                return self.clean_sentence(example['en'])
                
                # 如果没有例句，尝试从其他字段获取
                if 'web' in result:
                    for web_item in result['web']:
                        if 'value' in web_item and len(web_item['value']) > 0:
                            # 选择包含目标单词的短语
                            for value in web_item['value']:
                                if word.lower() in value.lower():
                                    return self.clean_sentence(value)
            
            return ""
            
        except Exception as e:
            print(f"有道API调用失败: {e}")
            return ""
    
    def generate_with_youdao_web(self, word: str, translation: str) -> str:
        """使用有道词典网页版获取例句"""
        try:
            # 构建网页版请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://dict.youdao.com/',
                'Accept': 'application/json, text/plain, */*'
            }
            
            # 有道词典网页版API
            params = {
                'q': word,
                'le': 'en',
                't': int(time.time() * 1000),
                'client': 'web',
                'sign': self.generate_web_sign(word),
                'keyfrom': 'webdict'
            }
            
            response = requests.get(self.web_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                # 解析返回的JSON数据
                if 'ec' in result:
                    ec_data = result['ec']
                    
                    # 提取例句
                    if 'exam_type' in ec_data:
                        examples = ec_data['exam_type']
                        if examples and len(examples) > 0:
                            for example in examples:
                                if example.get('en'):
                                    return self.clean_sentence(example['en'])
                    
                    # 提取短语
                    if 'phrs' in ec_data:
                        phrs = ec_data['phrs']
                        if phrs and len(phrs) > 0:
                            for phr in phrs:
                                if 'en' in phr:
                                    return self.clean_sentence(phr['en'])
            
            return ""
            
        except Exception as e:
            print(f"有道网页版调用失败: {e}")
            return ""
    
    def generate_with_free_dict_api(self, word: str, translation: str) -> str:
        """使用其他免费词典API"""
        try:
            # 尝试使用免费的词典API
            apis = [
                {
                    'url': f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}',
                    'method': 'GET',
                    'headers': {},
                    'extract': lambda data: self.extract_from_free_api(data, word)
                },
                {
                    'url': f'https://api.datamuse.com/words?sp={word}&md=d',
                    'method': 'GET',
                    'headers': {},
                    'extract': lambda data: self.extract_from_datamuse(data, word)
                }
            ]
            
            for api in apis:
                try:
                    response = requests.request(
                        api['method'],
                        api['url'],
                        headers=api['headers'],
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        sentence = api['extract'](result, word)
                        if sentence:
                            return sentence
                            
                except Exception as e:
                    print(f"免费API调用失败: {e}")
                    continue
            
            return ""
            
        except Exception as e:
            print(f"免费词典API调用失败: {e}")
            return ""
    
    def extract_from_free_api(self, data, word):
        """从免费API数据中提取例句"""
        try:
            if isinstance(data, list) and len(data) > 0:
                word_data = data[0]
                if 'meanings' in word_data:
                    for meaning in word_data['meanings']:
                        if 'definitions' in meaning and len(meaning['definitions']) > 0:
                            definition = meaning['definitions'][0]['definition']
                            # 将定义转换为简单句子
                            return f"This word means {definition}."
            return ""
        except:
            return ""
    
    def extract_from_datamuse(self, data, word):
        """从Datamuse API数据中提取信息"""
        try:
            if isinstance(data, list) and len(data) > 0:
                word_info = data[0]
                if 'defs' in word_info and len(word_info['defs']) > 0:
                    definition = word_info['defs'][0]
                    return f"A {word} is {definition}."
            return ""
        except:
            return ""
    
    def generate_template_sentence(self, word: str, translation: str) -> str:
        """使用改进的模板生成例句（备用方案）"""
        # 根据中文翻译选择合适的模板
        translation_lower = translation.lower()
        
        # 动词相关
        if any(verb in translation_lower for verb in ['做', '走', '跑', '跳', '吃', '喝', '看', '听', '说', '读', '写', '买', '卖', '给', '拿', '放', '玩', '学习', '工作']):
            templates = [
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
        # 默认模板
        else:
            templates = [
                f"I like {word}.",
                f"She uses {word}.",
                f"He needs {word}.",
                f"We want {word}.",
                f"They have {word}.",
                f"My friend likes {word}.",
                f"The teacher shows {word}.",
                f"Children enjoy {word}.",
                f"People use {word}.",
                f"Everyone needs {word}."
            ]
        
        return random.choice(templates)
    
    def truncate(self, q):
        """截取字符串"""
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]
    
    def generate_web_sign(self, word):
        """生成网页版签名（简化版）"""
        # 这里是一个简化的签名生成，实际的有道签名算法更复杂
        return hashlib.md5((word + str(int(time.time()))).encode()).hexdigest()
    
    def clean_sentence(self, sentence: str) -> str:
        """清理和格式化句子"""
        if not sentence:
            return ""
        
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
        """尝试多种方法生成例句"""
        methods = [
            ('有道API', lambda: self.generate_with_youdao_api(word, translation)),
            ('有道网页版', lambda: self.generate_with_youdao_web(word, translation)),
            ('免费词典API', lambda: self.generate_with_free_dict_api(word, translation))
        ]
        
        for method_name, method_func in methods:
            print(f"  尝试使用 {method_name}...")
            result = method_func()
            if result:
                print(f"  ✅ {method_name} 生成成功")
                return result
            else:
                print(f"  ❌ {method_name} 生成失败")
        
        # 如果所有方法都失败，使用改进的模板
        print("  🔄 使用改进模板生成")
        return self.generate_template_sentence(word, translation)

def generate_sentences_with_youdao():
    """使用有道词典API生成例句"""
    
    print("🚀 开始使用有道词典API生成例句...")
    print("📝 尝试有道API、网页版和免费词典API")
    print("💡 提示: 有道API需要注册有道智云获取密钥")
    print()
    
    generator = YoudaoSentenceGenerator()
    
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
        
        # 使用有道词典API生成例句
        new_sentence = generator.generate_sentence(word, translation)
        data[i]['sentence'] = new_sentence
        
        print(f"  例句: {new_sentence}")
        print()
        
        # 添加延迟避免请求过快
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
    generate_sentences_with_youdao() 