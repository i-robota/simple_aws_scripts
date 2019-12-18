##Simple AWS Scripts

Just a few little automation things w/ boto.

###Cost_Allocation_Tagger_Snapshots

Goes through EBS volume snapshots and associates them with an EBS volume and EC2 Instance - if possible. Pulls back Instance tags and puts a cost category on the EBS Vol Snapshot

###ECR_Image_Scanner

Uses new Image Scan functionality of Elastic Container Repository. Queries ECS cluster to see what services are running - checks Task Definitions for container repo / tag. Scans all container images and reports high level findings

###ECS_Servcie_Location_Harvester

Queries ECS cluster for running services - finds Target groups and queries out individual targets for port, IP, running counts and health. 

###High_Plains_Cloudformation_Drift_Reporter

If you use lots of nested stacks - drift detection for CFn is annoying to read. This queries a stack for all nested stacks and runs drift detection on all and gives a summary report.  Useful before tearing down stacks to make sure manual changes have not been committed to CloudFormation.
