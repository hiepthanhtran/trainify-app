from rest_framework import serializers

from activities.models import Activity, ActivityRegistration, Bulletin, MissingActivityReport
from core.base.serializers import BaseSerializer
from core.utils import factory, validations
from interacts.models import Like


class ActivitySerializer(BaseSerializer):
    class Meta:
        model = Activity
        fields = [
            "id", "name", "participant", "start_date", "end_date",
            "location", "point", "updated_date", "created_date",
            "bulletin", "faculty", "semester", "criterion",
            "image", "organizational_form", "description"
        ]

    def to_representation(self, activity):
        data = super().to_representation(activity)
        image = data.get("image", None)

        if "image" in self.fields and image:
            data["image"] = activity.image.url
        if "bulletin" in self.fields and activity.bulletin:
            data["bulletin"] = f"{activity.bulletin}"
        if "faculty" in self.fields and activity.faculty:
            data["faculty"] = f"{activity.faculty}"
        if "semester" in self.fields and activity.semester:
            data["semester"] = f"{activity.semester}"
        if "criterion" in self.fields and activity.criterion:
            data["criterion"] = f"{activity.criterion}"

        return data

    def create(self, validated_data):
        request = self.context.get("request")

        instance_name = validations.check_account_role(request.user)[0]
        validated_data["organizer"] = getattr(request.user, instance_name, None)
        activity = Activity.objects.create(**validated_data)

        image = validated_data.get("image", None)
        activity.image = factory.get_or_upload_image(file=image, public_id=f"activity-{activity.id}" if image else None, ftype="activity")
        activity.save()

        return activity

    def update(self, activity, validated_data):
        image = validated_data.get("image", None)
        if image:
            validated_data["image"] = factory.get_or_upload_image(file=image, public_id=f"activity-{activity.id}", ftype="activity")

        for key, value in validated_data.items():
            setattr(activity, key, value)
        activity.save()

        return activity


class AuthenticatedActivitySerializer(ActivitySerializer):
    liked = serializers.SerializerMethodField()

    class Meta:
        model = ActivitySerializer.Meta.model
        fields = ActivitySerializer.Meta.fields + ["liked"]

    def get_liked(self, activity):
        request = self.context.get("request")

        try:
            like = Like.objects.get(account=request.user, activity=activity)
        except Like.DoesNotExist:
            return False

        return like.is_active


class AuthenticatedActivityDetailsSerializer(AuthenticatedActivitySerializer):
    organizer = serializers.SerializerMethodField()

    class Meta:
        model = ActivitySerializer.Meta.model
        fields = AuthenticatedActivitySerializer.Meta.fields + ["organizer"]

    def get_organizer(self, activity):
        serializer_class = validations.check_user_instance(activity.organizer)[0]
        return serializer_class(activity.organizer).data


class BulletinSerializer(BaseSerializer):
    class Meta:
        model = Bulletin
        fields = ["id", "title", "cover", "created_date", "updated_date", "content"]

    def to_representation(self, bulletin):
        data = super().to_representation(bulletin)
        cover = data.get("cover")

        if "cover" in self.fields and cover:
            data["cover"] = bulletin.cover.url

        return data

    def create(self, validated_data):
        request = self.context.get("request")

        instance_name = validations.check_account_role(request.user)[0]
        validated_data["poster"] = getattr(request.user, instance_name, None)
        bulletin = Bulletin.objects.create(**validated_data)

        cover = validated_data.pop("cover", None)
        bulletin.cover = factory.get_or_upload_image(file=cover, public_id=f"bulletin-{bulletin.id}" if cover else None, ftype="bulletin")
        bulletin.save()

        return bulletin

    def update(self, bulletin, validated_data):
        cover = validated_data.get("cover", None)
        if cover:
            validated_data["cover"] = factory.get_or_upload_image(file=cover, public_id=f"bulletin-{bulletin.id}")

        for key, value in validated_data.items():
            setattr(bulletin, key, value)
        bulletin.save()

        return bulletin


class BulletinDetailsSerialzer(BulletinSerializer):
    poster = serializers.SerializerMethodField()

    class Meta:
        model = BulletinSerializer.Meta.model
        fields = BulletinSerializer.Meta.fields + ["poster"]

    def get_poster(self, bulletin):
        serializer_class = validations.check_user_instance(bulletin.poster)[0]
        return serializer_class(bulletin.poster).data


class ActivityRegistrationSerializer(BaseSerializer):
    from users import serializers as user_serializers
    student = user_serializers.StudentSerializer()
    activity = ActivitySerializer()

    class Meta:
        model = ActivityRegistration
        fields = ["id", "is_attendance", "is_point_added", "created_date", "updated_date", "student", "activity", ]


class MissingActivityReportSerializer(BaseSerializer):
    from users import serializers as user_serializers
    student = user_serializers.StudentSerializer()
    activity = ActivitySerializer()

    class Meta:
        model = MissingActivityReport
        fields = ["id", "is_resolved", "evidence", "created_date", "updated_date", "content", "student", "activity", ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        evidence = data.get("evidence", None)
        if "evidence" in self.fields and evidence:
            data["evidence"] = instance.evidence.url

        return data
