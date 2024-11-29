#!/usr/bin/env python3

import os
import time
import random
import string
import logging
import click
from kubernetes import client, watch
from kubernetes.client.models.v1_node_selector_requirement import V1NodeSelectorRequirement
from kubernetes.client.models.v1_node_selector_term import V1NodeSelectorTerm


logger = logging.getLogger(__name__)


def load_kube_config():
    print("start loading Kube configuration file.")
    with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as token_file:
        token = token_file.read()
    ""
    host = "https://%s:%s" % (
        os.environ.get("KUBERNETES_SERVICE_HOST", "127.0.0.1"),
        os.environ.get("KUBERNETES_SERVICE_PORT", "443"),
    )
    config = client.Configuration(host=host)
    config.api_key = {"authorization": "Bearer " + token}
    config.verify_ssl = True
    if config.verify_ssl:
        config.ssl_ca_cert = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    client.Configuration.set_default(config)


def refresh_daemonset(namespace, daemonset_name):
    apps_v1_api = client.AppsV1Api()
    core_v1_api = client.CoreV1Api()
    daemonset = apps_v1_api.read_namespaced_daemon_set(daemonset_name, namespace)
    kwargs = {
        "namespace": namespace,
        "label_selector": ",".join(
            [f"{key}!={value}" for key, value in daemonset.spec.selector.match_labels.items()]
        ),
    }
    new_node_names = list({
        item.spec.node_name for item in core_v1_api.list_namespaced_pod(**kwargs).items
    })
    print(f"refresh daemonset in namespace {namespace}, node_names: {new_node_names}.")
    node_selector_terms = daemonset.spec.template.spec.affinity.node_affinity.\
        required_during_scheduling_ignored_during_execution.\
            node_selector_terms
    old_node_names = node_selector_terms[0].match_expressions[0].values
    old_node_names.sort()
    new_node_names.sort()
    if len(new_node_names) == 0 or old_node_names != new_node_names:
        node_selector_terms.clear()
        if len(new_node_names) == 0:
            new_node_names.append(''.join(
                random.choices(string.ascii_uppercase + string.digits, k=32)
            ))
        node_selector_terms.append(V1NodeSelectorTerm(match_expressions=[
            V1NodeSelectorRequirement(
                key="kubernetes.io/hostname",
                operator="In",
                values=new_node_names,
            )
        ]))
        apps_v1_api.patch_namespaced_daemon_set(daemonset_name, namespace, body=daemonset)
    else:
        print(f"no changes node_names: {new_node_names}.")


@click.command()
@click.option("--namespace", "namespace", required=True, help="k8s namespace.")
@click.option("--daemonset-name", "daemonset_name", required=True, help="k8s daemonset name.")
@click.option("--retry-interval", "retry_interval", show_default=True, default=60, type=int, help="k8s watch retry interval.")
@click.option("--refresh-interval", "refresh_interval", show_default=True, default=1200, type=int, help="k8s max refresh interval.")
def main(namespace, daemonset_name, retry_interval, refresh_interval):
    load_kube_config()
    core_v1_api = client.CoreV1Api()
    apps_v1_api = client.AppsV1Api()
    daemonset = apps_v1_api.read_namespaced_daemon_set(daemonset_name, namespace)
    kwargs = {
        "namespace": namespace,
        "watch": True,
        "timeout_seconds": retry_interval,
        "label_selector": ",".join(
            [f"{key}!={value}" for key, value in daemonset.spec.selector.match_labels.items()]
        ),
    }
    timestamp = 0
    while True:
        w = watch.Watch()
        try:
            if int(time.time() - timestamp) > refresh_interval:
                refresh_daemonset(namespace, daemonset_name)
                timestamp = int(time.time())
            for event in w.stream(core_v1_api.list_namespaced_pod, **kwargs):
                node_name = event['object'].spec.node_name
                if node_name:
                    if event['type'] in ("ADDED", "MODIFIED", "DELETED"):
                        timestamp = 0
        except Exception as ex:
            logger.exception(ex)
            w.stop()


if __name__ == "__main__":
    main()
