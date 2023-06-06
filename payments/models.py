from django.db import models
from users.models import User

# Create your models here.


class Payment(models.Model):
    '''
    작성자 : 송지명
    작성날짜 : 2023.06.06
    작성내용 : 결제 시스템 모델
    업데이트 날짜 :
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount= models.PositiveIntegerField()
    payment_Token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

