#!/usr/bin/env python3

import click
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import sys
import googleapiclient.discovery


def apply_job_filter(job, filters):
    for filter in filters:
        if filter in job['name']:
            return True
    return False


def wait_for_operation(compute, project, zone, operation):
    click.echo('Waiting for resize operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            click.echo("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)


def resize_if_needed(compute, project_id, gce_zone,
                     gce_instance_group_name, desired_slots, slots_per_instance):
    result = compute.instanceGroupManagers().get(
        project=project_id, zone=gce_zone, instanceGroupManager=gce_instance_group_name).execute()

    targetSize = result['targetSize']
    click.echo('current group size={}'.format(result['targetSize']))

    scale_to = None
    if desired_slots // slots_per_instance > targetSize:
        scale_to = desired_slots // slots_per_instance
        click.echo(
            'Target size is less than desired_slots // slots_per_instance, scaling up to {}'.format(scale_to))
    elif desired_slots == 0 and targetSize > 0:
        scale_to = 0
        click.echo('Desired slots is 0, scaling to 0')

    if scale_to is not None:
        result = compute.instanceGroupManagers().resize(size=scale_to,
                                                        project=project_id,
                                                        zone=gce_zone,
                                                        instanceGroupManager=gce_instance_group_name).execute()
        wait_for_operation(compute, project_id, gce_zone, result['name'])


def requests_retry_session(retries=5, backoff_factor=0.5, status_forcelist=(429, 500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


@click.command()
@click.option('--project-id', default="my-project", help='GCE project ID')
@click.option('--gce-zone', default="us-central1-a", help='GCE zone')
@click.option('--gce-instance-group-name', required=True, help="Name of GCE instance group")
@click.option('--job-filter', default="", help='Filter job names by this comma separated list of keywords')
@click.option('--interval', default=30, help='Interval (in seconds) to poll GitLab API')
@click.option('--gitlab-project-ids', required=True, help="Comma separate list of GitLab projects IDs to poll for jobs")
@click.option('--gitlab-personal-token', required=True, help="GitLab API token")
@click.option('--slots-per-instance', default=1, help='Target number of slots per instance')
def main(project_id, gce_zone, gce_instance_group_name, job_filter, interval, gitlab_project_ids, gitlab_personal_token, slots_per_instance):
    compute = googleapiclient.discovery.build('compute', 'v1')

    gl_url = 'https://gitlab.com/api/v4/projects'
    gl_headers = {'Private-Token': gitlab_personal_token}

    gl_projects = gitlab_project_ids.split(',')
    gl_job_filter = job_filter.split(',')

    while True:
        try:
            for gl_project_id in gl_projects:
                click.echo(
                    'Fetching GitLab jobs for gl_project_id={}'.format(gl_project_id))
                jobs_len = 100
                page = 1
                jobs = []
                while jobs_len == 100:
                    r = requests_retry_session().get(
                        gl_url + '/{}/jobs'.format(gl_project_id),
                        headers=gl_headers,
                        params={'per_page': '100', 'page': page, 'scope[]': ['created', 'running', 'pending']})

                    r.raise_for_status()
                    job_result = r.json()
                    jobs_len = len(job_result)
                    jobs.extend(job_result)
                    page += 1

                running_jobs = list(
                    filter(lambda job: job['status'] == 'running' and apply_job_filter(job, gl_job_filter), jobs))
                pending_jobs = list(
                    filter(lambda job: job['status'] == 'pending' and apply_job_filter(job, gl_job_filter), jobs))
                created_jobs = list(
                    filter(lambda job: job['status'] == 'created' and apply_job_filter(job, gl_job_filter), jobs))

                click.echo('Job queue lengths: created={}, pending={}, running={}'.format(
                    len(created_jobs),
                    len(pending_jobs),
                    len(running_jobs),
                ))

                desired_slots = sum([len(running_jobs), len(pending_jobs)])
                if desired_slots == 0 and len(created_jobs) > 0:
                    desired_slots = slots_per_instance

                click.echo('desired_slots={}'.format(desired_slots))

                resize_if_needed(compute, project_id, gce_zone,
                                 gce_instance_group_name, desired_slots, slots_per_instance)
        except requests.exceptions.RequestException as e:
            click.echo(
                'Caught an exception: {}'.format(e))

        time.sleep(interval)


if __name__ == '__main__':
    main()
