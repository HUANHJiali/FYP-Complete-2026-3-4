import json
import os
import re
import requests
import time
import jwt
from typing import Dict, List, Any
from django.conf import settings
from comm.CommUtils import DateUtil

class AIUtils:
    """AI工具类，提供AI评分和AI自动创建题目功能"""
    
    def __init__(self):
        # 读取配置（优先环境变量，便于智谱AI和OpenAI对接）并做清洗，防止换行/引号导致 Header 无效
        raw_api_key = (
            os.getenv('ZHIPUAI_API_KEY')
            or os.getenv('OPENAI_API_KEY')
            or getattr(settings, 'OPENAI_API_KEY', '')
        )
        self.api_key = self._sanitize_config_string(raw_api_key)

        # 默认使用智谱AI模型（可在 settings 或环境变量中覆盖）
        raw_model = (
            os.getenv('ZHIPUAI_MODEL')
            or os.getenv('OPENAI_MODEL')
            or getattr(settings, 'OPENAI_MODEL', 'glm-4-flash')
        )
        self.model = self._sanitize_config_string(raw_model)
        
        # 调试信息：显示模型配置来源
        print(f"🔍 模型配置调试:")
        print(f"  ZHIPUAI_MODEL环境变量: {os.getenv('ZHIPUAI_MODEL')}")
        print(f"  OPENAI_MODEL环境变量: {os.getenv('OPENAI_MODEL')}")
        print(f"  settings.OPENAI_MODEL: {getattr(settings, 'OPENAI_MODEL', '未设置')}")
        print(f"  最终使用的模型: {self.model}")

        raw_base_url = (
            os.getenv('ZHIPUAI_BASE_URL')
            or os.getenv('OPENAI_BASE_URL')
            or getattr(settings, 'OPENAI_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
        )
        base_url_clean = self._sanitize_config_string(raw_base_url)
        # 补齐协议头，避免拼接 URL 异常
        if base_url_clean and not re.match(r'^https?://', base_url_clean):
            base_url_clean = 'https://' + base_url_clean
        self.base_url = base_url_clean or 'https://open.bigmodel.cn/api/paas/v4'
        
        # 检查是否为智谱AI
        self.is_zhipuai = 'bigmodel.cn' in self.base_url
    
    def ai_score_answer(self, question_content: str, correct_answer: str, 
                       student_answer: str, question_type: int, 
                       max_score: float = 10.0) -> Dict[str, Any]:
        """
        AI评分功能
        
        Args:
            question_content: 题目内容
            correct_answer: 正确答案
            student_answer: 学生答案
            question_type: 题目类型 (0-选择 1-填空 2-判断 3-编程)
            max_score: 最大分值
            
        Returns:
            Dict包含: score(得分), feedback(反馈), analysis(分析)
        """
        try:
            # 根据题目类型构建不同的评分提示
            if question_type == 0:  # 选择题
                prompt = self._build_choice_scoring_prompt(question_content, correct_answer, student_answer, max_score)
            elif question_type == 1:  # 填空题
                prompt = self._build_fill_scoring_prompt(question_content, correct_answer, student_answer, max_score)
            elif question_type == 2:  # 判断题
                prompt = self._build_judge_scoring_prompt(question_content, correct_answer, student_answer, max_score)
            elif question_type == 3:  # 编程题
                prompt = self._build_programming_scoring_prompt(question_content, correct_answer, student_answer, max_score)
            else:
                prompt = self._build_general_scoring_prompt(question_content, correct_answer, student_answer, max_score)
            
            # 调用AI API
            response = self._call_openai_api(prompt)
            
            # 解析AI响应
            result = self._parse_scoring_response(response, max_score)
            # 默认补充模型与置信度
            result.setdefault('confidence', 0.7)
            result.setdefault('model', self.model)

            return result
            
        except Exception as e:
            # 如果AI评分失败，使用传统评分方法作为备选
            return self._fallback_scoring(question_content, correct_answer, student_answer, question_type, max_score)
    
    def ai_generate_questions(self, subject: str, topic: str, difficulty: str, 
                            question_type: int, count: int = 5) -> List[Dict[str, Any]]:
        """
        AI自动创建题目功能
        
        Args:
            subject: 科目名称
            topic: 主题/章节
            difficulty: 难度等级 (easy/medium/hard)
            question_type: 题目类型 (0-选择 1-填空 2-判断 3-编程)
            count: 生成题目数量
            
        Returns:
            List[Dict] 包含生成的题目信息
        """
        try:
            # 构建题目生成提示（首次尝试）
            prompt = self._build_question_generation_prompt(subject, topic, difficulty, question_type, count)
            response = self._call_openai_api(prompt)
            questions = self._parse_question_generation_response(response, question_type)

            # 若首次为空，进行更严格 JSON 输出与降载重试
            if not questions:
                strict_prompt = self._build_question_generation_prompt(subject, topic, difficulty, question_type, min(count, 2))
                try:
                    response2 = self._call_openai_api(strict_prompt, force_json=True, max_tokens=800, temperature=0.2)
                    questions = self._parse_question_generation_response(response2, question_type)
                except Exception:
                    questions = []

            # 再次为空，做最小单题重试
            if not questions:
                min_prompt = self._build_question_generation_prompt(subject, topic, difficulty, question_type, 1)
                try:
                    response3 = self._call_openai_api(min_prompt, force_json=True, max_tokens=600, temperature=0.2)
                    questions = self._parse_question_generation_response(response3, question_type)
                except Exception:
                    questions = []

            return questions
            
        except Exception as e:
            print(f"AI生成题目失败: {str(e)}")
            return []
    
    def ai_analyze_wrong_answer(self, question_content: str, correct_answer: str, 
                               wrong_answer: str, question_type: int) -> Dict[str, str]:
        """
        AI分析错误答案
        
        Args:
            question_content: 题目内容
            correct_answer: 正确答案
            wrong_answer: 错误答案
            question_type: 题目类型
            
        Returns:
            Dict包含: analysis(分析), suggestion(建议)
        """
        try:
            prompt = f"""
请分析以下题目的错误答案，并提供详细的分析和改进建议：

题目：{question_content}
正确答案：{correct_answer}
学生答案：{wrong_answer}
题目类型：{self._get_question_type_name(question_type)}

请从以下几个方面进行分析：
1. 错误原因分析
2. 知识点掌握情况
3. 改进建议
4. 相关知识点复习建议

请以JSON格式返回：
{{
    "analysis": "详细错误分析",
    "suggestion": "改进建议",
    "knowledge_points": "相关知识点",
    "review_suggestions": "复习建议"
}}
"""
            
            response = self._call_openai_api(prompt)
            result = self._parse_json_response(response)
            
            return result
            
        except Exception as e:
            return {
                "analysis": "无法进行AI分析",
                "suggestion": "建议重新学习相关知识点",
                "knowledge_points": "",
                "review_suggestions": ""
            }
    
    def _build_choice_scoring_prompt(self, question_content: str, correct_answer: str, 
                                   student_answer: str, max_score: float) -> str:
        """构建选择题评分提示"""
        return f"""
请对以下选择题进行评分：

题目：{question_content}
正确答案：{correct_answer}
学生答案：{student_answer}
满分：{max_score}分

评分标准：
- 完全正确：{max_score}分
- 部分正确：{max_score * 0.5}分
- 完全错误：0分

请以JSON格式返回评分结果：
{{
    "score": 得分,
    "feedback": "评分反馈",
    "analysis": "详细分析",
    "is_correct": true/false
}}
"""
    
    def _build_fill_scoring_prompt(self, question_content: str, correct_answer: str, 
                                 student_answer: str, max_score: float) -> str:
        """构建填空题评分提示"""
        return f"""
请对以下填空题进行评分：

题目：{question_content}
正确答案：{correct_answer}
学生答案：{student_answer}
满分：{max_score}分

评分标准：
- 完全正确：{max_score}分
- 部分正确：根据正确程度给予{max_score * 0.3}-{max_score * 0.8}分
- 完全错误：0分

请考虑：
1. 答案的准确性
2. 拼写错误（轻微扣分）
3. 表达方式（同义词可接受）

请以JSON格式返回评分结果（务必严格符合以下JSON结构）：
{{
    "score": 得分,
    "feedback": "评分反馈",
    "analysis": "详细分析",
    "is_correct": true/false,
    "confidence": 介于0和1之间的置信度数字
}}
"""
    
    def _build_judge_scoring_prompt(self, question_content: str, correct_answer: str, 
                                  student_answer: str, max_score: float) -> str:
        """构建判断题评分提示"""
        return f"""
请对以下判断题进行评分：

题目：{question_content}
正确答案：{correct_answer}
学生答案：{student_answer}
满分：{max_score}分

评分标准：
- 完全正确：{max_score}分
- 完全错误：0分

请以JSON格式返回评分结果：
{{
    "score": 得分,
    "feedback": "评分反馈",
    "analysis": "详细分析",
    "is_correct": true/false
}}
"""
    
    def _build_programming_scoring_prompt(self, question_content: str, correct_answer: str, 
                                        student_answer: str, max_score: float) -> str:
        """构建编程题评分提示"""
        return f"""
请对以下编程题进行评分：

题目：{question_content}
参考答案：{correct_answer}
学生答案：{student_answer}
满分：{max_score}分

评分标准：
- 完全正确：{max_score}分
- 逻辑正确但有小错误：{max_score * 0.8}分
- 思路正确但实现有误：{max_score * 0.6}分
- 部分正确：{max_score * 0.3}-{max_score * 0.5}分
- 完全错误：0分

请考虑：
1. 代码逻辑的正确性
2. 语法错误
3. 算法思路
4. 代码风格

请以JSON格式返回评分结果（务必严格符合以下JSON结构）：
{{
    "score": 得分,
    "feedback": "评分反馈",
    "analysis": "详细分析",
    "is_correct": true/false,
    "code_quality": "代码质量评价",
    "confidence": 介于0和1之间的置信度数字
}}
"""
    
    def _build_general_scoring_prompt(self, question_content: str, correct_answer: str, 
                                    student_answer: str, max_score: float) -> str:
        """构建通用评分提示"""
        return f"""
请对以下题目进行评分：

题目：{question_content}
正确答案：{correct_answer}
学生答案：{student_answer}
满分：{max_score}分

请根据答案的准确性、完整性和表达质量进行评分。

请以JSON格式返回评分结果（务必严格符合以下JSON结构）：
{{
    "score": 得分,
    "feedback": "评分反馈",
    "analysis": "详细分析",
    "is_correct": true/false,
    "confidence": 介于0和1之间的置信度数字
}}
"""
    
    def _build_question_generation_prompt(self, subject: str, topic: str, difficulty: str, 
                                        question_type: int, count: int) -> str:
        """构建题目生成提示"""
        type_name = self._get_question_type_name(question_type)
        
        return f"""
你是资深出题专家，请为 {subject} 科目的“{topic}”主题生成 {count} 道 {difficulty} 难度的 {type_name}。

严格输出要求（非常重要）：
- 只输出一个严格的 JSON 对象，不能包含任何解释性文字、Markdown、反引号或注释
- JSON 使用双引号；不要包含多余字段；不要有尾随逗号
- 当题型不是“选择题”时，必须完全省略 "options" 字段

必须返回的 JSON 结构：
{{
  "questions": [
    {{
      "content": "题目内容",
      "options": ["选项A", "选项B", "选项C", "选项D"],
      "answer": "正确答案",
      "analysis": "题目解析",
      "difficulty": "{difficulty}",
      "knowledge_points": "涉及知识点"
    }}
  ]
}}
说明：若当前题型不是选择题，则不要返回 "options" 字段；若是选择题，请确保有且仅有 4 个选项。
"""
    
    def _call_openai_api(self, prompt: str, force_json: bool = False, max_tokens: int = 1200, temperature: float = 0.3) -> str:
        """调用兼容 OpenAI/智谱AI 的 Chat Completions 接口"""
        try:
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            
            # 构建请求payload
            payload = {
                'model': self.model,
                'messages': [
                    {"role": "system", "content": "你是一个专业的教育评估专家，擅长题目评分和题目生成。"},
                    {"role": "user", "content": prompt}
                ],
                'temperature': temperature,
                'max_tokens': max_tokens,
            }
            if force_json:
                payload['response_format'] = { 'type': 'json_object' }
            
            # 根据智谱AI官方文档，使用简单的Bearer API Key认证
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            print(f"智谱AI请求URL: {url}")
            print(f"智谱AI请求Headers: {headers}")
            print(f"智谱AI请求Payload: {payload}")

            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            print(f"智谱AI响应状态码: {resp.status_code}")
            print(f"智谱AI响应Headers: {dict(resp.headers)}")
            
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                # 尝试取回服务端返回的错误细节
                detail = ''
                try:
                    err_json = resp.json()
                    print(f"智谱AI错误响应JSON: {err_json}")
                    # OpenAI 常见错误结构 {error: {message: ...}}
                    detail = err_json.get('error', {}).get('message') or err_json.get('message') or ''
                except Exception:
                    detail = resp.text
                    print(f"智谱AI错误响应文本: {detail}")
                raise Exception(f"HTTP {resp.status_code}: {detail}") from http_err
            data = resp.json()
            # 兼容 OpenAI 风格返回
            content = (
                data.get('choices', [{}])[0]
                .get('message', {})
                .get('content', '')
            )
            # 若没有内容，返回完整响应数据
            if not content:
                content = json.dumps(data)
            return content
        except Exception as e:
            print(f"AI接口调用失败: {str(e)}")
            raise e
    
    def _generate_zhipuai_jwt(self) -> str:
        """生成智谱AI的JWT Token"""
        try:
            print(f"正在解析API Key: {self.api_key[:20]}...")
            
            # 解析API Key格式：id.secret
            if '.' not in self.api_key:
                raise Exception("智谱AI API Key格式错误，应为 'id.secret' 格式")
            
            api_id, api_secret = self.api_key.split('.', 1)
            print(f"API ID: {api_id[:10]}..., API Secret: {api_secret[:10]}...")
            
            # 生成JWT payload - 智谱AI v4格式
            # 使用标准的payload格式，包含所有必要字段
            current_time = int(time.time())
            payload = {
                'api_key': api_id,
                'exp': current_time + 3600,  # 1小时过期
                'iat': current_time,         # 签发时间
                'nbf': current_time          # 生效时间
            }
            
            # 使用API Secret签名
            token = jwt.encode(payload, api_secret, algorithm='HS256')
            print(f"JWT Token生成成功: {token[:20]}...")
            
            # 调试信息：解码JWT验证内容
            try:
                decoded = jwt.decode(token, api_secret, algorithms=['HS256'])
                print(f"JWT解码验证: {decoded}")
            except Exception as decode_err:
                print(f"JWT解码失败: {decode_err}")
            
            return token
            
        except Exception as e:
            print(f"生成智谱AI JWT失败: {str(e)}")
            # 尝试使用简单的API Key认证作为备选
            print("尝试使用简单API Key认证...")
            return self.api_key
    
    def _parse_scoring_response(self, response: str, max_score: float) -> Dict[str, Any]:
        """解析评分响应"""
        try:
            result = self._parse_json_response(response)
            
            # 确保分数在合理范围内
            score = float(result.get('score', 0))
            score = max(0, min(score, max_score))
            
            return {
                'score': score,
                'feedback': result.get('feedback', ''),
                'analysis': result.get('analysis', ''),
                'is_correct': result.get('is_correct', False),
                'confidence': float(result.get('confidence', 0.7)),
                'model': self.model
            }
        except Exception as e:
            print(f"解析评分响应失败: {str(e)}")
            return {
                'score': 0,
                'feedback': '评分解析失败',
                'analysis': '无法进行AI分析',
                'is_correct': False
            }
    
    def _parse_question_generation_response(self, response: str, question_type: int) -> List[Dict[str, Any]]:
        """解析题目生成响应"""
        try:
            result = self._parse_json_response(response)
            questions = result.get('questions', [])
            
            # 为每个题目添加创建时间
            for question in questions:
                question['createTime'] = DateUtil.getNowDateTime()
                question['type'] = question_type
            
            return questions
        except Exception as e:
            print(f"解析题目生成响应失败: {str(e)}")
            return []
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析JSON响应（更健壮）：
        - 允许模型在外层包裹多余文本/Markdown
        - 尝试去除 // 注释与尾随逗号
        """
        try:
            raw = response or ""

            # 去掉 Markdown 代码块标记
            raw = raw.replace('```json', '').replace('```', '')

            # 尝试提取第一个大括号 JSON 片段
            json_match = re.search(r'\{[\s\S]*\}', raw)
            json_str = json_match.group() if json_match else raw

            def _strip_line_comments(text: str) -> str:
                # 移除不在字符串中的 // 注释
                result_chars = []
                in_string = False
                escape = False
                i = 0
                length = len(text)
                while i < length:
                    ch = text[i]
                    if in_string:
                        result_chars.append(ch)
                        if escape:
                            escape = False
                        elif ch == '\\':
                            escape = True
                        elif ch == '"':
                            in_string = False
                        i += 1
                        continue
                    # 非字符串状态
                    if ch == '"':
                        in_string = True
                        result_chars.append(ch)
                        i += 1
                        continue
                    if ch == '/' and i + 1 < length and text[i + 1] == '/':
                        # 跳到行末
                        i += 2
                        while i < length and text[i] not in '\r\n':
                            i += 1
                        continue
                    result_chars.append(ch)
                    i += 1
                return ''.join(result_chars)

            cleaned = _strip_line_comments(json_str)
            # 去除尾随逗号
            cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
            # 尝试解析
            return json.loads(cleaned)
        except Exception as e:
            print(f"JSON解析失败: {str(e)}")
            return {}

    @staticmethod
    def _sanitize_config_string(value: Any) -> str:
        """清洗配置字符串：去除首尾空白/换行，去除包裹引号，移除内联换行符。"""
        try:
            text = str(value) if value is not None else ''
            # 去掉首尾空白与换行
            text = text.strip().replace('\r', '').replace('\n', '')
            # 去掉包裹引号
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1].strip()
            return text
        except Exception:
            return ''
    
    def _fallback_scoring(self, question_content: str, correct_answer: str, 
                         student_answer: str, question_type: int, max_score: float) -> Dict[str, Any]:
        """传统评分方法作为备选"""
        try:
            # 简单的字符串比较
            if question_type == 0:  # 选择题
                is_correct = str(student_answer).strip() == str(correct_answer).strip()
            elif question_type == 2:  # 判断题
                is_correct = str(student_answer).strip().lower() == str(correct_answer).strip().lower()
            else:  # 其他题型
                is_correct = str(student_answer).strip().lower() == str(correct_answer).strip().lower()
            
            score = max_score if is_correct else 0
            
            return {
                'score': score,
                'feedback': '使用传统评分方法',
                'analysis': 'AI评分不可用，使用传统评分',
                'is_correct': is_correct
            }
        except Exception as e:
            return {
                'score': 0,
                'feedback': '评分失败',
                'analysis': '评分系统错误',
                'is_correct': False
            }
    
    def _get_question_type_name(self, question_type: int) -> str:
        """获取题目类型名称"""
        type_names = {
            0: "选择题",
            1: "填空题", 
            2: "判断题",
            3: "编程题"
        }
        return type_names.get(question_type, "未知类型")


def test_ai_connection() -> bool:
    """
    测试 AI 服务连接

    Returns:
        True if AI service is available, False otherwise
    """
    try:
        import os
        from django.conf import settings

        # 检查 API Key 是否配置
        api_key = (
            os.getenv('ZHIPUAI_API_KEY')
            or os.getenv('OPENAI_API_KEY')
            or getattr(settings, 'OPENAI_API_KEY', '')
        )

        if not api_key or api_key == '':
            print("AI 服务未配置：API Key 为空")
            return False

        # 尝试发送一个简单的测试请求
        ai_utils = AIUtils()

        # 发送一个简单的测试提示
        test_prompt = "测试连接"

        try:
            # 调用 AI API（使用很短的提示）
            url = f"{ai_utils.base_url.rstrip('/')}/chat/completions"
            headers = {
                'Authorization': f'Bearer {ai_utils.api_key}',
                'Content-Type': 'application/json',
            }
            payload = {
                'model': ai_utils.model,
                'messages': [{"role": "user", "content": "Hi"}],
                'max_tokens': 10,
            }

            import requests
            resp = requests.post(url, headers=headers, json=payload, timeout=10)

            if resp.status_code == 200:
                print("AI 服务连接成功")
                return True
            elif resp.status_code == 401:
                print("AI 服务认证失败：API Key 无效")
                return False
            else:
                print(f"AI 服务返回错误：{resp.status_code}")
                return False

        except requests.exceptions.Timeout:
            print("AI 服务连接超时")
            return False
        except Exception as e:
            print(f"AI 服务测试失败：{str(e)}")
            return False

    except Exception as e:
        print(f"AI 服务检查失败：{str(e)}")
        return False
