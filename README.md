[![Build Status](https://travis-ci.org/brndnmtthws/gitlab-gce-autoscaler.svg?branch=master)](https://travis-ci.org/brndnmtthws/gitlab-gce-autoscaler) [![PyPI version](https://badge.fury.io/py/gitlab-gce-autoscaler.svg)](https://badge.fury.io/py/gitlab-gce-autoscaler)

# GitLab GCE Autoscaler

A very simple autoscaler for GitLab CI on GCE

## Features

- watches a GitLab pipeline for queued jobs
- scales a GCE instance group to meet demand

That's it 😄

## Synopsis

```ShellSession
$ gitlab-gce-autoscaler --help
Usage: gitlab-gce-autoscaler [OPTIONS]

Options:
  --project-id TEXT               GCE project ID
  --gce-zone TEXT                 GCE zone
  --gce-instance-group-name TEXT  Name of GCE instance group  [required]
  --job-filter TEXT               Filter job names by this comma separated
                                  list of keywords
  --interval INTEGER              Interval (in seconds) to poll GitLab API
  --gitlab-project-ids TEXT       Comma separate list of GitLab projects IDs
                                  to poll for jobs  [required]
  --gitlab-personal-token TEXT    GitLab API token  [required]
  --slots-per-instance INTEGER    Target number of slots per instance
  --help                          Show this message and exit.
```

## Helm Chart

There's a Helm chart included in the repo. To use it, you'll need to create a service account on GCE with the following permissions:

- `compute.instanceGroupManagers.get`
- `compute.instanceGroupManagers.update`

Then, create a secret with the service account credentials:

```ShellSession
$ kubectl create secret generic gitlab-gce-autoscaler --from-file=service-account-creds.json=service-account.json
secret/gitlab-gce-autoscaler created
```

Now install the chart:

```ShellSession
$ helm upgrade --install gitlab-gce-autoscaler helm/gitlab-gce-autoscaler -f myvalues.yaml
```
