"""
管理员消息管理相关视图

从 admin 视图中拆分消息管理逻辑，降低单文件复杂度。
"""

import os

from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import FileResponse

from app import models
from comm.BaseView import BaseView


class AdminMessageView:
    """管理员消息管理接口集合"""

    @staticmethod
    def get_messages(request):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', request.GET.get('pageSize', 10)))
            search = request.GET.get('search', '') or request.GET.get('keyword', '')
            message_type = request.GET.get('type', '')

            messages_query = models.Messages.objects.select_related(
                'sender'
            ).prefetch_related(
                'messagereads_set'
            ).all().order_by('-createTime', '-id')

            if search:
                messages_query = messages_query.filter(title__icontains=search)
            if message_type:
                messages_query = messages_query.filter(type=message_type)

            total = messages_query.count()
            paginator = Paginator(messages_query, size)
            messages_page = paginator.get_page(page)

            messages_data = []
            for message in messages_page:
                total_recipients = message.messagereads_set.count()
                read_count = message.messagereads_set.filter(isRead=True).count()
                unread_count = total_recipients - read_count
                read_rate = round(read_count / total_recipients * 100) if total_recipients > 0 else 0

                attachments_data = []
                if hasattr(message, 'attachments'):
                    for att in message.attachments.all():
                        attachments_data.append({
                            'id': att.id,
                            'name': att.name,
                            'size': att.size or 0,
                            'url': att.file.url if att.file else ''
                        })

                messages_data.append({
                    'id': message.id,
                    'title': message.title,
                    'content': message.content,
                    'type': message.type,
                    'priority': message.priority,
                    'senderId': message.sender.id if message.sender else None,
                    'senderName': message.sender.name if message.sender else '',
                    'createTime': message.createTime.strftime('%Y-%m-%d %H:%M:%S') if message.createTime else '',
                    'readCount': read_count,
                    'unreadCount': unread_count,
                    'readRate': read_rate,
                    'receiverCount': total_recipients,
                    'totalRecipients': total_recipients,
                    'attachments': attachments_data
                })

            return BaseView.successData({
                'list': messages_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取消息列表失败: {str(e)}')

    @staticmethod
    def get_message_readers(request):
        try:
            message_id = request.GET.get('messageId')
            if not message_id:
                return BaseView.error('消息ID不能为空')

            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('pageSize', 10))

            qs = models.MessageReads.objects.filter(message_id=message_id).select_related('user')
            paginator = Paginator(qs.order_by('-readTime'), size)
            page_obj = paginator.get_page(page)

            readers = []
            for mr in page_obj:
                user = mr.user
                readers.append({
                    'id': mr.id,
                    'userId': user.id if user else None,
                    'userName': user.userName if user else '',
                    'realName': user.name if user else '',
                    'userType': user.type if user else None,
                    'isRead': mr.isRead,
                    'readTime': mr.readTime.strftime('%Y-%m-%d %H:%M:%S') if mr.readTime else ''
                })

            total_count = qs.count()
            read_count = qs.filter(isRead=True).count()
            unread_count = total_count - read_count
            read_rate = round(read_count / total_count * 100) if total_count > 0 else 0

            return BaseView.successData({
                'totalCount': total_count,
                'readCount': read_count,
                'unreadCount': unread_count,
                'readRate': read_rate,
                'readers': readers,
                'page': page,
                'pageSize': size,
                'total': total_count
            })
        except Exception as e:
            return BaseView.error(f'获取已读情况失败: {str(e)}')

    @staticmethod
    def manage_messages(request):
        try:
            action = request.POST.get('action')

            if action in ('send', 'add'):
                title = request.POST.get('title')
                content = request.POST.get('content')
                message_type = request.POST.get('type', 'notice')
                priority = request.POST.get('priority', 'medium')
                user_type = request.POST.get('userType', 'all')
                recipient_ids = request.POST.getlist('recipientIds[]')

                sender_id = cache.get(request.POST.get('token'))
                sender = models.Users.objects.filter(id=sender_id).first()
                if not sender:
                    return BaseView.error('发送者不存在或未登录，请重新登录后再试')

                message = models.Messages.objects.create(
                    title=title,
                    content=content,
                    type=message_type,
                    priority=priority,
                    sender=sender
                )

                files = request.FILES.getlist('attachments') or request.FILES.getlist('attachmentFiles')
                if hasattr(models, 'MessageAttachments'):
                    for file_obj in files:
                        models.MessageAttachments.objects.create(
                            message=message,
                            file=file_obj,
                            name=getattr(file_obj, 'name', ''),
                            size=getattr(file_obj, 'size', None)
                        )

                if user_type != 'custom':
                    qs = models.Users.objects.all()
                    if user_type == 'admin':
                        qs = qs.filter(type=0)
                    elif user_type == 'teacher':
                        qs = qs.filter(type=1)
                    elif user_type == 'student':
                        qs = qs.filter(type=2)
                    recipient_ids = [user.id for user in qs]

                for recipient_id in recipient_ids:
                    recipient = models.Users.objects.filter(id=recipient_id).first()
                    if recipient:
                        models.MessageReads.objects.create(
                            message=message,
                            user=recipient,
                            isRead=False
                        )

                return BaseView.success('消息发送成功')

            if action == 'forward':
                message_id = request.POST.get('messageId')
                recipient_ids = request.POST.getlist('recipientIds[]')

                if not message_id or not recipient_ids:
                    return BaseView.error('请选择要转发的消息和接收者')

                original_message = models.Messages.objects.filter(id=message_id).first()
                if not original_message:
                    return BaseView.error('消息不存在')

                forwarder_id = cache.get(request.POST.get('token'))
                forwarder = models.Users.objects.filter(id=forwarder_id).first()
                if not forwarder:
                    return BaseView.error('用户未登录')

                forwarded_title = f"转发：{original_message.title}"
                sender_name = original_message.sender.name if original_message.sender else '系统'
                forwarded_content = f"【转发自 {sender_name}】\n\n{original_message.content}"

                forwarded_message = models.Messages.objects.create(
                    title=forwarded_title,
                    content=forwarded_content,
                    type=original_message.type,
                    priority=original_message.priority,
                    sender=forwarder
                )

                if hasattr(models, 'MessageAttachments') and hasattr(original_message, 'attachments'):
                    for att in original_message.attachments.all():
                        models.MessageAttachments.objects.create(
                            message=forwarded_message,
                            file=att.file,
                            name=att.name,
                            size=att.size
                        )

                for recipient_id in recipient_ids:
                    recipient = models.Users.objects.filter(id=recipient_id).first()
                    if recipient:
                        models.MessageReads.objects.create(
                            message=forwarded_message,
                            user=recipient,
                            isRead=False
                        )

                return BaseView.success('消息转发成功')

            if action == 'delete':
                message_id = request.POST.get('id')
                message = models.Messages.objects.filter(id=message_id).first()
                if not message:
                    return BaseView.error('消息不存在')

                if hasattr(models, 'MessageAttachments'):
                    models.MessageAttachments.objects.filter(message=message).delete()
                models.MessageReads.objects.filter(message=message).delete()

                message.delete()
                return BaseView.success('消息删除成功')

            return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'消息操作失败: {str(e)}')

    @staticmethod
    def download_message_attachment(request):
        try:
            if not hasattr(models, 'MessageAttachments'):
                return BaseView.error('当前版本未启用消息附件功能')

            attachment_id = request.GET.get('id')
            if not attachment_id:
                return BaseView.error('缺少附件ID')

            attachment = models.MessageAttachments.objects.filter(id=attachment_id).first()
            if not attachment or not attachment.file:
                return BaseView.error('附件不存在')

            filename = attachment.name or os.path.basename(attachment.file.name)
            return FileResponse(attachment.file.open('rb'), as_attachment=True, filename=filename)
        except Exception as e:
            return BaseView.error(f'下载附件失败: {str(e)}')
