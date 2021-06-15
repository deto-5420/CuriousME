from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from questions.models import Question, OptionVotes,Options,UserVotes, Category, Like

@receiver(post_save, sender=Question)
def update_category_question_count(sender, instance=None, created=False, **kwargs):
    if created:
        category = Category.objects.get(id=instance.category.id)
        category.total_questions += 1
        category.save()


@receiver([post_save,post_delete], sender=UserVotes)
def Question_upvote(sender, instance=None, created=False, **kwargs):
    vote=instance.vote_type
    if created:
        if vote.lower()=="upvote":
            count=instance.question.upvote_count +1
            print(count)
            Question.objects.filter(id=instance.question.id).update(upvote_count=count)
        else:
            count=instance.question.downvote_count +1
            print(count)
            Question.objects.filter(id=instance.question.id).update(downvote_count=count)
        
    else:
        print(1)

        if vote.lower()=="upvote":

            if instance.question.upvote_count:
                
                count=instance.question.upvote_count -1
                print(count)
                a=Question.objects.filter(id=instance.question.id).update(upvote_count=count)
                
        else:
            if instance.question.downvote_count:
                count=instance.question.downvote_count -1
                print(count)
                Question.objects.filter(id=instance.question.id).update(downvote_count=count)
                
@receiver([post_save,post_delete], sender=OptionVotes)
def update_Option(sender, instance=None, created=False, **kwargs):
    if created:
        option=instance.option
        question=instance.question
        all_option=Options.objects.filter(question=question)
        total_votes=0
        for obj in all_option:
            total_votes+=obj.vote
        total_votes+=1
        for obj in all_option:
            if obj.id==option.id:
                obj.vote_percent=((obj.vote +1)/total_votes) *100
                obj.vote+=1
                obj.save()
                print(all_option,obj.vote)
            else:
                obj.vote_percent=(obj.vote/total_votes) *100
                obj.save()

    else:
        option=instance.option
        question=instance.question
        all_option=Options.objects.filter(question=question)
        total_votes=0
        for obj in all_option:
            total_votes+=obj.vote
        total_votes-=1
        if not total_votes or total_votes <0:
            all_option.update(vote=0,vote_percent=0)
        else:
            for obj in all_option:
                if obj.id==option.id:
                    obj.vote_percent=((obj.vote -1)/total_votes) *100
                    obj.vote-=1
                    obj.save()
                    print(all_option,obj.vote)
                else:
                    obj.vote_percent=(obj.vote/total_votes) *100
                    obj.save()
                
@receiver([post_save,post_delete], sender=Like)
def Question_upvote(sender, instance=None, created=False, **kwargs):
    
    if created:
        
        count=instance.question_id.like_count +1
        Question.objects.filter(id=instance.question_id.id).update(like_count=count)
        
    else:
        if instance.question_id.like_count :      
            count=instance.question_id.like_count -1
            a=Question.objects.filter(id=instance.question_id.id).update(like_count=count)
                
        
