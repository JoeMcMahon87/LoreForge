from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePageWidget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("widget_type", models.CharField(max_length=50)),
                ("order", models.PositiveIntegerField(default=0)),
                ("config", models.JSONField(default=dict)),
                (
                    "visibility",
                    models.CharField(
                        choices=[
                            ("gm_only", "GM only"),
                            ("player", "Player"),
                            ("public", "Public"),
                        ],
                        default="public",
                        max_length=10,
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
            },
        ),
    ]
