import boto3
import pprint



pp = pprint.PrettyPrinter(indent=2)

snsclient = boto3.client('sns')
ecsclient = boto3.client('ecs')
elbclient = boto3.client('elbv2')
ec2resource = boto3.resource('ec2')


def get_target_details(service_tg_arn):
    target_group_health = elbclient.describe_target_health(TargetGroupArn=service_tg_arn)
    #pp.pprint(target_group_health)
    target_summary=[]
    for target in target_group_health['TargetHealthDescriptions']:
        #pp.pprint(target)
        target_instance=ec2resource.Instance(target['Target']['Id'])
        target_port=target['Target']['Port']
        target_health=target['TargetHealth']['State']
        target_summary.append({'port': target_port, 'public_ip': target_instance.public_ip_address, 'private_ip': target_instance.private_ip_address, 'health': target_health})

    return target_summary


def main():

    env='ecsclustername'
    service_summary=[]

    l_services=ecsclient.list_services(cluster=env, maxResults=100)
    #pp.pprint(l_services)

    for service_arn in l_services['serviceArns']:
        d_services = ecsclient.describe_services(cluster=env, services=[service_arn])
        for service in d_services['services']:
            service_name=(service['serviceName'])
            #print(service_name)
            service_dcount=(service['desiredCount'])
            service_rcount=(service['runningCount'])
            try:
                service_tg_arn=(service['loadBalancers'][0]['targetGroupArn'])
            except:
                service_tg_arn='none'


            if service_tg_arn != 'none':
                target_summary=get_target_details(service_tg_arn)
                service_summary.append({'name':service_name, 'running_count':service_rcount, 'desired_count': service_dcount, 'target_summary': target_summary})
            else:
                service_summary.append({'name':service_name, 'running_count':service_rcount, 'desired_count': service_dcount, 'target_summary': 'no-targets'})

    pp.pprint(service_summary)



if __name__ == "__main__":
    main()
