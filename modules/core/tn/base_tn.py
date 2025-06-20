import html
import os
import platform
import re

import emojiswitch
import ftfy

from modules.core.tn.TNPipeline import GuessLang, TNPipeline
from modules.repos_static.zh_normalization.text_normlization import TextNormalizer
from modules.utils.HomophonesReplacer import HomophonesReplacer
from modules.utils.html import remove_html_tags as _remove_html_tags
from modules.utils.markdown import markdown_to_text

BaseTN = TNPipeline()

# ------- UTILS ---------


def is_markdown(text):
    markdown_patterns = [
        r"(^|\s)#[^#]",  # 标题
        r"\*\*.*?\*\*",  # 加粗
        r"\*.*?\*",  # 斜体
        r"!\[.*?\]\(.*?\)",  # 图片
        r"\[.*?\]\(.*?\)",  # 链接
        r"`[^`]+`",  # 行内代码
        r"```[\s\S]*?```",  # 代码块
        r"(^|\s)\* ",  # 无序列表
        r"(^|\s)\d+\. ",  # 有序列表
        r"(^|\s)> ",  # 引用
        r"(^|\s)---",  # 分隔线
    ]

    for pattern in markdown_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True

    return False


character_map = {
    "：": "，",
    "；": "，",
    "！": "。",
    "（": "，",
    "）": "，",
    "【": "，",
    "】": "，",
    "『": "，",
    "』": "，",
    "「": "，",
    "」": "，",
    "《": "，",
    "》": "，",
    "－": "，",
    ":": ",",
    ";": ",",
    "!": ".",
    "(": ",",
    ")": ",",
    "[": ",",
    "]": ",",
    ">": ",",
    "<": ",",
    "-": ",",
    "~": " ",
    "～": " ",
    "/": " ",
    "·": " ",
}

# 多字符替换映射（需要单独处理）
multi_char_replacements = {
    "'": " ",
    """: " ",
    "'": " ",
    """: " ",
    '"': " ",
    "'": " ",
}

# -----------------------


@BaseTN.block()
def html_unescape(text: str, guess_lang: GuessLang):
    text = html.unescape(text)
    text = html.unescape(text)
    return text


@BaseTN.block()
def fix_text(text: str, guess_lang: GuessLang):
    return ftfy.fix_text(text=text)


@BaseTN.block()
def apply_markdown_to_text(text: str, guess_lang: GuessLang):
    if is_markdown(text):
        text = markdown_to_text(text)
    return text


@BaseTN.block()
def remove_html_tags(text: str, guess_lang: GuessLang):
    return _remove_html_tags(text)


# 将 "xxx" => \nxxx\n
# 将 'xxx' => \nxxx\n
@BaseTN.block()
def replace_quotes(text: str, guess_lang: GuessLang):
    repl = r"\n\1\n"
    patterns = [
        ['"', '"'],
        ["'", "'"],
        [""", """],
        ["'", "'"],
    ]
    for p in patterns:
        # 确保模式有两个元素（开始和结束引号）
        if len(p) >= 2:
            try:
                # 使用更安全的正则表达式
                start_quote = re.escape(p[0])
                end_quote = re.escape(p[1])
                pattern = f"({start_quote}[^{start_quote}{end_quote}]*?{end_quote})"
                text = re.sub(pattern, repl, text)
            except (re.error, IndexError) as e:
                # 如果正则表达式出错或索引错误，跳过这个模式
                continue
    return text


# ---- main normalize ----


@BaseTN.block(name="tx_zh", enabled=True)
def tx_normalize(text: str, guss_lang: GuessLang):
    if guss_lang.zh_or_en != "zh":
        return text
    # NOTE: 这个是魔改过的 TextNormalizer 来自 PaddlePaddle
    tx = TextNormalizer()
    # NOTE: 为什么要分行？因为我们需要保留 "\n" 作为 chunker 的分割信号
    lines = [line for line in text.split("\n") if line.strip() != ""]
    texts: list[str] = []
    for line in lines:
        ts = tx.normalize(line)
        texts.append("".join(ts))
    return "\n".join(texts)


@BaseTN.block(name="wetext_en", enabled=True)
def wetext_normalize(text: str, guss_lang: GuessLang):
    # NOTE: wetext 依赖 pynini 无法在 windows 和 macOS 上安装，所以这里只在 linux 上启用
    if os.name == "nt" or platform.system() == "Darwin":
        # 在 Windows 和 macOS 上跳过英文文本归一化
        return text
    if guss_lang.zh_or_en == "en":
        try:
            from pywrapfst import FstOpError
            from tn.english.normalizer import Normalizer as EnNormalizer

            en_tn_model = EnNormalizer(overwrite_cache=False)
            return en_tn_model.normalize(text)
        except (ImportError, FstOpError):
            # NOTE: 如果导入失败或 tn 出错，直接返回原文本
            pass
    return text


# ---- end main normalize ----


@BaseTN.block()
def apply_character_map(text: str, guess_lang: GuessLang):
    # 首先处理单字符替换
    translation_table = str.maketrans(character_map)
    text = text.translate(translation_table)
    
    # 然后处理多字符替换
    for old_char, new_char in multi_char_replacements.items():
        text = text.replace(old_char, new_char)
    
    return text


@BaseTN.block()
def apply_emoji_map(text: str, guess_lang: GuessLang):
    return emojiswitch.demojize(text, delimiters=("", ""), lang=guess_lang.zh_or_en)


@BaseTN.block()
def insert_spaces_between_uppercase(text: str, guess_lang: GuessLang):
    # 使用正则表达式在每个相邻的大写字母之间插入空格
    return re.sub(
        r"(?<=[A-Z])(?=[A-Z])|(?<=[a-z])(?=[A-Z])|(?<=[\u4e00-\u9fa5])(?=[A-Z])|(?<=[A-Z])(?=[\u4e00-\u9fa5])",
        " ",
        text,
    )


homo_replacer = HomophonesReplacer(
    map_file_path="./modules/repos_static/ChatTTS/ChatTTS/res/homophones_map.json"
)


@BaseTN.block()
def replace_homophones(text: str, guess_lang: GuessLang):
    if guess_lang.zh_or_en == "zh":
        text = homo_replacer.replace(text)
    return text 