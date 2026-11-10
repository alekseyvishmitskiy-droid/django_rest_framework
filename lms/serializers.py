from rest_framework import serializers
from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    last_lesson = serializers.CharField(source='lessons.last.title', read_only=True, default=None)


    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, instance):
        return instance.lessons.count()


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
