import logging
import re
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

from app.models.db import execute_query

logger = logging.getLogger(__name__)

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

ASSET_CLASSES = ['Equities', 'Bonds', 'FX', 'Commodities', 'Crypto', 'Real Estate']

signals_bp = Blueprint('signals', __name__)


@signals_bp.route('/api/signals')
def get_signals():
    """Fetch unthemed articles with asset tags, grouped by asset class."""
    try:
        from_date = request.args.get('from', '').strip() or None
        to_date = request.args.get('to', '').strip() or None

        # Validate date format and parse to catch invalid dates like 2026-99-99
        if from_date:
            if not DATE_RE.match(from_date):
                return jsonify({'error': True, 'message': 'Invalid date format, use YYYY-MM-DD', 'code': 'INVALID_DATE'}), 400
            try:
                datetime.strptime(from_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': True, 'message': 'Invalid date value', 'code': 'INVALID_DATE'}), 400
        if to_date:
            if not DATE_RE.match(to_date):
                return jsonify({'error': True, 'message': 'Invalid date format, use YYYY-MM-DD', 'code': 'INVALID_DATE'}), 400
            try:
                datetime.strptime(to_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': True, 'message': 'Invalid date value', 'code': 'INVALID_DATE'}), 400

        # Build parameterized date filters
        # SAFETY: clauses are hardcoded strings only — never interpolate user input
        params = []

        if from_date:
            params.append(from_date)
        else:
            # Default: last 30 days
            params.append((datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%d'))

        if to_date:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
            params.append(to_dt.strftime('%Y-%m-%d'))

        # Use explicit SQL branches instead of f-string clause assembly
        if to_date:
            articles = execute_query(
                """
                SELECT id, title, url, source_name, published_at, asset_tags
                FROM articles
                WHERE theme_id IS NULL
                  AND asset_tags IS NOT NULL
                  AND array_length(asset_tags, 1) > 0
                  AND published_at >= %s
                  AND published_at < %s
                ORDER BY published_at DESC
                LIMIT 200
                """,
                tuple(params),
            )
        else:
            articles = execute_query(
                """
                SELECT id, title, url, source_name, published_at, asset_tags
                FROM articles
                WHERE theme_id IS NULL
                  AND asset_tags IS NOT NULL
                  AND array_length(asset_tags, 1) > 0
                  AND published_at >= %s
                ORDER BY published_at DESC
                LIMIT 200
                """,
                tuple(params),
            )

        # Group articles by asset class
        grouped = {cls: [] for cls in ASSET_CLASSES}
        total = len(articles)

        for article in articles:
            item = {
                'id': article['id'],
                'title': article['title'],
                'url': article['url'],
                'source_name': article['source_name'],
                'published_at': article['published_at'].isoformat() if hasattr(article['published_at'], 'isoformat') else article['published_at'],
            }
            tags = article.get('asset_tags') or []
            for tag in tags:
                if tag in grouped:
                    grouped[tag].append(item)

        return jsonify({
            'data': grouped,
            'meta': {
                'total_articles': total,
                'last_updated': datetime.now(timezone.utc).isoformat(),
            }
        })

    except Exception as e:
        logger.exception('Signals endpoint error: %s', e)
        return jsonify({
            'error': True,
            'message': 'An internal error occurred while fetching signals.',
            'code': 'SIGNALS_ERROR'
        }), 500
