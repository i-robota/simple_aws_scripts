import boto3
import json
import pprint
import time
from botocore.exceptions import ClientError


pp = pprint.PrettyPrinter(indent=2)

ec2client = boto3.client('ec2')
ec2 = boto3.resource('ec2')


def get_instance_tags(instance_id):
    instance=ec2.Instance(instance_id)

    instance_cost_cat='untagged'
    instance_name='untagged'
    for tag in instance.tags:
        if tag['Key'] == 'dev-ec2-cost':
            instance_cost_cat = tag['Value']
        if tag['Key'] == 'Name':
            instance_name = tag['Value']


    return instance_name,instance_cost_cat


def get_volume_details(volume_id):
    volume_details=[]
    try:
        vol_deets=ec2client.describe_volumes(VolumeIds=[volume_id])

        try:
            instance_id=vol_deets['Volumes'][0]['Attachments'][0]['InstanceId']
            vol_status ='vol-attached'
        except:
            instance_id='none'
            vol_status = 'vol-unattached'

    except ClientError as e:
        vol_status='vol-terminated'
        instance_id='none'

    return vol_status,instance_id


def get_untagged_volume_snapshots(exclude_key):
    paginator = ec2client.get_paginator('describe_snapshots')
    pages = paginator.paginate(Filters=[{'Name': 'owner-id', 'Values': ['773981645558']}])

    snapshot_list=[]
    for page in pages:
        print('New Page')
        for snapshot in page['Snapshots']:
            pp.pprint(snapshot)
            if 'Tags' in snapshot:
                 #print('tags')
                 #print(snapshot['Tags'])
                 if not any(exclude_key in tag['Key'] for tag in snapshot['Tags']):
                     snapshot_list.append(snapshot)
                     print('adding')
            else:
                snapshot_list.append(snapshot)
                print('adding')

    return snapshot_list


def main():

    exclude_key='backup'
    untagged_snapshot_list=get_untagged_volume_snapshots(exclude_key)


    for untagged_snapshot in untagged_snapshot_list:
        ebs_snapshot_resource = ec2.Snapshot(untagged_snapshot['SnapshotId'])
        volume_id=untagged_snapshot['VolumeId']

        volume_status,instance_id=get_volume_details(volume_id)

        print(volume_status)
        print(instance_id)

        if instance_id != 'none':
            instance_name,instance_cost_cat=get_instance_tags(instance_id)
            print(instance_name)
            snap_cost_cat=instance_cost_cat
        else:
            instance_name='no-instance'
            snap_cost_cat=volume_status

        print(untagged_snapshot['SnapshotId'])

        print(snap_cost_cat)

        create_tag = ebs_snapshot_resource.create_tags(Tags=[{'Key': 'dev-ebs-cost', 'Value': snap_cost_cat}, {'Key': 'dev-other-cost', 'Value': instance_name}])


if __name__ == "__main__":
    main()
