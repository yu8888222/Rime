import re

# 小鹤双拼映射表
shengmu = {
    'ch': 'i', 'sh': 'u', 'zh': 'v'
}

yunmu = {
    'iu': 'q', 'ia': 'x', 'ua': 'x', 'er': 'er', 'üe': 't', 'ue': 't', 've': 't',
    'in': 'b', 'uai': 'k', 'ing': 'k', 'uo': 'o', 'un': 'y', 'iong': 's', 'ong': 's',
    'ian': 'm', 'iang': 'l', 'uang': 'l', 'en': 'f', 'eng': 'g', 'ang': 'h',
    'an': 'j', 'ao': 'c', 'ai': 'd', 'ei': 'w', 'ie': 'p', 'ou': 'z', 'ui': 'v', 'ü': 'v',
    'uan': 'r', 'iao': 'n',
    'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u'
}

zero_shengmu_map = {
    'a': 'aa', 'ai': 'ai', 'an': 'an', 'ang': 'ah', 'ao': 'ao',
    'e': 'ee', 'ei': 'ei', 'en': 'en', 'eng': 'eg', 'er': 'er',
    'o': 'oo', 'ou': 'ou'
}

def pinyin_to_xiaohe(pinyin):
    pinyin = pinyin.lower()
    
    # 零声母直接映射
    if pinyin in zero_shengmu_map:
        return zero_shengmu_map[pinyin]
        
    # 特殊的整体认读音节/零声母处理 (y, w开头)
    # y开头
    if pinyin.startswith('y'):
        if pinyin == 'yi': return 'yi'
        if pinyin == 'yin': return 'yb'
        if pinyin == 'ying': return 'yk'
        if pinyin == 'yu': return 'yu'
        if pinyin == 'yue': return 'yt'
        if pinyin == 'yuan': return 'yr'
        if pinyin == 'yun': return 'yy'
        if pinyin == 'yong': return 'ys'
        if pinyin == 'ya': return 'yx'
        if pinyin == 'yan': return 'yj'
        if pinyin == 'yang': return 'yh'
        if pinyin == 'yao': return 'yc'
        if pinyin == 'ye': return 'ye'
        if pinyin == 'you': return 'yz'
        
    # w开头
    if pinyin.startswith('w'):
        if pinyin == 'wu': return 'wu'
        if pinyin == 'wa': return 'wa'
        if pinyin == 'wai': return 'wd'
        if pinyin == 'wan': return 'wj'
        if pinyin == 'wang': return 'wh'
        if pinyin == 'wei': return 'ww'
        if pinyin == 'wen': return 'wf'
        if pinyin == 'weng': return 'wg'
        if pinyin == 'wo': return 'wo'
    
    # 常规声韵母拆分
    sm = ''
    ym = ''
    
    if pinyin.startswith(('ch', 'sh', 'zh')):
        sm = pinyin[:2]
        ym = pinyin[2:]
    else:
        sm = pinyin[0]
        ym = pinyin[1:]
        
    # 如果没有韵母（比如单字母输入），则补全
    if not ym:
        ym = sm
        
    # 转换声母
    if sm in shengmu:
        sm = shengmu[sm]
        
    # 特殊处理：j,q,x 后面的 u 实际是 ü
    if sm in ['j', 'q', 'x'] and ym.startswith('u'):
        ym = 'v' + ym[1:]
        if ym == 've': ym = 'ue'
        if ym == 'van': ym = 'uan'
        if ym == 'vn': ym = 'un'
    
    # 转换韵母
    if ym in yunmu:
        ym = yunmu[ym]
    elif ym == 'v':
        ym = 'v'
        
    return sm + ym

with open('emoji.dict.yaml.bak', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() == '' or line.startswith('#') or line.startswith('---') or line.startswith('...') or ':' in line or line.startswith('  -'):
        new_lines.append(line)
        continue
        
    parts = line.strip().split('\t')
    if len(parts) >= 2:
        emoji = parts[0]
        pinyin_str = parts[1]
        pinyins = pinyin_str.split('\'')
        xiaohe_pinyins = [pinyin_to_xiaohe(py) for py in pinyins]
        # 使用单引号连接，保持原格式
        new_code = '\''.join(xiaohe_pinyins)
        
        if len(parts) > 2:
            new_lines.append(f"{emoji}\t{new_code}\t{parts[2]}\n")
        else:
            new_lines.append(f"{emoji}\t{new_code}\n")
    else:
        new_lines.append(line)

with open('emoji.dict.yaml', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Conversion done.')
