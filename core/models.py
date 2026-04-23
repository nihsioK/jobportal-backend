"""Core models: Skills, Categories, and Cities."""

from django.db import models


class JobCategory(models.Model):
    """Broad classification of industries/roles."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Job categories"

    def __str__(self) -> str:
        return self.name


class Skill(models.Model):
    """Specific skill tag."""

    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="skills",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    """Location reference."""

    name = models.CharField(max_length=100, unique=True)
    region = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Cities"

    def __str__(self) -> str:
        if self.region:
            return f"{self.name}, {self.region}"
        return self.name
