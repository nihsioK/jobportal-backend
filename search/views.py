"""Views for search operations."""

from __future__ import annotations

import logging
from typing import Any

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from search.indexing import get_vacancy_index
from search.serializers import VacancySearchSerializer


logger = logging.getLogger(__name__)


class VacancySearchView(APIView):
    """Public search endpoint for vacancies."""

    authentication_classes: list = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter("q", str, description="Search query string"),
            OpenApiParameter("status", str, description="Filter by vacancy status (e.g., OPEN)"),
            OpenApiParameter("salary_min", int, description="Filter by minimum salary"),
            OpenApiParameter("salary_max", int, description="Filter by maximum salary"),
            OpenApiParameter("employer_id", int, description="Filter by employer ID"),
        ],
        responses={200: VacancySearchSerializer(many=True)},
        tags=["search"],
    )
    def get(self, request: Any) -> Response:
        """Execute a search query against MeiliSearch."""
        query = request.query_params.get("q", "")
        
        # Build filters
        filters = []
        if status_param := request.query_params.get("status"):
            filters.append(f"status = {status_param}")
        
        if salary_min := request.query_params.get("salary_min"):
            filters.append(f"salary_min >= {salary_min}")
            
        if salary_max := request.query_params.get("salary_max"):
            filters.append(f"salary_max <= {salary_max}")
            
        if employer_id := request.query_params.get("employer_id"):
            filters.append(f"employer_id = {employer_id}")

        logger.info("Performing vacancy search: query='%s', filters=%s", query, filters)
        
        try:
            index = get_vacancy_index()
            search_params = {}
            if filters:
                search_params["filter"] = filters
                
            results = index.search(query, search_params)
            hits = results.get("hits", [])
            
            serializer = VacancySearchSerializer(hits, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception("MeiliSearch query failed: %s", e)
            return Response(
                {"error": "Search service temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
