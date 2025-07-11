import json
import eng_to_ipa as ipa

with open('school.list.2.json', encoding='utf-8') as f:
    data = json.load(f)

for w in data:
    ipa_str = ipa.convert(w['character']).strip()
    w['pinyin'] = ipa_str if ipa_str and ipa_str != w['character'] else ''

with open('school.list.2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2) 