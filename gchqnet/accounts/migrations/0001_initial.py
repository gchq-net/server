# Generated by Django 5.0.4 on 2024-05-07 21:48

import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.db.models.functions.text
import django.utils.timezone
import gchqnet.accounts.models.user
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='account name')),
                ('display_name', models.CharField(error_messages={'unique': 'Another player already has that display name'}, max_length=30, unique=True, verbose_name='display name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', gchqnet.accounts.models.user.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Database ID')),
                ('mac_address', models.CharField(help_text='IEEE 802 format, e.g 12-34-56-78-90-AB-CD', max_length=17, unique=True, validators=[django.core.validators.RegexValidator('^([0-9A-F]{2}[-]){5}([0-9A-F]{2})$', 'The MAC address does not appear to be in the correct format.')], verbose_name='MAC Address')),
                ('is_enabled', models.BooleanField(default=True, help_text='Is the badge enabled? i.e can it be used to capture locations?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badges', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(('email', ''), ('is_superuser', True), _negated=True), name='superuser_must_have_email', violation_error_message='Any user with superuser permissions must have an email address'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('display_name'), name='unique_display_name', violation_error_message='Another player already has that display name'),
        ),
    ]
