from rest_framework import serializers
from lms.models import Course, Lesson, Subscription
from lms.validators import YoutubeOnlyValidator


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [YoutubeOnlyValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):
    last_lesson = serializers.CharField(source='lessons.last.title', read_only=True, default=None)
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'preview',
            'description',
            'owner',
            'last_lesson',
            'lessons',
            'lessons_count',
            'is_subscribed'
        ]

    def get_lessons_count(self, instance):
        return instance.lessons.count()

    def get_is_subscribed(self, instance):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, course=instance).exists()


class CourseCreateSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, required=False)

    class Meta:
        model = Course
        fields = '__all__'

    def create(self, validated_data):
        lessons_data = validated_data.pop('lessons', [])
        course_item = Course.objects.create(**validated_data)

        for lesson in lessons_data:
            Lesson.objects.create(**lesson, course=course_item)

        return course_item
