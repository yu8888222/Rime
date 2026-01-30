import os
import re


CJK_3_RE = re.compile(r"^[\u4e00-\u9fff]{3}$")


def iter_dict_lines(path: str):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#") or "\t" not in line:
                continue
            yield line.split("\t")


def load_word_set(path: str) -> set[str]:
    words: set[str] = set()
    for parts in iter_dict_lines(path):
        w = parts[0].strip()
        # Clean up word (sometimes they have comments or extra chars)
        if CJK_3_RE.match(w):
            words.add(w)
    return words


def is_good_phrase(word: str, banned_words: set[str], excluded_words: set[str]) -> bool:
    if word in excluded_words:
        return False
    if word in banned_words:
        return False

    # Filter bad characters (particles, etc.)
    bad_chars = set("的了着过吗呢吧啊呀哦嗯么嘛啦哇咯喽呗兮")
    if any(ch in bad_chars for ch in word):
        return False

    # Filter transliterated names/places patterns
    # Starts with common foreign name chars
    starts_with = {"阿", "爱", "奥", "伊", "欧", "埃", "艾", "安", "昂", "巴", "比", "伯", "布", "达", "德", "杜", "费", "弗", "格", "哈", "赫", "加", "贾", "杰", "卡", "凯", "科", "克", "肯", "库", "拉", "莱", "兰", "劳", "雷", "里", "利", "林", "卢", "鲁", "路", "马", "麦", "曼", "梅", "蒙", "米", "摩", "莫", "穆", "纳", "尼", "诺", "帕", "佩", "皮", "普", "奇", "齐", "乔", "切", "萨", "桑", "瑟", "森", "莎", "苏", "索", "塔", "泰", "坦", "特", "提", "蒂", "托", "瓦", "万", "威", "韦", "维", "文", "沃", "乌", "希", "席", "夏", "辛", "休", "亚", "雅", "伊", "尤", "詹", "哲", "芝", "朱", "佐"}
    # Ends with common foreign name chars
    ends_with = {"亚", "巴", "坦", "斯", "尔", "夫", "卡", "德", "罗", "姆", "纳", "恩", "利", "兰", "达", "廷", "伯", "顿", "奇", "索", "格", "克", "特", "曼", "森", "林", "瓦", "普", "莱", "雷", "蒙", "佩", "宾", "吉", "福", "多", "冈", "哥", "科", "平", "里", "塞", "维", "韦", "伊", "莎", "莉", "娜", "妮", "娃", "耶", "基", "诺", "捷", "波", "治", "梅", "纽", "布", "塔", "蒂", "士", "瑞", "兹", "勒"}
    
    if word and word[0] in starts_with and word[-1] in ends_with:
        # Heuristic: if start and end are common transliteration chars, likely a name/place
        # But be careful with common words like "爱国者" (starts with 爱, ends with 者 - not in ends_with)
        # "奥地利" (starts with 奥, ends with 利) -> Filtered
        # "爱尔兰" (starts with 爱, ends with 兰) -> Filtered
        # "阿根廷" (starts with 阿, ends with 廷) -> Filtered
        # "俄罗斯" (starts with 俄 - maybe add 俄) -> Filtered if I add 俄
        return False

    bad_substrings = (
        "先生", "小姐", "女士", "同志", "经理", "主任", "教授", "老师", "医生", # Titles
        "市长", "省长", "部长", "总统", "总理", "主席",
        "公司", "集团", "银行", "大学", "学院", "中学", "小学", # Institutions
        "街道", "路", "区", "县", "市", "省", # Places
        "主义", "思想", "理论", "精神",
        "中国", "美国", "日本", "英国", "法国", "德国", "俄国", # Countries
        "北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", # Cities
    )
    
    if any(sub in word for sub in bad_substrings):
        return False
        
    return True


def main() -> None:
    max_keep = 1000

    # 1. Load exclusions (Names and Places)
    excluded_words = set()
    excluded_words |= load_word_set(os.path.join("cn_dicts_cell", "name.dict.yaml"))
    excluded_words |= load_word_set(os.path.join("cn_dicts_cell", "name2.dict.yaml"))
    excluded_words |= load_word_set(os.path.join("cn_dicts_cell", "place.dict.yaml"))
    excluded_words |= load_word_set(os.path.join("cn_dicts_cell", "luna_pinyin.place.dict.yaml"))
    excluded_words |= load_word_set(os.path.join("cn_dicts_cell", "geography.dict.yaml"))
    excluded_words |= load_word_set(os.path.join("cn_dicts_cell", "history.dict.yaml"))
    
    # Manual blacklist for things observed in the file or known bad ones
    banned_words = {
        "爱德华", "奥地利", "爱尔兰", "阿凡达", "阿根廷", "阿拉伯", "奥斯卡", "阿森纳", "奥特曼",
        "贝多芬", "巴菲特", "蝙蝠侠", "贝吉塔", "宝可梦", "布鲁斯", "柏拉图", "俾斯麦", "博物馆",
        "杜兰特", "费德勒", "福克斯", "菲律宾", "弗兰克", "法拉利", "方舟子",
        "郭德纲", "高尔夫", "高句丽", "郭敬明", "郭沫若", "宫崎骏", "钢铁侠", "高晓松",
        "哈尔滨", "华尔街", "黑格尔", "海明威", "霍去病", "汉武帝", "海贼王",
        "基督教", "甲骨文", "加拿大", "金球奖", "金字塔",
        "卡夫卡", "卡罗拉", "卡西欧",
        "勒布朗", "刘慈欣", "罗大佑", "令狐冲", "流川枫", "林俊杰", "梁静茹", "刘强东", "洛杉矶", "利物浦", "罗永浩", "林忆莲", "李宗盛",
        "麦当劳", "迈克尔", "麦克风", "马克思", "马里奥", "美联储", "马拉松", "牧马人", "明日香", "马斯克", "摩托车", "莫扎特", "毛主席", "墨西哥", "毛泽东",
        "纳达尔", "尼克斯", "内马尔", "拿破仑",
        "普鲁士", "葡萄牙",
        "乔布斯", "切尔西", "秦始皇", "钱学森", "犬夜叉",
        "日本人", "人民币", "任天堂",
        "苏炳添", "苏东坡", "塞尔达", "苏格兰", "三国杀", "三国志", "索罗斯", "司马光", "司马迁", "司马懿", "斯坦福", "孙悟空",
        "土耳其", "特朗普", "托马斯", "太平洋", "特斯拉",
        "沃尔沃", "王安石", "王家卫", "王力宏", "王小波", "吴亦凡", "五月天", "武则天",
        "星巴克", "西班牙", "新东方", "学而思", "小红书", "西蒙斯", "谢霆锋", "希特勒", "徐志摩", "肖秀荣", "西雅图",
        "袁隆平", "约基奇", "意大利", "英格兰", "亚马逊", "以色列", "英特尔", "犹太人", "优衣库", "亚洲人",
        "张三丰", "詹姆斯", "诸葛亮", "周杰伦", "中科大", "中科院", "张无忌", "张艺谋", "蜘蛛侠",
        # Add more countries/cities just in case
        "俄罗斯", "新加坡", 
    }

    best_by_code: dict[str, tuple[str, int]] = {}
    
    # Process base.dict.yaml and ext.dict.yaml
    for file_name in ["base.dict.yaml", "ext.dict.yaml"]:
        path = os.path.join("cn_dicts_moqi", file_name)
        for parts in iter_dict_lines(path):
            if len(parts) < 3:
                continue
            word = parts[0]
            
            # Filter for 3-char words
            if not CJK_3_RE.match(word):
                continue
            
            # Filter exclusions
            if not is_good_phrase(word, banned_words, excluded_words):
                continue

            try:
                freq = int(parts[2])
            except ValueError:
                continue
            
            # Minimum frequency filter to "streamline"
            if freq < 100: # Heuristic threshold
                continue

            # Generate code: 3 pinyin initials + /
            pinyin_raw = parts[1]
            # pinyin usually "a b c"
            pinyin_list = pinyin_raw.split(" ")
            if len(pinyin_list) != 3:
                continue
            
            code_initials = "".join([p[0] for p in pinyin_list]).lower()
            if not code_initials.isalpha():
                continue
                
            code = code_initials + "/"

            # Keep the one with higher frequency
            existing = best_by_code.get(code)
            if existing is None or freq > existing[1]:
                best_by_code[code] = (word, freq)

    # Sort by frequency and take top 1000
    selected = sorted(best_by_code.items(), key=lambda kv: kv[1][1], reverse=True)[:max_keep]
    
    # Output
    out_path = os.path.join("custom_phrase", "custom_phrase_super_3jian.txt")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("## 超强3简 使用deal_super_3jian.py生成\n")
        for code, (word, _freq) in selected:
            f.write(f"{word}\t{code}\n")

if __name__ == "__main__":
    main()
