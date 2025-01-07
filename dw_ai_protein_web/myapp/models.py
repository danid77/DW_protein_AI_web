from django.db import models

# Create your models here.

# class Question(models.Model):
#     subject = models.CharField(max_length=200)
#     content = models.TextField()
#     create_date = models.DateTimeField()
    
    # shell에서 
    # >>> from myapp.models import Question, Answer
    # >>> Question.objects.all()
    # 입력시 id 대신에 subject가 출력되게 하는 코드
    # 대신 변경할 때마다 재시작 해야함
    # def __str__(self):
    #     return self.subject
    
    # 메소드가 추가될 때는 makemigrations와 migrate 명령을 할 필요 없음
    # 대산에 DB의 속성이 변경될 때는 makemigrations와 migrate 명령을 해서 DB수정을
    
class Alphafold3(models.Model):
    result_path = models.TextField()
    create_date = models.DateTimeField()


class chaiLab(models.Model):
    result_path = models.TextField()
    create_date = models.DateTimeField()

