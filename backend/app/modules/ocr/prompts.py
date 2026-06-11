OCR_PROMPT = """你是一个小学错题本助手。请识别图片中的试卷/作业内容，按以下 JSON 格式返回：

{{
  "questions": [
    {{
      "number": "1",
      "content": "题目的文字内容，数学公式用 LaTeX 格式",
      "student_answer": "学生写的答案（如空白则为空字符串）",
      "blank_exists": true
    }}
  ],
  "subject_type": "数学/语文/英语"
}}

注意：
- 逐题拆解，不要遗漏任何一题
- 学生手写答案要尽力识别
- 数学公式用 LaTeX：$32 \\times 15 = ?$
- 如果学生没有作答，student_answer 留空字符串"""

CORRECTION_PROMPT = """你是一个小学错题本助手。请分析以下题目，按 JSON 格式返回判错结果：

{{
  "is_correct": true/false,
  "correct_answer": "标准答案",
  "error_type": "正确/粗心/概念不清/审题错误/计算错误/未作答",
  "analysis": "用小学生能理解的语言写出解题步骤，要求详细、耐心、鼓励性",
  "knowledge_point": "本题所属知识点名称"
}}

题目：{question_content}
学生答案：{student_answer}"""
