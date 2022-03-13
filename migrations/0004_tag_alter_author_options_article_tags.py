# Generated by Django 4.0.3 on 2022-03-13 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flaxarticles', '0003_alter_documentanchor_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the tag', max_length=75, verbose_name='name')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AlterModelOptions(
            name='author',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(help_text='The tags to which the article belongs', to='flaxarticles.tag'),
        ),
    ]
