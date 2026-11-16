#!/usr/bin/env bash
# Record of the one-time AWS setup for Tap Genius (tap.alkouri.com). It SHARES the girl_game EC2 instance:
#   girl_game  -> :80   (systemd "game",        /opt/game)        -> CloudFront -> island.alkouri.com
#   tap genius -> :8081 (systemd "tap-genius",  /opt/tap-genius)  -> CloudFront -> tap.alkouri.com
# Needs admin AWS credentials. Already applied; kept for reproducibility. Steps 4-5 need DNS records at your DNS provider.
set -euo pipefail
R=us-west-1; IID=i-00966cc1ee771d0cc; VPC=vpc-03351a3947a37dd12
ACCT=$(aws sts get-caller-identity --query Account --output text)

# 1. Security group: 8081 from CloudFront only (separate SG - the island-night-web SG is at its rule limit)
SG=$(aws ec2 create-security-group --region $R --group-name tap-genius-web --description "Tap Genius 8081 from CloudFront only" --vpc-id $VPC --query GroupId --output text)
PL=$(aws ec2 describe-managed-prefix-lists --region $R --filters Name=prefix-list-name,Values=com.amazonaws.global.cloudfront.origin-facing --query 'PrefixLists[0].PrefixListId' --output text)
aws ec2 authorize-security-group-ingress --region $R --group-id "$SG" --ip-permissions "IpProtocol=tcp,FromPort=8081,ToPort=8081,PrefixListIds=[{PrefixListId=$PL}]"
CUR=$(aws ec2 describe-instances --region $R --instance-ids $IID --query 'Reservations[0].Instances[0].SecurityGroups[].GroupId' --output text)
aws ec2 modify-instance-attribute --region $R --instance-id $IID --groups $CUR $SG

# 2. systemd service (run on the instance via SSM)
aws ssm send-command --region $R --instance-ids $IID --document-name AWS-RunShellScript --parameters 'commands=[
 "mkdir -p /opt/tap-genius",
 "printf \"[Unit]\\nDescription=Tap Genius\\nAfter=network.target\\n[Service]\\nWorkingDirectory=/opt/tap-genius\\nEnvironment=PORT=8081\\nExecStart=/usr/bin/node server.js\\nRestart=always\\n[Install]\\nWantedBy=multi-user.target\\n\" > /etc/systemd/system/tap-genius.service",
 "systemctl daemon-reload && systemctl enable tap-genius"]'

# 3. OIDC deploy role "tap-genius-github-deploy": trust repo:aalkouri@40836919/tap_genius@1458175110 (main, claude/*),
#    policy = ssm:SendCommand on this instance + AWS-RunShellScript, ssm:GetCommandInvocation/ListCommandInvocations.

# 4. ACM cert (must be us-east-1 for CloudFront) -> add the printed validation CNAME at your DNS provider
CERT=$(aws acm request-certificate --region us-east-1 --domain-name tap.alkouri.com --validation-method DNS --query CertificateArn --output text)
aws acm describe-certificate --region us-east-1 --certificate-arn "$CERT" --query 'Certificate.DomainValidationOptions[0].ResourceRecord'
aws acm wait certificate-validated --region us-east-1 --certificate-arn "$CERT"

# 5. CloudFront: alias tap.alkouri.com, origin = instance DNS on port 8081, no caching, WebSockets work by default.
IP=$(aws ec2 describe-instances --region $R --instance-ids $IID --query 'Reservations[0].Instances[0].PublicDnsName' --output text)
cat > /tmp/tg-cf.json <<CF
{"CallerReference":"tap-genius-$(date +%s)","Comment":"tap genius","Enabled":true,"HttpVersion":"http2and3",
 "Aliases":{"Quantity":1,"Items":["tap.alkouri.com"]},
 "ViewerCertificate":{"ACMCertificateArn":"$CERT","SSLSupportMethod":"sni-only","MinimumProtocolVersion":"TLSv1.2_2021"},
 "Origins":{"Quantity":1,"Items":[{"Id":"ec2","DomainName":"$IP",
   "CustomOriginConfig":{"HTTPPort":8081,"HTTPSPort":443,"OriginProtocolPolicy":"http-only","OriginReadTimeout":60}}]},
 "DefaultCacheBehavior":{"TargetOriginId":"ec2","ViewerProtocolPolicy":"redirect-to-https",
   "AllowedMethods":{"Quantity":7,"Items":["GET","HEAD","OPTIONS","PUT","POST","PATCH","DELETE"]},
   "CachePolicyId":"4135ea2d-6df8-44a3-9df3-4b5a84be39ad","OriginRequestPolicyId":"b689b0a8-53d0-40ab-baf2-68738e2966ac","Compress":true}}
CF
aws cloudfront create-distribution --distribution-config file:///tmp/tg-cf.json --query Distribution.DomainName --output text
# Then add CNAME: tap.alkouri.com -> <that cloudfront domain>

# 6. Activity log bucket (private) + permission for the instance to write to it. deploy/ship-logs.sh uploads there hourly.
B=tap-genius-logs-$ACCT
aws s3api create-bucket --bucket "$B" --region $R --create-bucket-configuration LocationConstraint=$R
aws s3api put-public-access-block --bucket "$B" --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
PROFILE=$(aws ec2 describe-instances --region $R --instance-ids $IID --query 'Reservations[0].Instances[0].IamInstanceProfile.Arn' --output text | sed 's|.*/||')
ROLE=$(aws iam get-instance-profile --instance-profile-name "$PROFILE" --query 'InstanceProfile.Roles[0].RoleName' --output text)
aws iam put-role-policy --role-name "$ROLE" --policy-name tap-genius-log-upload --policy-document \
  "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"s3:PutObject\",\"Resource\":\"arn:aws:s3:::$B/events/*\"}]}"
