from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from tom.models import Target, PhotObs, TargetName, TargetList, Project
from sys import exit
from os import path

class Command(BaseCommand):
    help = 'Export a summary of the TOM database holdings for a given project'

    def add_arguments(self, parser):
        parser.add_argument('project', nargs='+', type=str)
        parser.add_argument('output_dir', nargs='+', type=str)

    def concat_targetnames(self,targetnames):
        target = targetnames[0].name
        if len(targetnames) > 1:
            for name in targetnames[1:]:
                target += '/' + name.name
        return target

    def summarize_observation_exposures(self, observation, exposure_set):
        targetnames = TargetName.objects.filter(target_id=observation.target_id)
        target = self.concat_targetnames(targetnames)
        report = []
        for exp in exposure_set:
            entry = target+' '+\
                    observation.group_id+' '+\
                    observation.network+' '+\
                    observation.site+' '+\
                    observation.telescope+' '+\
                    observation.instrument+' '+\
                    exp.inst_filter+' '+\
                    str(exp.exp_time)+' '+\
                    str(exp.n_exp)+' '+\
                    str(exp.defocus)+' '+\
                    str(exp.binning)+' '+\
                    observation.track_id+' '+\
                    observation.start_obs.strftime("%Y-%m-%dT%H:%M:%S")+' '+\
                    observation.stop_obs.strftime("%Y-%m-%dT%H:%M:%S")+' '+\
                    str(observation.cadence)+' '+\
                    str(observation.jitter)+' '+\
                    str(observation.airmass_limit)+' '+\
                    str(observation.lunar_distance_limit)+' '+\
                    str(observation.ipp)+' '+\
                    repr(observation.rapid_mode)+' '+\
                    observation.group_type+' '+\
                    observation.obs_mode+' '+\
                    repr(observation.simulate)+' '+\
                    observation.status+' '+\
                    observation.information+'\n'
            report.append(entry)
        return report

    def handle(self,*args, **options):

        qs = Project.objects.filter(name=options['project'][0])

        if len(qs) == 0:
            print('No projects called '+options['project'][0]+' are known to the database')
        elif len(qs) > 1:
            print('Multiple projects called '+options['project'][0])
        else:
            project = qs[0]

            targetlistobj = TargetList.objects.get(project_id=project.pk)
            targetlist = targetlistobj.targets.all()

            ts_file = open(path.join(options['output_dir'][0],project.name+'_targetlist.dat'),'w')
            ts_file.write('# Target_name   RA       Dec\n')
            for target in targetlist:
                targetnames = TargetName.objects.filter(target_id=target.pk)
                name = self.concat_targetnames(targetnames)
                ts_file.write(name+' '+target.ra+' '+target.dec+'\n')
            ts_file.close()

            obslist = PhotObs.objects.filter(project_id=project.pk)
            obs_file = open(path.join(options['output_dir'][0],project.name+'_obslist.dat'),'w')
            obs_file.write('#  Target_name  Group_ID  Network  Site  Telescope  Instrument   Filter   Exp_time(s)  N_exp   Defocus   Binning    Track_ID   Start_obs  Stop_obs   Cadence(hrs)  Jitter(hrs)   Airmass_limit    Lunar_distance_limit(deg)   IPP   Rapid_mode    Group_type   Obs_mode   Status  Information \n')
            for observation in obslist:
                exposure_set = observation.exposures.all()
                report = self.summarize_observation_exposures(observation, exposure_set)
                for entry in report:
                    obs_file.write(entry)
            obs_file.close()
