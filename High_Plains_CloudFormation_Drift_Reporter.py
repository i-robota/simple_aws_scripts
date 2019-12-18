import boto3
import json
import pprint
import time
import sys


#Setting sessions depends on how you want to run this - lambda vs local, etc
#boto3.setup_default_session(region_name="us-east-1")
#boto3.setup_default_session(profile_name="dev")

pp = pprint.PrettyPrinter(indent=2)

boto3.setup_default_session(region_name="us-east-1")
boto3.setup_default_session(profile_name="dev")

ecsclient = boto3.client('ecs')
cfnclient = boto3.client('cloudformation')
s3client = boto3.client('s3')




def driftreport(stack_name):

    print(f'Checking {stack_name}')
    dsd_response = cfnclient.detect_stack_drift(StackName=stack_name)
    sdd_id=dsd_response['StackDriftDetectionId']

    delay=60*10    #for 10 minutes max
    close_time=time.time()+delay

    while True:
        sdd_status_response=cfnclient.describe_stack_drift_detection_status(StackDriftDetectionId=sdd_id)
        sdd_status=sdd_status_response['DetectionStatus']
        #print(f'Detections status is {sdd_status}')
        if sdd_status == 'DETECTION_COMPLETE':
            break
        if time.time()>close_time:
            break
        time.sleep(5)
    resource_drift_resp=cfnclient.describe_stack_resource_drifts(StackName=stack_name,StackResourceDriftStatusFilters=['MODIFIED','DELETED'])
    #pp.pprint(response)
    for stack_resource in resource_drift_resp['StackResourceDrifts']:
        pp.pprint(f"Logical resource modified: {stack_resource['LogicalResourceId']}")
        pp.pprint(stack_resource['PropertyDifferences'])

def list_ecs_clusters():
    list_clusters = ecsclient.list_clusters()
    cluster_arns=(list_clusters['clusterArns'])
    cluster_list=[]
    for cluster in cluster_arns:
        print(cluster.rsplit('/', 1)[-1])
        cluster_list.append(cluster.rsplit('/', 1)[-1])

def main():

    environment=sys.argv[1]
    print(f'Running drift detection for {environment} stack and all nested stacks')
    paginator = cfnclient.get_paginator('list_stacks')
    list_stacks = paginator.paginate(StackStatusFilter=['CREATE_COMPLETE','UPDATE_COMPLETE','ROLLBACK_COMPLETE'])

    for page in list_stacks:
        for stack_summary in page['StackSummaries']:
            #print(stack_summary['StackName'])
            stack_name=stack_summary['StackName']
            if stack_name.startswith(environment):
                #print(stack_name)
                driftreport(stack_name)
        


if __name__ == "__main__":
    main()
