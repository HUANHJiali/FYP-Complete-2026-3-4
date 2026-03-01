"""
管理员导入导出相关视图

从 admin 视图中拆分学生导入与数据导出逻辑，降低单文件复杂度。
"""

import os
import tempfile

from django.http import HttpResponse

from comm.BaseView import BaseView


class AdminExportView:
    """管理员导入导出接口集合"""

    @staticmethod
    def import_students(request):
        """批量导入学生"""
        try:
            file = request.FILES.get('file')
            if not file:
                return BaseView.error('请选择文件')

            file_ext = os.path.splitext(file.name)[1].lower()

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                for chunk in file.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name

            try:
                from app.services.import_service import ImportService

                if file_ext in ['.xlsx', '.xls']:
                    success, fail, errors = ImportService.import_students_from_excel(tmp_path)
                elif file_ext == '.csv':
                    success, fail, errors = ImportService.import_students_from_csv(tmp_path)
                else:
                    return BaseView.error('不支持的文件格式，请上传Excel或CSV文件')

                result = {
                    'success': success,
                    'fail': fail,
                    'errors': errors[:50]
                }

                if success > 0:
                    return BaseView.successData(result)
                return BaseView.warn(f'导入失败: {"; ".join(errors[:5])}')
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception as e:
            return BaseView.error(f'导入失败: {str(e)}')

    @staticmethod
    def download_students_template(request):
        """下载学生导入模板"""
        try:
            from app.services.import_service import ImportService

            template_path = ImportService.download_student_template()

            with open(template_path, 'rb') as file_obj:
                response = HttpResponse(
                    file_obj.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename="students_template.xlsx"'

            if os.path.exists(template_path):
                os.remove(template_path)

            return response
        except Exception as e:
            return BaseView.error(f'下载模板失败: {str(e)}')

    @staticmethod
    def export_students(request):
        """导出学生列表"""
        try:
            grade_id = request.GET.get('gradeId')
            college_id = request.GET.get('collegeId')

            from app.services.export_service import ExportService
            return ExportService.export_student_list(
                grade_id=int(grade_id) if grade_id else None,
                college_id=int(college_id) if college_id else None
            )
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    @staticmethod
    def export_teachers(request):
        """导出教师列表"""
        try:
            from app.services.export_service import ExportService
            return ExportService.export_teacher_list()
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    @staticmethod
    def export_exam_results(request):
        """导出考试结果"""
        try:
            exam_id = request.GET.get('examId')
            if not exam_id:
                return BaseView.error('请提供考试ID')

            from app.services.export_service import ExportService
            return ExportService.export_exam_results(int(exam_id))
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    @staticmethod
    def export_practice_results(request):
        """导出练习结果"""
        try:
            practice_id = request.GET.get('practiceId')
            if not practice_id:
                return BaseView.error('请提供练习ID')

            from app.services.export_service import ExportService
            return ExportService.export_practice_results(int(practice_id))
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')
