from rest_framework import serializers
from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    last_lesson = serializers.CharField(source='lesson_set.all.first.title', read_only=True)


    lessons = LessonSerializer(source='lesson_set', many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, instance):
        if instance.lesson_set.all():
            return instance.lesson_set.all().count()
        return 0


class CourseCreateSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Course
        fields = '__all__'

    def create(self, validated_data):
        lessons_data = validated_data.pop('lessons', [])


        course_item = Course.objects.create(**validated_data)


        for lesson in lessons_data:
            Lesson.objects.create(**lesson, course=course_item)

        return course_item
