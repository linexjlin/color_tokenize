import html
import colorsys
from pathlib import Path
from tokenizers import Tokenizer

_tokenizer = None

def load_tokenizer(model_dir: str | Path = ".") -> Tokenizer:
    """惰性加载 tokenizer.json"""
    global _tokenizer
    if _tokenizer is None:
        tokenizer_path = Path(model_dir) / "tokenizer.json"
        if not tokenizer_path.exists():
            raise FileNotFoundError(f"错误：在 '{model_dir}' 目录下找不到 'tokenizer.json'。")
        _tokenizer = Tokenizer.from_file(str(tokenizer_path))
    return _tokenizer

def text_to_tokens(text: str, model_dir: str | Path = ".") -> list[tuple[int, str]]:
    """
    把文字 → [(token_id, token_str)]
    """
    tok = load_tokenizer(model_dir)
    encoding = tok.encode(text, add_special_tokens=True)
    ids = encoding.ids
    tokens = [tok.decode([tid]) for tid in ids]
    return list(zip(ids, tokens))

def text_to_tokens_with_color(text: str, model_dir: str | Path = ".") -> str:
    """
    把文字 → 带颜色标记和上标 ID 的 HTML 文本。
    """
    tok = load_tokenizer(model_dir)
    vocab_size = tok.get_vocab_size()
    
    tokens_with_ids = text_to_tokens(text, model_dir)
    
    html_parts = []
    
    for tid, tstr in tokens_with_ids:
        escaped_tstr = html.escape(tstr)
        hue = (tid / vocab_size) * 0.67
        lightness, saturation = 0.90, 0.85
        rgb_float = colorsys.hls_to_rgb(hue, lightness, saturation)
        rgb_int = tuple(int(c * 255) for c in rgb_float)
        hex_color = f"#{rgb_int[0]:02x}{rgb_int[1]:02x}{rgb_int[2]:02x}"
        
        # --- 修改此处生成新的 HTML 结构 ---
        # 使用一个外层 span 作为容器，内部包含上标 ID 和 token 文本
        span_tag = (
            f'<span class="token" style="background-color: {hex_color};">'
            f'<sup class="token-id">{tid}</sup>' # 将 ID 作为上标
            f'{escaped_tstr}'
            f'</span>'
        )
        html_parts.append(span_tag)
        
    return "".join(html_parts)

# --------------- 演示 ---------------
if __name__ == "__main__":
    try:
        text_for_demo = "Hello 世界! Welcome to the world of tokenization."
        
        # --- 演示 1：原始文本输出 (保持不变) ---
        print("--- 原始 Token 输出 ---")
        for tid, tstr in text_to_tokens(text_for_demo):
            print(f"{tid:>5} | {tstr}")

        # --- 演示 2：生成带颜色和上标 ID 的 HTML ---
        print("\n" + "="*30)
        print("--- 生成带颜色标记和上标 ID 的 HTML ---")
        
        html_output = text_to_tokens_with_color(text_for_demo)
        
        # --- 修改此处 CSS 以支持上标样式 ---
        full_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Token Visualization</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 2.2; font-size: 16px; padding: 20px; }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        div {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; background-color: #fdfdfd; }}
        
        /* Token 容器样式 */
        .token {{
            position: relative; /* 为内部绝对定位的上标提供锚点 */
            display: inline-block;
            padding: 4px 6px;
            margin: 10px 3px 3px 3px; /* 为上标留出顶部空间 */
            border-radius: 5px;
            white-space: pre-wrap; /* 保证空格等能正确换行 */
        }}
        .token:hover {{
            outline: 2px solid #555;
        }}
        
        /* Token ID 上标样式 */
        .token-id {{
            position: absolute;
            top: -1.4em; /* 定位到容器的上方 */
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 0.7em;
            color: #666;
            font-weight: normal;
            /* 覆盖 <sup> 标签的默认垂直对齐，以便精确定位 */
            vertical-align: baseline; 
        }}
    </style>
</head>
<body>
    <h1>Token Visualization</h1>
    <div>{html_output}</div>
</body>
</html>
"""
        output_filename = "token_visualization_with_id.html"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(full_html)
            
        print(f"成功！结果已保存到 '{output_filename}'。请在你的浏览器中打开此文件查看效果。")

    except FileNotFoundError as e:
        print(e)
        print("这是一个演示，你需要一个实际的 'tokenizer.json' 文件才能运行。")
