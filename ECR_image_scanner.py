import boto3
import json
import pprint
import time
import sys
import requests
import urllib3
import re



pp = pprint.PrettyPrinter(indent=2)

ecsclient = boto3.client('ecs')
ecrclient = boto3.client('ecr')

def get_running_service_images(env):
    running_service_images=[]
    l_services=ecsclient.list_services(cluster=env, maxResults=100)

    for service_arn in l_services['serviceArns']:
        d_services = ecsclient.describe_services(cluster=env, services=[service_arn])
        for service in d_services['services']:
            service_name=(service['serviceName'])
            service_rcount=(service['runningCount'])
            service_taskd=(service['taskDefinition'])
            if service_rcount > 0:

                td_description=ecsclient.describe_task_definition(taskDefinition=service_taskd)
                container_image=td_description['taskDefinition']['containerDefinitions'][0]['image']
                parse_container_image=re.split('/|:',container_image)
                container_repo=parse_container_image[1]
                image_tag=parse_container_image[2]

                running_service_images.append([service_name, container_image, container_repo, image_tag])

    return running_service_images


def main():

    env='stage'

    running_service_images=get_running_service_images(env)

    for image in running_service_images:
        service_name=image[0]
        container_image=image[1]
        container_repo=image[2]
        image_tag=image[3]

        try:
            start_scan=ecrclient.start_image_scan(repositoryName=container_repo, imageId={'imageTag': image_tag})
            print(f"Starting scan for {service_name} using ecr repo {container_repo} and tag {image_tag}")
        except:
            print(f"Failed to start scan for {service_name}. You can only do this once per day. Or you might need the newest version of boto3.")

    print('Wait for scan results a few minutes.')
    time.sleep(120)

    for image in running_service_images:
        service_name=image[0]
        container_image=image[1]
        container_repo=image[2]
        image_tag=image[3]

        image_scan_description=ecrclient.describe_image_scan_findings(repositoryName=container_repo, imageId={'imageTag': image_tag})

        print(f"scan for {service_name} is {image_scan_description['imageScanStatus']['status']}")
        print(f"Resulting Vunerability Count: {image_scan_description['imageScanFindings']['findingSeverityCounts']}")






if __name__ == "__main__":
    main()
