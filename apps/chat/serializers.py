from rest_framework import serializers
from .models import Conversation, Message
from apps.users.models import User

class UserChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role']
        
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['full_name'] = instance.get_full_name() or instance.username
        
        # Try to get store details if it's a vendor/institution
        if instance.role in ['VENDOR', 'INSTITUTION', 'SELLER']:
            try:
                store = instance.store
                repr['store_name'] = store.name or repr['full_name']
                if store.logo:
                    repr['logo'] = store.logo.url
            except Exception:
                pass
        return repr

class MessageSerializer(serializers.ModelSerializer):
    sender = UserChatSerializer(read_only=True)
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'content', 'is_read', 'created_at', 'sender', 'is_me']
        
    def get_is_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False

class ConversationListSerializer(serializers.ModelSerializer):
    partner = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'partner', 'last_message', 'unread_count', 'updated_at']

    def get_partner(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        partner_obj = obj.participant2 if obj.participant1 == request.user else obj.participant1
        return UserChatSerializer(partner_obj, context=self.context).data

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return {
                'content': msg.content,
                'created_at': msg.created_at,
                'is_read': msg.is_read,
                'is_me': self.context['request'].user == msg.sender
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()

class ConversationDetailSerializer(serializers.ModelSerializer):
    partner = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'partner', 'messages', 'created_at']

    def get_partner(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        partner_obj = obj.participant2 if obj.participant1 == request.user else obj.participant1
        return UserChatSerializer(partner_obj, context=self.context).data
