#!/usr/bin/env bash
# One-time AWS setup for Tap Genius, mirroring the girl_game / Island Night stack:
#   EC2 (AL2023, Node, systemd) + Elastic IP + CloudFront (HTTPS/WebSockets) + SSM + GitHub-OIDC deploy role.
# Needs admin AWS credentials. Idempotency is NOT guaranteed - run once, read the output.
set -euo pipefail
R=us-west-1; N=tap-genius
ACCT=$(aws sts get-caller-identity --query Account --output text)
REPO_SUB='repo:aalkouri@40836919/tap_genius@1458175110'   # ID-based OIDC subject format

# --- IAM: instance role (SSM only) ---
aws iam create-role --role-name $N-ssm --assume-role-policy-document \
 '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null
aws iam attach-role-policy --role-name $N-ssm --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
aws iam create-instance-profile --instance-profile-name $N-ssm >/dev/null
aws iam add-role-to-instance-profile --instance-profile-name $N-ssm --role-name $N-ssm
sleep 10

# --- Network: SG only reachable from CloudFront ---
VPC=$(aws ec2 describe-vpcs --region $R --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)
SG=$(aws ec2 create-security-group --region $R --group-name $N-web --description "Tap Genius web (CloudFront only)" --vpc-id "$VPC" --query GroupId --output text)
PL=$(aws ec2 describe-managed-prefix-lists --region $R --filters Name=prefix-list-name,Values=com.amazonaws.global.cloudfront.origin-facing --query 'PrefixLists[0].PrefixListId' --output text)
aws ec2 authorize-security-group-ingress --region $R --group-id "$SG" \
  --ip-permissions "IpProtocol=tcp,FromPort=80,ToPort=80,PrefixListIds=[{PrefixListId=$PL,Description=CloudFront origin-facing}]" >/dev/null

# --- EC2 ---
AMI=$(aws ssm get-parameter --region $R --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)
cat > /tmp/tg-userdata.sh <<'UD'
#!/bin/bash
dnf install -y nodejs20 || dnf install -y nodejs
mkdir -p /opt/game
cat > /etc/systemd/system/game.service <<'U'
[Unit]
Description=Tap Genius
After=network.target
[Service]
WorkingDirectory=/opt/game
Environment=PORT=80
ExecStart=/usr/bin/node server.js
Restart=always
[Install]
WantedBy=multi-user.target
U
systemctl daemon-reload && systemctl enable game
UD
IID=$(aws ec2 run-instances --region $R --image-id "$AMI" --instance-type t3.micro \
  --iam-instance-profile Name=$N-ssm --security-group-ids "$SG" --user-data file:///tmp/tg-userdata.sh \
  --metadata-options HttpTokens=required \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$N}]" --query 'Instances[0].InstanceId' --output text)
aws ec2 wait instance-running --region $R --instance-ids "$IID"
ALLOC=$(aws ec2 allocate-address --region $R --domain vpc --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=Name,Value=$N}]" --query AllocationId --output text)
aws ec2 associate-address --region $R --instance-id "$IID" --allocation-id "$ALLOC" >/dev/null
IP=$(aws ec2 describe-addresses --region $R --allocation-ids "$ALLOC" --query 'Addresses[0].PublicIp' --output text)
ORIGIN="ec2-${IP//./-}.$R.compute.amazonaws.com"

# --- CloudFront: HTTPS + WebSockets, no caching ---
cat > /tmp/tg-cf.json <<CF
{"CallerReference":"$N-$(date +%s)","Comment":"$N","Enabled":true,"HttpVersion":"http2and3",
 "Origins":{"Quantity":1,"Items":[{"Id":"ec2","DomainName":"$ORIGIN",
   "CustomOriginConfig":{"HTTPPort":80,"HTTPSPort":443,"OriginProtocolPolicy":"http-only","OriginReadTimeout":60}}]},
 "DefaultCacheBehavior":{"TargetOriginId":"ec2","ViewerProtocolPolicy":"redirect-to-https",
   "AllowedMethods":{"Quantity":7,"Items":["GET","HEAD","OPTIONS","PUT","POST","PATCH","DELETE"]},
   "CachePolicyId":"4135ea2d-6df8-44a3-9df3-4b5a84be39ad","OriginRequestPolicyId":"b689b0a8-53d0-40ab-baf2-68738e2966ac","Compress":true}}
CF
CF_DOMAIN=$(aws cloudfront create-distribution --distribution-config file:///tmp/tg-cf.json --query Distribution.DomainName --output text)

# --- GitHub OIDC deploy role (provider already exists from girl_game) ---
aws iam create-role --role-name $N-github-deploy --assume-role-policy-document "{
 \"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",
 \"Principal\":{\"Federated\":\"arn:aws:iam::$ACCT:oidc-provider/token.actions.githubusercontent.com\"},
 \"Action\":\"sts:AssumeRoleWithWebIdentity\",
 \"Condition\":{\"StringEquals\":{\"token.actions.githubusercontent.com:aud\":\"sts.amazonaws.com\"},
  \"StringLike\":{\"token.actions.githubusercontent.com:sub\":[\"$REPO_SUB:ref:refs/heads/main\",\"$REPO_SUB:ref:refs/heads/claude/*\"]}}}]}" >/dev/null
aws iam put-role-policy --role-name $N-github-deploy --policy-name deploy-via-ssm --policy-document "{
 \"Version\":\"2012-10-17\",\"Statement\":[
 {\"Effect\":\"Allow\",\"Action\":\"ssm:SendCommand\",\"Resource\":[\"arn:aws:ec2:$R:$ACCT:instance/$IID\",\"arn:aws:ssm:$R::document/AWS-RunShellScript\"]},
 {\"Effect\":\"Allow\",\"Action\":[\"ssm:GetCommandInvocation\",\"ssm:ListCommandInvocations\"],\"Resource\":\"*\"}]}"

sed -i "s/i-REPLACE_ME/$IID/" "$(dirname "$0")/../.github/workflows/deploy.yml"
echo "Instance: $IID  EIP: $IP  Site: https://$CF_DOMAIN (CloudFront takes ~5 min to deploy)"
echo "Now commit the updated workflow and push to main / claude/* to deploy the app."
