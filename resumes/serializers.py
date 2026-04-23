"""Serializers for resume resources."""

from __future__ import annotations

import logging
from typing import Any, cast

from rest_framework import serializers

from core.models import City, Skill
from .models import Certificate, Education, Language, Resume, WorkExperience

logger = logging.getLogger(__name__)


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        exclude = ("resume",)


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ("resume",)


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        exclude = ("resume",)


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        exclude = ("resume",)


class ResumeSerializer(serializers.ModelSerializer):
    """Serializer for the authenticated user's resume."""

    experience = WorkExperienceSerializer(many=True, required=False)
    education = EducationSerializer(many=True, required=False)
    languages = LanguageSerializer(many=True, required=False)
    certificates = CertificateSerializer(many=True, required=False)

    class Meta:
        model = Resume
        fields = (
            "id",
            "title",
            "summary",
            "desired_salary",
            "city",
            "skills",
            "visibility",
            "experience",
            "education",
            "languages",
            "certificates",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data: dict[str, Any]) -> Resume:
        experience_data = validated_data.pop("experience", [])
        education_data = validated_data.pop("education", [])
        languages_data = validated_data.pop("languages", [])
        certificates_data = validated_data.pop("certificates", [])
        skills = validated_data.pop("skills", [])
        
        user = self.context["request"].user
        validated_data["user"] = user

        resume = Resume.objects.create(**validated_data)
        resume.skills.set(skills)

        for exp in experience_data:
            WorkExperience.objects.create(resume=resume, **exp)
        for edu in education_data:
            Education.objects.create(resume=resume, **edu)
        for lang in languages_data:
            Language.objects.create(resume=resume, **lang)
        for cert in certificates_data:
            Certificate.objects.create(resume=resume, **cert)

        return resume

    def update(self, instance: Resume, validated_data: dict[str, Any]) -> Resume:
        experience_data = validated_data.pop("experience", None)
        education_data = validated_data.pop("education", None)
        languages_data = validated_data.pop("languages", None)
        certificates_data = validated_data.pop("certificates", None)
        skills = validated_data.pop("skills", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if skills is not None:
            instance.skills.set(skills)

        # Simplify nested updates by recreation for MVP
        if experience_data is not None:
            instance.experience.all().delete()
            for exp in experience_data:
                WorkExperience.objects.create(resume=instance, **exp)
                
        if education_data is not None:
            instance.education.all().delete()
            for edu in education_data:
                Education.objects.create(resume=instance, **edu)

        if languages_data is not None:
            instance.languages.all().delete()
            for lang in languages_data:
                Language.objects.create(resume=instance, **lang)

        if certificates_data is not None:
            instance.certificates.all().delete()
            for cert in certificates_data:
                Certificate.objects.create(resume=instance, **cert)

        return instance
