from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from apps.users.models import User
from .models import Conversation, Message
from .serializers import ConversationListSerializer, ConversationDetailSerializer, MessageSerializer

class ConversationListView(generics.ListAPIView):
    """جلب جميع المحادثات للمستخدم الحالي"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationListSerializer

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            Q(participant1=user) | Q(participant2=user)
        ).prefetch_related('messages')

class ConversationDetailView(generics.RetrieveAPIView):
    """جلب تفاصيل محادثة محددة مع جميع الرسائل"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            Q(participant1=user) | Q(participant2=user)
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Mark unread messages as read
        instance.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class SendMessageView(views.APIView):
    """إرسال رسالة جديدة (عبر رقم المحادثة أو رقم المستخدم الثاني)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        content = request.data.get('content')
        conversation_id = request.data.get('conversation_id')
        receiver_id = request.data.get('receiver_id')

        if not content:
            return Response({'error': 'محتوى الرسالة مطلوب'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. إذا كان لدينا رقم المحادثة
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                )
                if user not in [conversation.participant1, conversation.participant2]:
                    return Response({'error': 'غير مسموح لك بالوصول لهذه المحادثة'}, status=status.HTTP_403_FORBIDDEN)
            except Conversation.DoesNotExist:
                return Response({'error': 'المحادثة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)

        # 2. أو إذا كان لدينا رقم المستلم (مستخدم أو تاجر)
        elif receiver_id:
            try:
                receiver = User.objects.get(id=receiver_id)
                conversation = Conversation.get_or_create_conversation(user, receiver)
            except User.DoesNotExist:
                return Response({'error': 'المستخدم غير موجود'}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({'error': 'يجب توفير رقم المحادثة أو رقم المستلم'}, status=status.HTTP_400_BAD_REQUEST)

        # إنشاء الرسالة
        msg = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content
        )
        
        # Updating the updated_at on conversation manually to bubble it up
        conversation.save()

        serializer = MessageSerializer(msg, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
