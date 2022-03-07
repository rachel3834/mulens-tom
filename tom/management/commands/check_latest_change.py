from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from tom.models import Target, PhotObs, TargetName, TargetList, Project
from sys import exit

class Command(BaseCommand):
    help = 'Check latest change to the database'

    def handle(self,*args, **options):

        latest_target = Target.objects.latest('last_modified_date')
        latest_targetname = TargetName.objects.get(target_id=latest_target.pk)
        latest_observation = PhotObs.objects.latest('last_modified_date')

        latest_target_list = TargetList.objects.latest('last_modified_date')

        project_list = Project.objects.all()
        for project in project_list:
            try:
                latest_obs = PhotObs.objects.filter(project_id=project.pk).latest('stop_obs')
                latest_targetnames = TargetName.objects.filter(target_id=latest_obs.target_id)
                print(project.name, latest_targetnames[0].name, latest_obs.start_obs, latest_obs.stop_obs)
            except PhotObs.DoesNotExist:
                print(project.name, ' No observations recorded')
