import os
import re


CJK_4_RE = re.compile(r"^[\u4e00-\u9fff]{4}$")


def iter_dict_lines(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#") or "\t" not in line:
                continue
            yield line.split("\t")


def load_idiom_data(path: str) -> dict[str, dict]:
    data = {}
    for parts in iter_dict_lines(path):
        if len(parts) < 3:
            continue
        word = parts[0].strip()
        if not CJK_4_RE.match(word):
            continue

        # Parse pinyin from idiom.dict.yaml format
        # Format: "pinyin;... pinyin;... pinyin;... pinyin;..."
        pinyin_segments = parts[1].strip().split(" ")
        # Filter out empty segments (e.g. trailing spaces)
        pinyin_segments = [s for s in pinyin_segments if s]
        
        if len(pinyin_segments) != 4:
            continue

        try:
            # Extract pinyin (first item before ;) and then first letter
            # Example: "hou;iz;..." -> "hou" -> "h"
            code_chars = []
            for seg in pinyin_segments:
                pinyin = seg.split(";")[0]
                if pinyin:
                    code_chars.append(pinyin[0])
            
            if len(code_chars) != 4:
                continue
                
            code = "".join(code_chars).lower()
        except IndexError:
            continue

        if len(code) != 4 or not code.isalpha() or not code.islower():
            continue

        try:
            weight = int(parts[2])
        except ValueError:
            weight = 0

        data[word] = {"code": code, "weight": weight}
    return data


def load_word_set(path: str) -> set[str]:
    words: set[str] = set()
    for parts in iter_dict_lines(path):
        w = parts[0].strip()
        if CJK_4_RE.match(w):
            words.add(w)
    return words


def load_conflict_codes() -> set[str]:
    conflict: set[str] = set()

    for file_name in ["8105.dict.yaml", "41448.dict.yaml"]:
        path = os.path.join("cn_dicts_moqi", file_name)
        for parts in iter_dict_lines(path):
            word = parts[0]
            if len(word) != 1:
                continue
            pinyin = parts[1].strip()
            if len(pinyin) < 5:
                continue
            code = pinyin[0] + pinyin[1] + pinyin[3] + pinyin[4]
            if len(code) == 4 and code.isalpha() and code.islower():
                conflict.add(code)

    for file_name in ["base.dict.yaml", "ext.dict.yaml"]:
        path = os.path.join("cn_dicts_moqi", file_name)
        for parts in iter_dict_lines(path):
            if len(parts) < 3:
                continue
            word = parts[0]
            if len(word) != 2:
                continue
            try:
                freq = int(parts[2])
            except ValueError:
                continue
            if freq < 998:
                continue
            pinyin = parts[1].split(" ")
            if len(pinyin) != 2:
                continue
            code = (pinyin[0][:2] + pinyin[1][:2]).lower()
            if len(code) == 4 and code.isalpha() and code.islower():
                conflict.add(code)

    return conflict


def is_good_phrase(word: str, banned_words: set[str], excluded_words: set[str]) -> bool:
    if word in excluded_words:
        return False
    if word in banned_words:
        return False

    bad_chars = set("的了着过吗呢吧啊呀哦嗯么嘛啦哇咯喽呗兮")
    if any(ch in bad_chars for ch in word):
        return False

    if word and word[0] in {"阿", "爱", "奥", "伊", "欧", "埃", "艾"} and word[-1] in {"亚", "巴", "坦", "斯", "尔", "夫", "卡", "德", "罗", "姆", "纳", "恩"}:
        return False

    bad_substrings = (
        "越来越",
        "绝大",
        "多数",
        "重要",
        "不用",
        "不太",
        "完全",
        "不同",
        "相对",
        "总体",
        "对我",
        "这样",
        "事项",
        "日常",
        "搜索",
        "引擎",
        "不确定",
        "商业",
        "银行",
        "事业",
        "单位",
        "氧化",
        "化碳",
        "之一",
        "最近",
        "几年",
        "现在",
        "看来",
        "据我",
        "怎样",
        "才能",
        "打个",
        "伙伴",
        "法规",
        "咨询",
        "执照",
        "化学",
        "物理",
        "学家",
        "资源",
        "分子",
        "五险",
        "一金",
        "格拉",
        "拉底",
        "这个",
        "那个",
        "一个",
        "一种",
        "一些",
        "一点",
        "一下",
        "一遍",
        "一次",
        "我们",
        "你们",
        "他们",
        "她们",
        "它们",
        "自己",
        "别人",
        "如何",
        "怎么",
        "什么",
        "多少",
        "哪里",
        "为何",
        "为啥",
        "一直",
        "目前",
        "至今",
        "今天",
        "明天",
        "昨天",
        "今年",
        "去年",
        "明年",
        "当时",
        "此时",
        "可以",
        "不能",
        "不会",
        "不是",
        "没有",
        "还有",
        "已经",
        "正在",
        "需要",
        "应该",
        "可能",
        "一定",
        "必须",
        "是否",
        "如果",
        "因为",
        "所以",
        "但是",
        "不过",
        "然后",
        "同时",
        "认为",
        "觉得",
        "知道",
        "喜欢",
        "希望",
        "建议",
        "总结",
        "举例",
        "例子",
        "比如",
        "例如",
        "参考",
        "介绍",
        "开始",
        "原因",
        "结果",
        "世界",
        "城市",
        "小时",
        "分钟",
        "秒钟",
        "时间",
        "年代",
        "世纪",
        "时期",
        "问题",
        "事情",
        "地方",
        "方面",
        "情况",
        "方式",
        "方法",
        "能力",
        "水平",
        "程度",
        "关系",
        "影响",
        "变化",
        "增长",
        "减少",
        "提高",
        "降低",
        "选择",
        "决定",
        "解决",
        "处理",
        "实现",
        "完成",
        "支持",
        "安装",
        "更新",
        "维护",
        "检查",
        "确认",
        "使用",
        "输入",
        "输出",
        "下载",
        "上传",
        "注册",
        "登录",
        "公司",
        "企业",
        "政府",
        "国家",
        "人民",
        "社会",
        "经济",
        "市场",
        "资本",
        "投资",
        "金融",
        "管理",
        "工作",
        "学习",
        "考试",
        "毕业",
        "论文",
        "证书",
        "标准",
        "规则",
        "系统",
        "软件",
        "硬件",
        "程序",
        "代码",
        "网络",
        "电脑",
        "手机",
        "视频",
        "电影",
        "音乐",
        "小说",
        "游戏",
        "体育",
        "教育",
        "学校",
        "大学",
        "学院",
        "产品",
        "运营",
        "方案",
        "服务",
        "用户",
        "客户",
        "需求",
        "功能",
        "数据",
        "信息",
        "技术",
        "开发",
        "设计",
        "项目",
        "版本",
        "平台",
        "接口",
        "环境",
        "协议",
        "导图",
        "产权",
        "商务",
        "智能",
        "斯坦",
        "巴巴",
        "学者",
        "做事",
    )
    return not any(sub in word for sub in bad_substrings)


def main() -> None:
    max_keep = 1000

    # 1. Load idiom data (word -> {code, weight}) from idiom.dict.yaml
    idiom_data = load_idiom_data(os.path.join("cn_dicts_cell", "idiom.dict.yaml"))
    
    # 2. Load exclusions
    excluded_words = load_word_set(os.path.join("cn_dicts_cell", "place.dict.yaml")) | load_word_set(
        os.path.join("cn_dicts_cell", "name.dict.yaml")
    )
    conflict_codes = load_conflict_codes()

    banned_words: set[str] = {
        "阿里巴巴",
        "澳大利亚",
        "爱因斯坦",
        "冯诺依曼",
        "瑞文戴尔",
        "前赤壁赋",
    }

    # 3. Update weights using base/ext frequencies if available
    for file_name in ["base.dict.yaml", "ext.dict.yaml"]:
        path = os.path.join("cn_dicts_moqi", file_name)
        for parts in iter_dict_lines(path):
            if len(parts) < 3:
                continue
            word = parts[0]
            if word in idiom_data:
                try:
                    freq = int(parts[2])
                    # Update weight if freq from base/ext is higher (it usually is for common words)
                    # or simply overwrite to reflect usage frequency better.
                    if freq > idiom_data[word]["weight"]:
                        idiom_data[word]["weight"] = freq
                except ValueError:
                    pass

    # 4. Select best idioms
    best_by_code: dict[str, tuple[str, int]] = {}
    
    for word, info in idiom_data.items():
        code = info["code"]
        weight = info["weight"]

        if code in conflict_codes:
            continue
        
        if not is_good_phrase(word, banned_words=banned_words, excluded_words=excluded_words):
            continue

        existing = best_by_code.get(code)
        if existing is None or weight > existing[1]:
            best_by_code[code] = (word, weight)

    # 5. Sort and write
    selected = sorted(best_by_code.items(), key=lambda kv: kv[1][1], reverse=True)[:max_keep]
    out_path = os.path.join("custom_phrase", "custom_phrase_super_4jian_no_conflict.txt")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for code, (word, _freq) in selected:
            f.write(f"{word}\t{code}\n")


if __name__ == "__main__":
    main()
