# Manual migration for A/B metrics conversion

from django.db import migrations, models


def convert_to_ab_format(apps, schema_editor):
    """Convert existing metrics to A/B format"""
    PostMetrics = apps.get_model('metrics', 'PostMetrics')

    for metric in PostMetrics.objects.all():
        # Store old values temporarily
        old_likes = metric.likes if isinstance(metric.likes, int) else 0
        old_retweets = metric.retweets if isinstance(metric.retweets, int) else 0
        old_impressions = metric.impressions if isinstance(metric.impressions, int) else 0
        old_comments = metric.comments if isinstance(metric.comments, int) else 0
        old_tweet_id = metric.tweet_id if isinstance(metric.tweet_id, str) else ""
        old_comment_list = metric.commentList if isinstance(metric.commentList, list) else []

        # Set new JSON format (variant A gets old data, variant B is empty)
        metric.likes_json = {"A": old_likes, "B": 0}
        metric.retweets_json = {"A": old_retweets, "B": 0}
        metric.impressions_json = {"A": old_impressions, "B": 0}
        metric.comments_json = {"A": old_comments, "B": 0}
        metric.tweet_id_json = {"A": old_tweet_id, "B": ""}
        metric.commentList_json = {"A": old_comment_list, "B": []}

        metric.save()


def reverse_ab_format(apps, schema_editor):
    """Reverse migration: convert A/B format back to single values"""
    PostMetrics = apps.get_model('metrics', 'PostMetrics')

    for metric in PostMetrics.objects.all():
        # Take variant A as the single value
        metric.likes = metric.likes_json.get("A", 0) if isinstance(metric.likes_json, dict) else 0
        metric.retweets = metric.retweets_json.get("A", 0) if isinstance(metric.retweets_json, dict) else 0
        metric.impressions = metric.impressions_json.get("A", 0) if isinstance(metric.impressions_json, dict) else 0
        metric.comments = metric.comments_json.get("A", 0) if isinstance(metric.comments_json, dict) else 0
        metric.tweet_id = metric.tweet_id_json.get("A", "") if isinstance(metric.tweet_id_json, dict) else ""
        metric.commentList = metric.commentList_json.get("A", []) if isinstance(metric.commentList_json, dict) else []

        metric.save()


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0010_alter_postmetrics_tweet_id'),
    ]

    operations = [
        # Step 1: Add new JSON fields with temporary names
        migrations.AddField(
            model_name='postmetrics',
            name='likes_json',
            field=models.JSONField(default=dict, null=True),
        ),
        migrations.AddField(
            model_name='postmetrics',
            name='retweets_json',
            field=models.JSONField(default=dict, null=True),
        ),
        migrations.AddField(
            model_name='postmetrics',
            name='impressions_json',
            field=models.JSONField(default=dict, null=True),
        ),
        migrations.AddField(
            model_name='postmetrics',
            name='comments_json',
            field=models.JSONField(default=dict, null=True),
        ),
        migrations.AddField(
            model_name='postmetrics',
            name='tweet_id_json',
            field=models.JSONField(default=dict, null=True),
        ),
        migrations.AddField(
            model_name='postmetrics',
            name='commentList_json',
            field=models.JSONField(default=dict, null=True),
        ),

        # Step 2: Convert data
        migrations.RunPython(convert_to_ab_format, reverse_ab_format),

        # Step 3: Remove old fields
        migrations.RemoveField(
            model_name='postmetrics',
            name='likes',
        ),
        migrations.RemoveField(
            model_name='postmetrics',
            name='retweets',
        ),
        migrations.RemoveField(
            model_name='postmetrics',
            name='impressions',
        ),
        migrations.RemoveField(
            model_name='postmetrics',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='postmetrics',
            name='tweet_id',
        ),
        migrations.RemoveField(
            model_name='postmetrics',
            name='commentList',
        ),

        # Step 4: Rename new fields to original names
        migrations.RenameField(
            model_name='postmetrics',
            old_name='likes_json',
            new_name='likes',
        ),
        migrations.RenameField(
            model_name='postmetrics',
            old_name='retweets_json',
            new_name='retweets',
        ),
        migrations.RenameField(
            model_name='postmetrics',
            old_name='impressions_json',
            new_name='impressions',
        ),
        migrations.RenameField(
            model_name='postmetrics',
            old_name='comments_json',
            new_name='comments',
        ),
        migrations.RenameField(
            model_name='postmetrics',
            old_name='tweet_id_json',
            new_name='tweet_id',
        ),
        migrations.RenameField(
            model_name='postmetrics',
            old_name='commentList_json',
            new_name='commentList',
        ),

        # Step 5: Set defaults and make non-nullable
        migrations.AlterField(
            model_name='postmetrics',
            name='likes',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='postmetrics',
            name='retweets',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='postmetrics',
            name='impressions',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='postmetrics',
            name='comments',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='postmetrics',
            name='tweet_id',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='postmetrics',
            name='commentList',
            field=models.JSONField(default=dict),
        ),
    ]
