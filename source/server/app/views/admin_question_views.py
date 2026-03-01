"""
管理员题目管理相关视图

从 admin 视图中拆分题目管理逻辑，降低单文件复杂度。
"""

import csv
import io
import re

from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Count

from app import models
from comm.BaseView import BaseView
from comm.CommUtils import DateUtil


class AdminQuestionView:
    """管理员题目管理接口集合"""

    @staticmethod
    def _resolve_choice_answer_option_id(raw_answer, created_options):
        """将 AI 生成的选择题答案归一化并映射到真实 option.id。"""
        if not created_options:
            return None

        answer_text = str(raw_answer or '').strip()
        if not answer_text:
            return created_options[0].id

        upper = answer_text.upper()
        letters = ['A', 'B', 'C', 'D']

        index = None
        if upper in letters:
            index = letters.index(upper)
        elif upper.isdigit():
            val = int(upper)
            if 0 <= val <= 3:
                index = val
            elif 1 <= val <= 4:
                index = val - 1
        else:
            matched = re.search(r'[ABCD]', upper)
            if matched:
                index = letters.index(matched.group(0))

        if index is not None and 0 <= index < len(created_options):
            return created_options[index].id

        # 回退：按选项文本匹配
        for idx, option in enumerate(created_options):
            option_text = str(option.name or '').strip()
            if answer_text == option_text or upper == option_text.upper():
                return created_options[idx].id

        return created_options[0].id

    @staticmethod
    def get_questions(request):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search') or request.GET.get('keyword', '')
            subject_id = request.GET.get('subjectId') or request.GET.get('project', '')
            question_type = request.GET.get('questionType') or request.GET.get('type', '')

            questions_query = models.Practises.objects.all().order_by('-createTime', '-id')

            if search:
                questions_query = questions_query.filter(name__icontains=search)
            if subject_id:
                questions_query = questions_query.filter(project_id=subject_id)
            if question_type not in [None, '']:
                questions_query = questions_query.filter(type=question_type)

            total = questions_query.count()
            paginator = Paginator(questions_query, size)
            questions_page = paginator.get_page(page)

            questions_data = []
            for question in questions_page:
                options = models.Options.objects.filter(practise=question)
                options_data = []
                for option in options:
                    options_data.append({
                        'id': option.id,
                        'content': option.name
                    })

                questions_data.append({
                    'id': question.id,
                    'name': question.name,
                    'type': question.type,
                    'subjectId': question.project.id if question.project else None,
                    'subjectName': question.project.name if question.project else '',
                    'options': options_data,
                    'answer': question.answer,
                    'analyse': question.analyse,
                    'createTime': getattr(question, 'createTime', '')
                })

            return BaseView.successData({
                'list': questions_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取题目列表失败: {str(e)}')

    @staticmethod
    def manage_questions(request):
        try:
            action = request.POST.get('action')

            if action == 'add':
                name = request.POST.get('name')
                question_type = request.POST.get('type')
                subject_id = request.POST.get('subjectId') or request.POST.get('project') or request.POST.get('projectId')
                answer = request.POST.get('answer', '') or request.POST.get('correctAnswer', '')
                analyse = request.POST.get('analyse', '') or request.POST.get('analysis', '')
                options = request.POST.getlist('options[]')
                correct_options = request.POST.getlist('correctOptions[]')

                if not all([name, question_type is not None, subject_id]):
                    return BaseView.error('缺少必要参数')

                subject = models.Projects.objects.filter(id=subject_id).first() if subject_id else None

                question = models.Practises.objects.create(
                    name=name,
                    type=question_type,
                    project=subject,
                    answer=answer,
                    analyse=analyse
                )

                created_options = []
                for option_content in options:
                    opt = models.Options.objects.create(
                        practise=question,
                        name=option_content
                    )
                    created_options.append(opt)

                if question_type == '0' and correct_options and created_options:
                    try:
                        correct_idx = int(correct_options[0])
                        if 0 <= correct_idx < len(created_options):
                            question.answer = str(created_options[correct_idx].id)
                            question.save()
                    except (ValueError, IndexError):
                        pass

                return BaseView.successData({'id': question.id, 'message': '题目创建成功'})

            if action == 'update':
                question_id = request.POST.get('id')
                question = models.Practises.objects.filter(id=question_id).first()
                if not question:
                    return BaseView.error('题目不存在')

                question.name = request.POST.get('name', question.name)
                question.answer = request.POST.get('answer', question.answer) or request.POST.get('correctAnswer', question.answer)
                question.analyse = request.POST.get('analyse', question.analyse) or request.POST.get('analysis', question.analyse)
                question_type = request.POST.get('type')
                if question_type not in [None, '']:
                    question.type = question_type
                subject_id = request.POST.get('subjectId') or request.POST.get('project') or request.POST.get('projectId')
                if subject_id:
                    subject = models.Projects.objects.filter(id=subject_id).first()
                    if subject:
                        question.project = subject
                question.save()

                options = request.POST.getlist('options[]')
                correct_options = request.POST.getlist('correctOptions[]')

                models.Options.objects.filter(practise=question).delete()

                created_options = []
                for option_content in options:
                    opt = models.Options.objects.create(
                        practise=question,
                        name=option_content
                    )
                    created_options.append(opt)

                if question.type == 0 and correct_options and created_options:
                    try:
                        correct_idx = int(correct_options[0])
                        if 0 <= correct_idx < len(created_options):
                            question.answer = str(created_options[correct_idx].id)
                            question.save()
                    except (ValueError, IndexError):
                        pass

                return BaseView.success('题目更新成功')

            if action == 'delete':
                question_id = request.POST.get('id')
                question = models.Practises.objects.filter(id=question_id).first()
                if not question:
                    return BaseView.error('题目不存在')

                models.Options.objects.filter(practise=question).delete()
                question.delete()
                return BaseView.success('题目删除成功')

            if action == 'generate_ai':
                from app.views import AdminView as LegacyAdminView
                return LegacyAdminView.generateAIQuestions(request)

            return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'题目操作失败: {str(e)}')

    @staticmethod
    def import_questions(request):
        try:
            file = request.FILES.get('file')
            subject_id = request.POST.get('subjectId')
            if not file:
                return BaseView.error('未上传文件')

            if file.size > 10 * 1024 * 1024:
                return BaseView.error('文件大小不能超过10MB')

            if not file.name.endswith('.csv'):
                return BaseView.error('只支持CSV格式文件')

            subject = models.Projects.objects.filter(id=subject_id).first() if subject_id else None
            if not subject:
                return BaseView.error('指定的科目不存在')

            decoded = file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded))

            fieldnames = [str(f).strip() for f in (reader.fieldnames or []) if f is not None]
            if not fieldnames:
                return BaseView.error('CSV文件缺少表头')

            has_name_col = ('name' in fieldnames) or ('题目' in fieldnames)
            has_answer_col = ('answer' in fieldnames) or ('答案' in fieldnames)
            if not has_name_col or not has_answer_col:
                return BaseView.error('CSV缺少必要列：name/题目、answer/答案')

            created, failed = 0, []
            for idx, row in enumerate(reader, start=2):
                try:
                    name = row.get('name') or row.get('题目')
                    type_str = (row.get('type') or row.get('题型') or '0').strip()
                    type_map = {
                        'single': 0, '选择': 0, '选择题': 0, '0': 0,
                        'fill': 1, '填空': 1, '填空题': 1, '1': 1,
                        'judge': 2, '判断': 2, '判断题': 2, '2': 2,
                        'essay': 3, '编程': 3, '简答': 3, '编程题': 3, '3': 3,
                    }
                    normalized_type = str(type_str).strip().lower()
                    if normalized_type == '':
                        normalized_type = '0'
                    if normalized_type not in type_map:
                        failed.append({'line': idx, 'reason': f'无效的题目类型: {type_str}'})
                        continue
                    qtype = type_map.get(normalized_type)

                    answer = row.get('answer') or row.get('答案') or ''
                    analyse = row.get('analyse') or row.get('解析') or ''

                    if not name or not name.strip():
                        failed.append({'line': idx, 'reason': '题目内容为空'})
                        continue

                    if not answer or not answer.strip():
                        failed.append({'line': idx, 'reason': '答案不能为空'})
                        continue

                    options = []
                    if qtype == 0:
                        for key in ['optionA', 'optionB', 'optionC', 'optionD',
                                    'A', 'B', 'C', 'D', '选项A', '选项B', '选项C', '选项D']:
                            if row.get(key):
                                options.append(row.get(key))

                        if len(options) < 2:
                            failed.append({'line': idx, 'reason': '选择题至少需要2个选项'})
                            continue

                        if answer:
                            ans_norm = answer.strip().upper()
                            letter_to_index = {'A': '0', 'B': '1', 'C': '2', 'D': '3'}
                            normalized_answer_tokens = []
                            for token in ans_norm.replace(',', '|').split('|'):
                                token = token.strip()
                                if token == '':
                                    continue
                                mapped = letter_to_index.get(token, token)
                                if not str(mapped).isdigit():
                                    failed.append({'line': idx, 'reason': f'选择题答案格式错误: {answer}'})
                                    normalized_answer_tokens = []
                                    break
                                option_index = int(mapped)
                                if option_index < 0 or option_index >= len(options):
                                    failed.append({'line': idx, 'reason': f'选择题答案超出选项范围: {answer}'})
                                    normalized_answer_tokens = []
                                    break
                                normalized_answer_tokens.append(str(option_index))

                            if not normalized_answer_tokens:
                                continue
                            answer = '|'.join(normalized_answer_tokens)

                    if qtype == 2:
                        answer_norm = str(answer).strip().lower()
                        judge_map = {
                            'true': 'true',
                            'false': 'false',
                            '1': 'true',
                            '0': 'false',
                            '是': 'true',
                            '否': 'false',
                            '对': 'true',
                            '错': 'false',
                            '正确': 'true',
                            '错误': 'false'
                        }
                        if answer_norm not in judge_map:
                            failed.append({'line': idx, 'reason': f'判断题答案格式错误: {answer}'})
                            continue
                        answer = judge_map.get(answer_norm, answer)

                    row_subject_id = row.get('subjectId') or row.get('学科ID')
                    row_subject = models.Projects.objects.filter(
                        id=row_subject_id).first() if row_subject_id else subject

                    if not row_subject:
                        failed.append({'line': idx, 'reason': '科目不存在'})
                        continue

                    question = models.Practises.objects.create(
                        name=name.strip(),
                        type=qtype,
                        project=row_subject,
                        answer=answer,
                        analyse=analyse
                    )
                    if qtype == 0 and options:
                        for opt in options:
                            models.Options.objects.create(practise=question, name=opt)
                    created += 1
                except Exception as ie:
                    failed.append({'line': idx, 'reason': str(ie)})

            total_rows = created + len(failed)
            reason_stats = {}
            for item in failed:
                reason = item.get('reason', '未知错误')
                reason_stats[reason] = reason_stats.get(reason, 0) + 1

            return BaseView.successData({
                'created': created,
                'failed': failed,
                'total': total_rows,
                'failedCount': len(failed),
                'reasonStats': reason_stats
            })
        except Exception as e:
            return BaseView.error(f'导入失败: {str(e)}')

    @staticmethod
    def export_questions(request):
        try:
            subject_id = request.POST.get('subjectId')
            search = request.POST.get('search', '')
            question_type = request.POST.get('questionType')
            query = models.Practises.objects.all()
            if subject_id:
                query = query.filter(project_id=subject_id)
            if search:
                query = query.filter(name__icontains=search)
            if question_type not in [None, '']:
                query = query.filter(type=question_type)

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['id', 'name', 'type', 'subjectId', 'answer', 'analyse', 'options'])
            for question in query:
                options = models.Options.objects.filter(practise=question).values_list('name', flat=True)
                writer.writerow([
                    question.id,
                    question.name,
                    question.type,
                    question.project.id if question.project else '',
                    question.answer,
                    question.analyse,
                    '|'.join(options)
                ])

            response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename=questions_export.csv'
            return response
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    @staticmethod
    def questions_template(request):
        try:
            sample = (
                'name,type,answer,analyse,optionA,optionB,optionC,optionD,subjectId\n'
                '以下哪个是 Python 的整数类型标识?,0,0,整数类型多为 int,整型,int,float,str,1\n'
                'Python 定义函数使用的关键字是?,1,def,函数定义关键字,,, , ,1\n'
                'Python 是解释型语言?,2,true,判断正误题,,, , ,1\n'
                '实现函数 add(a,b) 返回和,3,def add(a,b): return a+b,示例答案,,, , ,1\n'
            )
            response = HttpResponse(sample, content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename=questions_template.csv'
            return response
        except Exception as e:
            return BaseView.error(f'生成模板失败: {str(e)}')

    @staticmethod
    def generate_ai_questions_batch(request):
        """AI 批量生成多类型题目并入库。"""
        try:
            from comm.AIUtils import AIUtils
            import json as _json

            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            difficulty = request.POST.get('difficulty', 'medium')
            subject_id = request.POST.get('subjectId')
            question_types_raw = request.POST.get('questionTypes', '')
            counts_raw = request.POST.get('counts', '')
            total_count = int(request.POST.get('count', '0') or '0')

            max_batch_size = 50
            if total_count > max_batch_size:
                return BaseView.error(f'单次生成题目数量不能超过{max_batch_size}道')

            if not all([subject, topic, subject_id, question_types_raw]):
                return BaseView.error('缺少必要参数：subject/topic/subjectId/questionTypes')

            types_list = []
            try:
                if question_types_raw.strip().startswith('['):
                    types_list = [_ for _ in _json.loads(question_types_raw)]
                else:
                    types_list = [int(x) for x in str(question_types_raw).split(',') if str(x).strip() != '']
            except Exception:
                return BaseView.error('参数 questionTypes 格式错误')
            types_list = [int(t) for t in types_list if int(t) in [0, 1, 2, 3]]
            if not types_list:
                return BaseView.error('请选择至少一种题目类型')

            count_by_type = {}
            if counts_raw:
                try:
                    if counts_raw.strip().startswith('{'):
                        tmp = _json.loads(counts_raw)
                        for k, v in tmp.items():
                            count_by_type[int(k)] = int(v)
                    else:
                        pairs = [p for p in counts_raw.split(',') if ':' in p]
                        for p in pairs:
                            k, v = p.split(':', 1)
                            count_by_type[int(k)] = int(v)
                except Exception:
                    count_by_type = {}
            if not count_by_type:
                even = max(1, (total_count or 0) // len(types_list)) if (total_count or 0) > 0 else 5
                for t in types_list:
                    count_by_type[int(t)] = even

            subject_obj = models.Projects.objects.filter(id=subject_id).first()
            if not subject_obj:
                return BaseView.error('科目不存在')

            ai_utils = AIUtils()
            created_total = 0
            created_by_type = {0: 0, 1: 0, 2: 0, 3: 0}
            quality_by_type = {}

            for t in types_list:
                count = int(count_by_type.get(int(t), 0))
                if count <= 0:
                    continue
                questions = ai_utils.ai_generate_questions(
                    subject=subject,
                    topic=topic,
                    difficulty=difficulty,
                    question_type=int(t),
                    count=count
                )
                quality_by_type[str(int(t))] = getattr(ai_utils, 'last_generation_report', {})
                for question_data in questions or []:
                    try:
                        question = models.Practises.objects.create(
                            name=question_data['content'],
                            type=int(t),
                            project=subject_obj,
                            answer=question_data.get('answer', ''),
                            analyse=question_data.get('analysis', ''),
                            createTime=DateUtil.getNowDateTime()
                        )
                        created_options = []
                        if int(t) == 0 and 'options' in question_data:
                            for option in question_data['options']:
                                created_options.append(models.Options.objects.create(practise=question, name=option))
                            if created_options:
                                question.answer = str(
                                    AdminQuestionView._resolve_choice_answer_option_id(
                                        question_data.get('answer', ''),
                                        created_options
                                    )
                                )
                                question.save(update_fields=['answer'])
                        created_total += 1
                        created_by_type[int(t)] += 1
                    except Exception as ie:
                        print(f'保存题目失败(type={t}): {str(ie)}')
                        continue

            return BaseView.successData({
                'created': created_total,
                'createdByType': created_by_type,
                'generationQualityByType': quality_by_type
            })
        except Exception as e:
            return BaseView.error(f'批量生成失败: {str(e)}')

    @staticmethod
    def generate_ai_questions(request):
        """AI 自动生成题目。"""
        try:
            from comm.AIUtils import AIUtils

            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            difficulty = request.POST.get('difficulty', 'medium')
            question_type = int(request.POST.get('questionType', 0))
            count = int(request.POST.get('count', 5))
            subject_id = request.POST.get('subjectId')

            if not all([subject, topic, subject_id]):
                return BaseView.error('缺少必要参数：科目、主题和科目ID')

            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'medium'

            if question_type not in [0, 1, 2, 3]:
                return BaseView.error('无效的题目类型')

            if count < 1 or count > 20:
                count = 5

            subject_obj = models.Projects.objects.filter(id=subject_id).first()
            if not subject_obj:
                return BaseView.error('科目不存在')

            ai_utils = AIUtils()
            questions = ai_utils.ai_generate_questions(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                count=count
            )
            generation_quality = getattr(ai_utils, 'last_generation_report', {})

            if not questions:
                return BaseView.error(f"AI生成题目失败（model={ai_utils.model}, base_url={ai_utils.base_url}）")

            created_questions = []
            for question_data in questions:
                try:
                    question = models.Practises.objects.create(
                        name=question_data['content'],
                        type=question_type,
                        project=subject_obj,
                        answer=question_data['answer'],
                        analyse=question_data.get('analysis', ''),
                        createTime=DateUtil.getNowDateTime()
                    )

                    created_options = []
                    if question_type == 0 and 'options' in question_data:
                        for option in question_data['options']:
                            created_options.append(models.Options.objects.create(
                                practise=question,
                                name=option
                            ))
                        if created_options:
                            question.answer = str(
                                AdminQuestionView._resolve_choice_answer_option_id(
                                    question_data.get('answer', ''),
                                    created_options
                                )
                            )
                            question.save(update_fields=['answer'])

                    created_questions.append({
                        'id': question.id,
                        'content': question.name,
                        'answer': question.answer,
                        'analysis': question.analyse
                    })
                except Exception as ie:
                    print(f"保存题目失败: {str(ie)}")
                    continue

            return BaseView.successData({
                'message': f'成功生成{len(created_questions)}道题目',
                'questions': created_questions,
                'total_generated': len(created_questions),
                'requested_count': count,
                'generationQuality': generation_quality
            })

        except Exception as e:
            print(f"AI生成题目失败: {str(e)}")
            return BaseView.error(f'AI生成题目失败: {str(e)}')

    @staticmethod
    def fill_all_subjects_minimum(request):
        """为所有学科补齐基础题量：选择10、填空10、判断10、编程2。"""
        try:
            counts_str = request.POST.get('counts', '0:10,1:10,2:10,3:2')
            default_counts = {0: 10, 1: 10, 2: 10, 3: 2}
            counts_map = dict(default_counts)
            try:
                pairs = [p for p in counts_str.split(',') if ':' in p]
                for pair in pairs:
                    key, value = pair.split(':', 1)
                    k_i, v_i = int(key), int(value)
                    if k_i in [0, 1, 2, 3] and v_i >= 0:
                        counts_map[k_i] = v_i
            except Exception:
                counts_map = default_counts

            topic = request.POST.get('topic', '基础知识与核心概念')
            difficulty = request.POST.get('difficulty', 'medium')

            cache_key = 'projects:all_ids'
            subject_ids = cache.get(cache_key)
            if subject_ids is None:
                subject_ids = list(models.Projects.objects.all().values_list('id', flat=True))
                cache.set(cache_key, subject_ids, 3600)

            if not subject_ids:
                return BaseView.successData({
                    'createdTotal': 0,
                    'list': []
                })

            all_subjects = list(models.Projects.objects.filter(id__in=subject_ids).all())

            type_counts = models.Practises.objects.filter(project_id__in=subject_ids).values(
                'project_id', 'type'
            ).annotate(count=Count('id'))

            subject_question_counts = {sid: {0: 0, 1: 0, 2: 0, 3: 0} for sid in subject_ids}
            for tc in type_counts:
                subject_question_counts[tc['project_id']][tc['type']] = tc['count']

            valid_choice_counts = models.Options.objects.filter(
                practise__type=0, practise__project_id__in=subject_ids
            ).values('practise_id').annotate(c=Count('id')).filter(c=4)

            valid_choice_map = {sid: 0 for sid in subject_ids}
            practise_map = {
                p.id: p.project_id for p in models.Practises.objects.filter(
                    id__in=[vc['practise_id'] for vc in valid_choice_counts]
                ).only('id', 'project_id')
            }
            for vc in valid_choice_counts:
                pid = vc['practise_id']
                sid = practise_map.get(pid)
                if sid in valid_choice_map:
                    valid_choice_map[sid] += 1

            ai = None
            results = []
            total_created = 0
            quality_reports = []

            for subject in all_subjects:
                created_by_type = {0: 0, 1: 0, 2: 0, 3: 0}

                counts = subject_question_counts.get(subject.id, {0: 0, 1: 0, 2: 0, 3: 0})
                valid_choice = valid_choice_map.get(subject.id, 0)

                need_map = {
                    0: max(0, int(counts_map.get(0, 10)) - valid_choice),
                    1: max(0, int(counts_map.get(1, 10)) - counts[1]),
                    2: max(0, int(counts_map.get(2, 10)) - counts[2]),
                    3: max(0, int(counts_map.get(3, 2)) - counts[3]),
                }

                if any(v > 0 for v in need_map.values()) and ai is None:
                    from comm.AIUtils import AIUtils
                    ai = AIUtils()

                for t, need in need_map.items():
                    if need <= 0:
                        continue
                    questions = ai.ai_generate_questions(
                        subject=subject.name,
                        topic=topic,
                        difficulty=difficulty,
                        question_type=int(t),
                        count=int(need)
                    ) or []
                    quality_reports.append({
                        'subjectId': subject.id,
                        'subjectName': subject.name,
                        'type': int(t),
                        'report': getattr(ai, 'last_generation_report', {})
                    })
                    for question in questions:
                        try:
                            pr = models.Practises.objects.create(
                                name=question.get('content', ''),
                                type=int(t),
                                project=subject,
                                answer=question.get('answer', ''),
                                analyse=question.get('analysis', ''),
                                createTime=DateUtil.getNowDateTime()
                            )
                            created_options = []
                            if int(t) == 0 and question.get('options'):
                                for option in question['options']:
                                    created_options.append(models.Options.objects.create(practise=pr, name=option))
                                if created_options:
                                    pr.answer = str(
                                        AdminQuestionView._resolve_choice_answer_option_id(
                                            question.get('answer', ''),
                                            created_options
                                        )
                                    )
                                    pr.save(update_fields=['answer'])
                            created_by_type[int(t)] += 1
                            total_created += 1
                        except Exception as ie:
                            print(f'学科{subject.id}生成失败(type={t}): {str(ie)}')

                results.append({
                    'subjectId': subject.id,
                    'subjectName': subject.name,
                    'createdByType': created_by_type
                })

            return BaseView.successData({
                'createdTotal': total_created,
                'list': results,
                'generationQualityReports': quality_reports
            })
        except Exception as e:
            return BaseView.error(f'补齐失败: {str(e)}')