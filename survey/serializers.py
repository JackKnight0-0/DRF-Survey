from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Survey, Question, Answer


# survey serializers
class SurveyCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Survey
        fields = (
            'owner',
            'title',
            'description'
        )


class SurveyListSerializer(serializers.ModelSerializer):
    absolute_url = serializers.URLField(read_only=True, source='get_absolute_url')

    class Meta:
        model = Survey
        fields = (
            'title',
            'description',
            'absolute_url'
        )


class SurveyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            'title',
            'description',
        )


class SurveyPublishedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            'published',
        )

    def check_survey_having_questions(self, instance):
        if not instance.question.all().exists():
            raise ValidationError({'published': 'The survey cannot be published without questions!'})

    def check_all_questions(self, instance):
        questions = instance.question.all()
        for question in questions:
            if question.question_type == 'BINARY' and len(question.answers.all()) != 2:
                raise ValidationError({'question': f'The question ({question.pk}) have to have only 2 answers!'})
            elif len(question.answers.all()) < 2:
                raise ValidationError({'question': f'The question ({question.pk}) have to have more questions!'})

    def update(self, instance, validated_data):
        self.check_survey_having_questions(instance=instance)
        self.check_all_questions(instance=instance)
        return super().update(instance=instance, validated_data=validated_data)


class ShowSurveyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            'title',
            'description',
            'question',
        )

    def to_representation(self, instance):
        order_dict = super().to_representation(instance=instance)
        questions = QuestionSerializer(data=instance.question, many=True)
        questions.is_valid()
        order_dict['question'] = questions.data  # rewrite the answers id to question data
        return order_dict


class SurveyStatisticSerializer(serializers.ModelSerializer):
    passed_users = serializers.IntegerField(read_only=True, source='how_many_user_passes')

    class Meta:
        model = Survey
        fields = (
            'title',
            'description',
            'question',
            'passed_users'
        )

    def to_representation(self, instance):
        order_dict = super().to_representation(instance=instance)
        questions = QuestionStatisticSerializer(data=instance.question.all(), many=True)
        questions.is_valid()
        order_dict['question'] = questions.data  # rewrite the answers id to question data
        return order_dict


# questions serializers
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'pk',
            'question',
            'question_type',
            'answers'
        )

    def to_representation(self, instance):
        order_dict = super().to_representation(instance=instance)
        answers = AnswerSerializer(data=instance.answers, many=True)
        answers.is_valid()
        order_dict['answers'] = answers.data  # rewrite the answers id to answers data
        return order_dict


class QuestionStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'pk',
            'question',
            'question_type',
            'answers'
        )

    def to_representation(self, instance):
        order_dict = super().to_representation(instance=instance)
        answers = AnswerStatisticSerializer(data=instance.answers, many=True)
        answers.is_valid()
        order_dict['answers'] = answers.data  # rewrite the answers id to answers data
        return order_dict


class QuestionCreateSerializer(serializers.ModelSerializer):
    survey = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Question
        fields = (
            'survey',
            'question',
            'question_type',
        )


class QuestionSubmitSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(required=True)

    class Meta:
        model = Question
        fields = (
            'question_id',
            'answers'
        )

    def _check_if_question_in_survey(self, survey, question):
        if question not in survey.question.all():
            raise ValidationError({'question': "The question doesn't belong to this survey!"})

    def _check_if_answers_is_empty(self, question, answers):
        if not answers:
            raise ValidationError({'question': f'The {question.question} is required question!'})

    def _check_answer_to_question(self, question, answers):
        for answer in answers:
            if answer.question != question:
                raise ValidationError({'answer': "The answer doesn't belong to this question!"})

    def _check_amount_of_answers(self, question, answers):
        if (question.question_type == 'BINARY' and len(answers) > 1) or (
                question.question_type == 'DEFAULT' and len(answers) > 1):
            raise ValidationError({'question': f'The question {question.question} can have only one answer!'})

    def validate(self, attrs):
        """
        attrs have to have such data as: {'question_id': id, 'answers': [AnswerModel, ...]
        """
        question = get_object_or_404(Question, pk=attrs.get('question_id'))
        answers = attrs.get('answers')
        survey = self.context.get('survey')  # getting the survey from context
        self._check_if_question_in_survey(survey=survey, question=question)
        self._check_if_answers_is_empty(question=question, answers=answers)
        self._check_amount_of_answers(question=question, answers=answers)
        self._check_answer_to_question(question=question, answers=answers)
        return super().validate(attrs)


# answer serializers
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'pk',
            'answer'
        )


class AnswerStatisticSerializer(serializers.ModelSerializer):
    user_answered = serializers.IntegerField(read_only=True, source='how_many_user_answered')

    class Meta:
        model = Answer
        fields = (
            'answer',
            'user_answered'
        )


class AnswerCreateSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Answer
        fields = (
            'question',
            'answer'
        )
