import csv

from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from activities import serializers as activities_serializers
from activities.models import Activity, Participation, DeficiencyReport
from interacts import serializers as interacts_serializers
from interacts.models import Like
from schools.models import TrainingPoint
from tpm import paginators, perms
from tpm.filters import DeficiencyReportFilter
from users.models import Student


class ActivityViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveAPIView):
    queryset = Activity.objects.prefetch_related("list_of_participants").filter(is_active=True)
    serializer_class = activities_serializers.ActivitySerializer
    pagination_class = paginators.ActivityPagination

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            if self.request.user.has_in_activities_group():
                return activities_serializers.AuthenticatedActivityDetailsSerializer

            return activities_serializers.AuthenticatedActivitySerializer

        return self.serializer_class

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [perms.HasInActivitiesGroup()]

        if self.action in ["register_activity", "report_deficiency"]:
            return [perms.IsStudent()]

        if self.action in ["add_comment", "like"]:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=["post"], detail=True, url_path="register-activity")
    def register_activity(self, request, pk=None):
        participation, created = self.get_object().participations.get_or_create(student=request.user.student)
        if not created:
            return Response(data={"message": "Bạn đã đăng ký tham gia hoạt động này rồi!"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data=activities_serializers.ParticipationSerializer(participation).data, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=True, url_path="report-deficiency")
    def report_deficiency(self, request, pk=None):
        activity = self.get_object()
        student = request.user.student

        try:
            participation = self.get_object().participations.get(student=request.user.student)
        except ObjectDoesNotExist:
            return Response(data={"message": "Bạn chưa đăng ký tham gia hoạt động này"}, status=status.HTTP_400_BAD_REQUEST)

        if participation.is_attendance and participation.is_point_added:
            return Response(data={"message": "Bạn không thể báo thiếu hoạt động đã được cộng điểm"}, status=status.HTTP_400_BAD_REQUEST)

        report, created = DeficiencyReport.objects.get_or_create(student=student, activity=activity)

        if not created:
            return Response(data={"message": "Bạn đã báo thiếu điểm cho hoạt động này rồi!"}, status=status.HTTP_400_BAD_REQUEST)

        image = request.data.get("image", None)
        content = request.data.get("content", None)

        report.image = image
        report.content = content
        report.save()

        return Response(data=activities_serializers.DeficiencyReportSerializer(report).data, status=status.HTTP_201_CREATED)

    @action(methods=["get"], detail=True, url_path="comments")
    def get_comments(self, request, pk=None):
        comments = self.get_object().comment_set.select_related("account").all()

        paginator = paginators.CommentPaginators()
        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            serializer = interacts_serializers.CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(data=interacts_serializers.CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=True, url_path="add-comment")
    def add_comment(self, request, pk=None):
        comment = self.get_object().comment_set.create(content=request.data["content"], account=request.user)

        return Response(interacts_serializers.CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=True, url_path="like")
    def like(self, request, pk=None):
        activity, account = self.get_object(), request.user

        like, created = Like.objects.get_or_create(activity=activity, account=account)
        if not created:
            like.is_active = not like.is_active
            like.save()

        serializer = activities_serializers.AuthenticatedActivitySerializer(activity, context={"request": request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class DeficiencyReportViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = DeficiencyReport.objects.filter(is_active=True)
    serializer_class = activities_serializers.DeficiencyReportSerializer
    permission_classes = [perms.HasInActivitiesGroup]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DeficiencyReportFilter

    @action(methods=["post"], detail=True, url_path="confirm")
    def confirm_deficiency_report(self, request, pk=None):
        report = self.get_object()

        if report.is_resolved is True:
            return Response(data={"message": "Báo thiếu này đã được giải quyết!"}, status=status.HTTP_400_BAD_REQUEST)

        participation = Participation.objects.get(student=report.student, activity=report.activity)

        training_point, _ = TrainingPoint.objects.get_or_create(
            student=participation.student,
            semester=participation.activity.semester,
            criterion=participation.activity.criterion,
        )
        training_point.point += participation.activity.point
        training_point.save()

        participation.is_point_added = True
        participation.is_attendance = True
        participation.save()

        report.is_resolved = True
        report.save()

        return Response(data=activities_serializers.DeficiencyReportSerializer(report).data, status=status.HTTP_200_OK)

    @action(methods=["delete"], detail=True, url_path="refuse")
    def refuse_deficiency_report(self, request, pk=None):
        report = self.get_object()
        if report.is_resolved is False:
            report.delete()
            return Response(data=activities_serializers.DeficiencyReportSerializer(report).data, status=status.HTTP_200_OK)

        return Response(data={}, status=status.HTTP_204_NO_CONTENT)



class AttendanceViewSet(APIView):
    permission_classes = [perms.HasInActivitiesGroup]

    def post(self, request):
        file = request.FILES.get("file", None)
        if file is None:
            return Response(data={"message": "Không tìm thấy file!"}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith(".csv"):
            return Response(data={"message": "Vui lòng upload file có định dạng là csv"}, status=status.HTTP_400_BAD_REQUEST)

        csv_data = csv.reader(file.read().decode("utf-8").splitlines())
        next(csv_data)
        for row in csv_data:
            student_code, activity_id = row
            student = Student.objects.get(code=student_code)
            activity = Activity.objects.get(pk=activity_id)
            if student and activity:
                participation, _ = Participation.objects.get_or_create(student=student, activity=activity)
                if not participation.is_attendance:
                    training_point, _ = TrainingPoint.objects.get_or_create(
                        semester=activity.semester, criterion=activity.criterion, student=student
                    )
                    training_point.point += activity.point
                    training_point.save()

                    participation.is_point_added = True
                    participation.is_attendance = True
                    participation.save()

        return Response(data={"message": "Upload file điểm danh thành công"}, status=status.HTTP_200_OK)
