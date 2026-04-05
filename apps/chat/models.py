from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """
    محادثة بين مستخدمين (زبون وتاجر مثلاً).
    """
    participant1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='conversations_initiated', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='conversations_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Prevent duplicate conversations between same participants
        unique_together = ('participant1', 'participant2')
        verbose_name = 'محادثة'
        verbose_name_plural = 'المحادثات'

    def __str__(self):
        return f"محادثة بين {self.participant1.username} و {self.participant2.username}"
    
    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        # We ensure participant1 is always the one with lower ID to enforce uniqueness
        p1, p2 = sorted([user1, user2], key=lambda u: u.id)
        conv, created = cls.objects.get_or_create(participant1=p1, participant2=p2)
        return conv

class Message(models.Model):
    """
    رسالة فردية داخل المحادثة.
    """
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages_sent', on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'رسالة'
        verbose_name_plural = 'الرسائل'

    def __str__(self):
        return f"رسالة من {self.sender.username} في {self.created_at.strftime('%Y-%m-%d %H:%M')}"
