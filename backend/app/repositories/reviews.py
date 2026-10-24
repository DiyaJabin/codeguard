import os
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import boto3


def _to_dynamodb(value):
    """
    Convert normal Python values into values supported by DynamoDB.

    DynamoDB/boto3 does not accept Python float values directly,
    so floats are converted to Decimal recursively.
    """
    if isinstance(value, float):
        return Decimal(str(value))

    if isinstance(value, dict):
        return {
            key: _to_dynamodb(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [_to_dynamodb(item) for item in value]

    if isinstance(value, tuple):
        return [_to_dynamodb(item) for item in value]

    return value


def _from_dynamodb(value):
    """
    Convert DynamoDB Decimal values back into normal Python
    int/float values so FastAPI can return JSON responses.
    """
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)

    if isinstance(value, dict):
        return {
            key: _from_dynamodb(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [_from_dynamodb(item) for item in value]

    return value


class DynamoReviewRepository:

    def __init__(self):
        self.table_name = os.environ["REVIEWS_TABLE_NAME"]
        self.region = os.environ.get("AWS_REGION", "ap-south-1")

        dynamodb = boto3.resource(
            "dynamodb",
            region_name=self.region
        )

        self.table = dynamodb.Table(self.table_name)

    def save(self, req, result):
        review_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        item = {
            "review_id": review_id,
            "created_at": created_at,
            "language": req.language,
            "filename": req.filename,
            "analysis_provider": result["analysis_provider"],
            "summary": result["summary"],
            "total_issues": result["total_issues"],
            "severity_counts": result["severity_counts"],
            "category_counts": result["category_counts"],
            "findings": result["findings"],
        }

        # Convert floats recursively before writing to DynamoDB.
        dynamodb_item = _to_dynamodb(item)

        self.table.put_item(Item=dynamodb_item)

        # Return normal Python values to FastAPI.
        return _from_dynamodb(dynamodb_item)

    def get(self, review_id):
        response = self.table.get_item(
            Key={"review_id": review_id}
        )

        item = response.get("Item")

        if not item:
            return None

        return _from_dynamodb(item)

    def delete(self, review_id):
        existing = self.get(review_id)

        if not existing:
            return None

        self.table.delete_item(
            Key={"review_id": review_id}
        )

        return existing

    def list(self, page=1, page_size=20, search="", severity=""):
        response = self.table.scan()
        items = [
            _from_dynamodb(item)
            for item in response.get("Items", [])
        ]

        if search:
            search_lower = search.lower()

            items = [
                item
                for item in items
                if search_lower in item.get("filename", "").lower()
                or search_lower in item.get("language", "").lower()
            ]

        if severity:
            items = [
                item
                for item in items
                if item.get("severity_counts", {}).get(severity, 0) > 0
            ]

        items.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )

        start = (page - 1) * page_size
        end = start + page_size

        page_items = items[start:end]

        return {
            "items": page_items,
            "page": page,
            "page_size": page_size,
            "has_more": end < len(items),
        }

    def stats(self):
        items = [
            _from_dynamodb(item)
            for item in self.table.scan().get("Items", [])
        ]

        langs = {}

        severity = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Informational": 0,
        }

        categories = {}
        days = {}

        for review in items:

            language = review.get("language")

            if language:
                langs[language] = langs.get(language, 0) + 1

            created_at = review.get("created_at", "")
            day = created_at[:10]

            if day:
                days[day] = days.get(day, 0) + 1

            for key, value in review.get(
                "severity_counts", {}
            ).items():

                severity[key] = severity.get(key, 0) + value

            for key, value in review.get(
                "category_counts", {}
            ).items():

                categories[key] = categories.get(key, 0) + value

        total_issues = sum(
            review.get("total_issues", 0)
            for review in items
        )

        return {
            "total_reviews": len(items),

            "total_issues": total_issues,

            "high_severity_issues": (
                severity.get("High", 0)
                + severity.get("Critical", 0)
            ),

            "average_issues_per_review": (
                round(
                    total_issues / len(items),
                    1
                )
                if items
                else 0
            ),

            "by_language": langs,

            "severity": severity,

            "categories": categories,

            "over_time": [
                {
                    "date": key,
                    "reviews": value
                }
                for key, value in sorted(days.items())
            ],
        }