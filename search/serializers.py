"""Serializers for search results."""

from __future__ import annotations

from rest_framework import serializers


class VacancySearchSerializer(serializers.Serializer):
    """Serializer for vacancy search result documents."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    salary_min = serializers.IntegerField()
    salary_max = serializers.IntegerField()
    status = serializers.CharField()
    employer_id = serializers.IntegerField()
    created_at = serializers.FloatField()
    updated_at = serializers.FloatField()
