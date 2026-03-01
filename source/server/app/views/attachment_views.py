"""
任务附件管理视图
支持任务附件的上传、下载、删除等功能
"""
import os
import json
from datetime import datetime
from django.http import HttpResponse, FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from app import models
from app.permissions import get_user_from_request
from comm.BaseView import BaseView


class TaskAttachmentViews:
    """任务附件管理"""
    
    # 允许的文件类型
    ALLOWED_EXTENSIONS = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
        '.ppt', '.pptx', '.txt', '.zip', '.rar',
        '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3'
    ]
    
    # 最大文件大小 (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024

    @staticmethod
    def _require_login(request):
        user = get_user_from_request(request)
        if not user:
            return None, BaseView.error('用户未登录')
        return user, None
    
    @staticmethod
    def upload_attachment(request):
        """
        上传任务附件
        
        参数:
            taskId: 任务ID
            file: 附件文件
        
        返回:
            附件信息
        """
        user, err = TaskAttachmentViews._require_login(request)
        if err:
            return err

        task_id = request.POST.get('taskId')
        uploaded_file = request.FILES.get('file')
        
        if not task_id:
            return BaseView.warn('缺少任务ID')
        
        if not uploaded_file:
            return BaseView.warn('请选择要上传的文件')
        
        # 验证任务是否存在
        try:
            task = models.Tasks.objects.get(id=int(task_id))
        except models.Tasks.DoesNotExist:
            return BaseView.warn('任务不存在')
        
        # 验证文件大小
        if uploaded_file.size > TaskAttachmentViews.MAX_FILE_SIZE:
            return BaseView.warn('文件大小不能超过50MB')
        
        # 验证文件类型
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in TaskAttachmentViews.ALLOWED_EXTENSIONS:
            return BaseView.warn(f'不支持的文件类型: {file_ext}')
        
        # 生成安全的文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_filename = f'task_{task_id}_{timestamp}{file_ext}'
        
        # 保存文件
        upload_dir = os.path.join('uploads', 'task_attachments', str(task_id))
        file_path = os.path.join(upload_dir, safe_filename)
        
        # 确保目录存在
        full_path = os.path.join(settings.MEDIA_ROOT, upload_dir)
        os.makedirs(full_path, exist_ok=True)
        
        # 保存文件
        saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
        
        # 创建附件记录
        attachment = models.TaskAttachments.objects.create(
            task=task,
            fileName=uploaded_file.name,
            filePath=saved_path,
            fileSize=uploaded_file.size,
            fileType=file_ext,
            uploadedBy_id=user.id
        )
        
        return BaseView.successData({
            'id': attachment.id,
            'fileName': attachment.fileName,
            'fileSize': attachment.fileSize,
            'fileType': attachment.fileType,
            'uploadTime': attachment.uploadTime
        })
    
    @staticmethod
    def get_attachments(request):
        """
        获取任务附件列表
        
        参数:
            taskId: 任务ID
        
        返回:
            附件列表
        """
        _, err = TaskAttachmentViews._require_login(request)
        if err:
            return err

        task_id = request.GET.get('taskId')
        
        if not task_id:
            return BaseView.warn('缺少任务ID')
        
        attachments = models.TaskAttachments.objects.filter(
            task_id=task_id
        ).order_by('-uploadTime')
        
        data = [{
            'id': a.id,
            'fileName': a.fileName,
            'fileSize': a.fileSize,
            'fileType': a.fileType,
            'uploadTime': a.uploadTime,
            'uploadedBy': a.uploadedBy.name if a.uploadedBy else ''
        } for a in attachments]
        
        return BaseView.successData(data)
    
    @staticmethod
    def download_attachment(request):
        """
        下载任务附件
        
        参数:
            attachmentId: 附件ID
        
        返回:
            文件下载
        """
        _, err = TaskAttachmentViews._require_login(request)
        if err:
            return err

        attachment_id = request.GET.get('attachmentId')
        
        if not attachment_id:
            return BaseView.warn('缺少附件ID')
        
        try:
            attachment = models.TaskAttachments.objects.get(id=int(attachment_id))
        except models.TaskAttachments.DoesNotExist:
            return BaseView.warn('附件不存在')
        
        # 检查文件是否存在
        file_path = os.path.join(settings.MEDIA_ROOT, attachment.filePath)
        if not os.path.exists(file_path):
            return BaseView.warn('文件不存在')
        
        # 返回文件
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=attachment.fileName
        )
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="{attachment.fileName}"'
        
        return response
    
    @staticmethod
    def delete_attachment(request):
        """
        删除任务附件
        
        参数:
            attachmentId: 附件ID
        
        返回:
            删除结果
        """
        _, err = TaskAttachmentViews._require_login(request)
        if err:
            return err

        attachment_id = request.POST.get('attachmentId')
        
        if not attachment_id:
            return BaseView.warn('缺少附件ID')
        
        try:
            attachment = models.TaskAttachments.objects.get(id=int(attachment_id))
        except models.TaskAttachments.DoesNotExist:
            return BaseView.warn('附件不存在')
        
        # 删除文件
        file_path = os.path.join(settings.MEDIA_ROOT, attachment.filePath)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 删除记录
        attachment.delete()
        
        return BaseView.success('删除成功')
