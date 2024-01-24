from django.shortcuts import get_object_or_404

from rest_framework import generics, mixins
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN

from .models import Survey, Question, Answer

import survey.serializers as serializers

from .permissions import IsOwnerOfSurvey, IsSurveyDraft


# survey

class ShowMySurveyAPIView(generics.ListAPIView):
    queryset = Survey.objects.all()
    serializer_class = serializers.SurveyListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.surveys


class SurveyCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.SurveyCreateSerializer
    permission_classes = (IsAuthenticated,)


class SurveyDeleteAPIView(generics.DestroyAPIView):
    queryset = Survey.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOfSurvey)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class SurveyUpdateAPIView(generics.GenericAPIView, UpdateModelMixin):
    queryset = Survey.objects.all()
    serializer_class = serializers.SurveyUpdateSerializer
    permission_classes = (IsAuthenticated, IsSurveyDraft, IsOwnerOfSurvey)
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class PublishedSurvey(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Survey.objects.all()
    serializer_class = serializers.SurveyPublishedSerializer
    permission_classes = (IsAuthenticated, IsOwnerOfSurvey,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class SurveyDetailAPIView(generics.RetrieveAPIView):
    queryset = Survey.is_published.all()
    serializer_class = serializers.ShowSurveyDetailSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class SurveyListAPIView(generics.ListAPIView):
    queryset = Survey.is_published
    serializer_class = serializers.SurveyListSerializer


class SurveySubmitAPIView(generics.GenericAPIView):
    serializer_class = serializers.QuestionSubmitSerializer
    permission_classes = (IsAuthenticated,)

    def is_user_pass_survey(self, user, survey):
        return user in survey.passed_users()

    def get_survey(self):
        return get_object_or_404(Survey.is_published, slug=self.kwargs.get('slug', None))

    def _add_user_to_answers(self, serializer, user):
        answers = [answer for data in serializer.data for answer in data.get('answers')]
        answers = Answer.objects.filter(pk__in=answers)
        for answer in answers:
            answer.add_user(user)

    def _add_user_to_survey(self, survey, user):
        survey.add_user_pass(user=user)

    def post(self, request, *args, **kwargs):
        """
        The expected data for serializer is
        {
            "answers": [
                {"question_id": id, "answers": [id]},
                {"question_id": id,"answers": [id]},
                {"question_id": id, "answers": [id]},
                {"question_id": id, "answers": [id]}
            ]
        }
        """
        user = self.request.user
        survey = self.get_survey()
        if not self.is_user_pass_survey(survey=survey, user=user):
            serializer = serializers.QuestionSubmitSerializer(data=request.data.get('answers'),
                                                              context={'survey': survey},
                                                              many=True)
            serializer.is_valid(raise_exception=True)
            self._add_user_to_answers(serializer=serializer, user=user)
            self._add_user_to_survey(survey=survey, user=user)
            return Response(data=serializer.data)

        return Response(data={'msg': "You've already taken this survey"}, status=HTTP_403_FORBIDDEN)


class ShowStatisticOfSurvey(generics.RetrieveAPIView):
    queryset = Survey.objects.all()
    serializer_class = serializers.SurveyStatisticSerializer
    permission_classes = (IsAuthenticated, IsOwnerOfSurvey)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


# question
class QuestionCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.QuestionCreateSerializer
    permission_classes = (IsAuthenticated, IsSurveyDraft, IsOwnerOfSurvey,)

    def get_survey(self):
        survey = get_object_or_404(Survey, slug=self.kwargs.get('survey_slug'))
        self.check_object_permissions(request=self.request, obj=survey)
        return survey

    def perform_create(self, serializer):
        return serializer.save(survey=self.get_survey())


class QuestionDeleteAPIView(generics.DestroyAPIView):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticated, IsSurveyDraft, IsOwnerOfSurvey,)

    def get_object(self):
        question = get_object_or_404(Question, pk=self.kwargs.get('pk'))
        survey = question.survey
        self.check_object_permissions(request=self.request, obj=survey)
        return question


# answer
class AddAnswerToQuestionAPIView(generics.CreateAPIView):
    serializer_class = serializers.AnswerCreateSerializer
    permission_classes = (IsAuthenticated, IsSurveyDraft, IsOwnerOfSurvey,)

    def get_question(self):
        question = get_object_or_404(Question, pk=self.kwargs.get('question_id'))
        survey = question.survey
        self.check_object_permissions(request=self.request, obj=survey)
        return question

    def perform_create(self, serializer):
        return serializer.save(question=self.get_question())


class DeleteAnswerAPIView(generics.DestroyAPIView):
    answer = Answer.objects.all()
    permission_classes = (IsAuthenticated, IsSurveyDraft, IsOwnerOfSurvey,)

    def get_object(self):
        answer = get_object_or_404(Answer, pk=self.kwargs.get('pk'))
        survey = answer.question.survey
        self.check_object_permissions(request=self.request, obj=survey)
        return answer
