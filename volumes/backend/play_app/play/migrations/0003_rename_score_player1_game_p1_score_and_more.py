# Generated by Django 4.2.16 on 2024-10-02 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('play', '0002_remove_game_winner_game_game_round_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='score_player1',
            new_name='p1_score',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='score_player2',
            new_name='p2_score',
        ),
        migrations.RemoveField(
            model_name='game',
            name='player1',
        ),
        migrations.RemoveField(
            model_name='game',
            name='player2',
        ),
        migrations.AddField(
            model_name='game',
            name='p1_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='p1_name',
            field=models.CharField(default='Player1', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='p2_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='p2_name',
            field=models.CharField(default='Player2', max_length=16),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='game',
            name='game_round',
            field=models.CharField(choices=[('single', 'single'), ('semifinal1', 'Semi-Final 1'), ('semifinal2', 'Semi-Final 2'), ('final', 'Final')], default='single', max_length=16),
        ),
        migrations.AlterField(
            model_name='game',
            name='game_type',
            field=models.CharField(choices=[('pong', 'Pong')], max_length=16),
        ),
        migrations.DeleteModel(
            name='Player',
        ),
    ]
