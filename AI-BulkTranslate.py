import re
import sys
import time
from openai import OpenAI

if len(sys.argv) < 10:
    print("Usage: python AI-BulkTranslate.py <base_url> <api_key> <input_file> <output_file> <model> <role> <prompt> <temperature> <pattern>")
    sys.exit(1)

base_url = sys.argv[1]
api_key = sys.argv[2]
input_file = sys.argv[3]
output_file = sys.argv[4]
model = sys.argv[5]
role = sys.argv[6]
prompt = sys.argv[7]
temperature = float(sys.argv[8])
pattern = sys.argv[9].strip().replace("^|", "|").replace("^<", "<").replace("^>", ">")

client = OpenAI(api_key=api_key, base_url=base_url)

def gemini_translate(text):
    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": f"{prompt}\n{text}"}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content.strip().replace("\n", " ")
        except Exception as e:
            if "network error" in str(e).lower() or "rate limit" in str(e).lower():
                wait_time = 300
                print(f"Network issue detected. Waiting {wait_time // 60} minutes before retrying...")
                time.sleep(wait_time)
            else:
                raise e

def translate_with_exceptions(text):
    if not pattern:
        return gemini_translate(text)

    matches = list(re.finditer(pattern, text))
    tokens = {}
    temp_text = text

    for i, match in enumerate(matches):
        token = f"<TOKEN_{i}>"
        tokens[token] = match.group(0)
        temp_text = temp_text.replace(match.group(0), token, 1)
    
    translated_text = gemini_translate(temp_text)

    for token, original_text in tokens.items():
        translated_text = re.sub(rf"({re.escape(token)})([\.\,\!\?\…])", rf"{original_text}\2", translated_text)
        translated_text = translated_text.replace(token, original_text)

    return translated_text

def translate_txt():
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = [line.rstrip() for line in infile]

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines([line + "\n" for line in lines])

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        while True:
            try:
                translated_line = translate_with_exceptions(line)
                break
            except Exception as e:
                print(f"Error: {e}. Retrying in 5 minutes...")
                time.sleep(300)

        with open(output_file, 'r+', encoding='utf-8') as outfile:
            output_lines = outfile.readlines()
            output_lines[i] = translated_line.strip() + "\n"
            outfile.seek(0)
            outfile.writelines(output_lines)
            outfile.truncate()

        print(f"Translated {i + 1}/{len(lines)} lines: {line} -> {translated_line}")

    print(f"Translation completed! Output saved to {output_file}")

translate_txt()
