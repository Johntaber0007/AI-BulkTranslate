@echo off
set base_url=https://generativelanguage.googleapis.com/v1beta/openai/
set API_KEY=YOUR_API_KEY_HERE
set input_file=input.txt
set output_file=output.txt
set model=gemini-2.0-flash-001
set role=You are a professional English to Thai translator.
set prompt=Translate text from English to Thai without explanation.
set temperature=0.0
set pattern=
python AI-BulkTranslate.py "%base_url%" "%API_KEY%" "%input_file%" "%output_file%" "%model%" "%role%" "%prompt%" "%temperature%" "%pattern%"
pause
