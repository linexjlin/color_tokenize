from flask import Flask, request, jsonify
import html
import colorsys
from pathlib import Path
from tokenizers import Tokenizer
import os

app = Flask(__name__)

# Global tokenizer cache
tokenizers_cache = {}

def get_available_tokenizers():
    """Get list of available tokenizer directories"""
    tokenizers_dir = Path("./tokenizers")
    if not tokenizers_dir.exists():
        return []
    
    modes = []
    for item in tokenizers_dir.iterdir():
        if item.is_dir() and (item / "tokenizer.json").exists():
            modes.append(item.name)
    return sorted(modes)

def load_tokenizer_by_mode(mode_name: str) -> Tokenizer:
    """Load tokenizer for a specific mode"""
    if mode_name in tokenizers_cache:
        return tokenizers_cache[mode_name]
    
    tokenizer_path = Path("./tokenizers") / mode_name / "tokenizer.json"
    if not tokenizer_path.exists():
        raise FileNotFoundError(f"Tokenizer not found for mode: {mode_name}")
    
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    tokenizers_cache[mode_name] = tokenizer
    return tokenizer

def text_to_tokens_with_mode(text: str, mode_name: str) -> tuple[str, int]:
    """
    Convert text to colored HTML tokens using specified mode
    Returns tuple of (html_output, token_count)
    """
    tokenizer = load_tokenizer_by_mode(mode_name)
    vocab_size = tokenizer.get_vocab_size()
    
    # Encode text
    encoding = tokenizer.encode(text, add_special_tokens=True)
    ids = encoding.ids
    tokens = [tokenizer.decode([tid]) for tid in ids]
    
    html_parts = []
    
    for tid, tstr in zip(ids, tokens):
        escaped_tstr = html.escape(tstr)
        hue = (tid / vocab_size) * 0.67
        lightness, saturation = 0.90, 0.85
        rgb_float = colorsys.hls_to_rgb(hue, lightness, saturation)
        rgb_int = tuple(int(c * 255) for c in rgb_float)
        hex_color = f"#{rgb_int[0]:02x}{rgb_int[1]:02x}{rgb_int[2]:02x}"
        
        span_tag = (
            f'<span class="token" style="background-color: {hex_color};">'
            f'<sup class="token-id">{tid}</sup>'
            f'{escaped_tstr}'
            f'</span>'
        )
        html_parts.append(span_tag)
    
    return "".join(html_parts), len(tokens)

@app.route('/api/modes', methods=['GET'])
def get_modes():
    """Get list of available tokenization modes"""
    try:
        modes = get_available_tokenizers()
        return jsonify({
            "modes": modes,
            "count": len(modes)
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/tokenized', methods=['GET'])
def get_tokenized():
    """Get colored HTML representation of text"""
    try:
        text = request.args.get('text', '')
        mode = request.args.get('mode', '')
        
        if not text:
            return jsonify({
                "error": "Missing required parameter: text"
            }), 400
        
        if not mode:
            return jsonify({
                "error": "Missing required parameter: mode"
            }), 400
        
        available_modes = get_available_tokenizers()
        if mode not in available_modes:
            return jsonify({
                "error": f"Invalid mode: {mode}. Available modes: {available_modes}"
            }), 400
        
        html_output, token_count = text_to_tokens_with_mode(text, mode)
        
        return jsonify({
            "text": text,
            "mode": mode,
            "html": html_output,
            "token_count": token_count
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "Color Tokenize API",
        "version": "1.0.0",
        "endpoints": {
            "/api/modes": "GET - List available tokenization modes",
            "/api/tokenized": "GET - Get colored HTML tokens for text"
        }
    })

@app.route('/', methods=['GET'])
def serve_html():
    """Serve the HTML client at root path"""
    return open('index.html').read()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)