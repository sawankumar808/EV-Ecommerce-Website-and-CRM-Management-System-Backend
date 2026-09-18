from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                default="SALES",
                max_length=50
            ),
        ),

        migrations.CreateModel(
            name="CustomRole",
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

                (
                    "name",
                    models.CharField(
                        max_length=100
                    ),
                ),

                (
                    "code",
                    models.CharField(
                        max_length=50,
                        unique=True
                    ),
                ),

                (
                    "category",
                    models.CharField(
                        choices=[
                            (
                                "MANAGEMENT",
                                "Management"
                            ),
                            (
                                "ACCOUNTS",
                                "Accounts"
                            ),
                            (
                                "OTHER",
                                "Other"
                            ),
                        ],
                        default="OTHER",
                        max_length=20,
                    ),
                ),

                (
                    "permissions",
                    models.JSONField(
                        blank=True,
                        default=dict
                    ),
                ),

                (
                    "is_active",
                    models.BooleanField(
                        default=True
                    ),
                ),

                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True
                    ),
                ),

                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True
                    ),
                ),
            ],

            options={
                "ordering": ["name"],
            },
        ),
    ]