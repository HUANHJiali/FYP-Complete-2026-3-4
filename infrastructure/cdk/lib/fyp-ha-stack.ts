import {
  CfnOutput,
  Duration,
  RemovalPolicy,
  Stack,
  StackProps,
} from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export interface FypHaStackProps extends StackProps {
  backendImageUri: string;
  frontendImageUri: string;
  dbName: string;
}

export class FypHaStack extends Stack {
  constructor(scope: Construct, id: string, props: FypHaStackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'FypVpc', {
      maxAzs: 2,
      natGateways: 0,
      subnetConfiguration: [
        {
          name: 'public',
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
      ],
    });

    const albSecurityGroup = new ec2.SecurityGroup(this, 'AlbSecurityGroup', {
      vpc,
      allowAllOutbound: true,
      description: 'Security group for the public ALB',
    });
    albSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80), 'HTTP');
    albSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443), 'HTTPS');

    const frontendSecurityGroup = new ec2.SecurityGroup(this, 'FrontendSecurityGroup', {
      vpc,
      allowAllOutbound: true,
      description: 'Security group for frontend ECS tasks',
    });

    const backendSecurityGroup = new ec2.SecurityGroup(this, 'BackendSecurityGroup', {
      vpc,
      allowAllOutbound: true,
      description: 'Security group for backend ECS tasks',
    });

    const databaseSecurityGroup = new ec2.SecurityGroup(this, 'DatabaseSecurityGroup', {
      vpc,
      allowAllOutbound: true,
      description: 'Security group for MySQL database',
    });

    frontendSecurityGroup.addIngressRule(albSecurityGroup, ec2.Port.tcp(80), 'ALB to frontend');
    backendSecurityGroup.addIngressRule(albSecurityGroup, ec2.Port.tcp(8000), 'ALB to backend');
    databaseSecurityGroup.addIngressRule(backendSecurityGroup, ec2.Port.tcp(3306), 'Backend to MySQL');

    const dbSecret = new secretsmanager.Secret(this, 'DatabaseSecret', {
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ username: 'examuser' }),
        generateStringKey: 'password',
        excludePunctuation: true,
      },
    });

    const appSecret = new secretsmanager.Secret(this, 'DjangoSecretKey', {
      generateSecretString: {
        passwordLength: 64,
        excludePunctuation: true,
      },
    });

    const dbSubnetGroup = new rds.CfnDBSubnetGroup(this, 'DatabaseSubnetGroup', {
      dbSubnetGroupDescription: 'Subnets for FYP MySQL database',
      subnetIds: vpc.publicSubnets.map((subnet) => subnet.subnetId),
      dbSubnetGroupName: 'fyp-ha-db-subnet-group',
    });

    const dbInstance = new rds.CfnDBInstance(this, 'Database', {
      allocatedStorage: '20',
      dbInstanceClass: 'db.t3.micro',
      dbName: props.dbName,
      dbSubnetGroupName: dbSubnetGroup.ref,
      engine: 'mysql',
      engineVersion: '8.0.36',
      masterUsername: dbSecret.secretValueFromJson('username').unsafeUnwrap(),
      masterUserPassword: dbSecret.secretValueFromJson('password').unsafeUnwrap(),
      maxAllocatedStorage: 100,
      publiclyAccessible: true,
      storageEncrypted: true,
      storageType: 'gp3',
      vpcSecurityGroups: [databaseSecurityGroup.securityGroupId],
      deletionProtection: false,
      backupRetentionPeriod: 0,
    });
    dbInstance.applyRemovalPolicy(RemovalPolicy.DESTROY);
    dbSubnetGroup.applyRemovalPolicy(RemovalPolicy.DESTROY);

    const cluster = new ecs.Cluster(this, 'Cluster', {
      vpc,
      containerInsights: true,
    });

    const logGroup = new logs.LogGroup(this, 'AppLogs', {
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const backendTask = new ecs.FargateTaskDefinition(this, 'BackendTask', {
      cpu: 512,
      memoryLimitMiB: 1024,
    });

    const frontendTask = new ecs.FargateTaskDefinition(this, 'FrontendTask', {
      cpu: 256,
      memoryLimitMiB: 512,
    });

    const backendImage = props.backendImageUri
      ? ecs.ContainerImage.fromRegistry(props.backendImageUri)
      : ecs.ContainerImage.fromRegistry('public.ecr.aws/docker/library/python:3.11-slim');

    const frontendImage = props.frontendImageUri
      ? ecs.ContainerImage.fromRegistry(props.frontendImageUri)
      : ecs.ContainerImage.fromRegistry('public.ecr.aws/nginx/nginx:stable-alpine');

    const backendContainer = backendTask.addContainer('BackendContainer', {
      image: backendImage,
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'backend',
        logGroup,
      }),
      command: [
        'sh',
        '-c',
        [
          'python manage.py migrate --noinput',
          '(python manage.py init_data || true)',
          'python manage.py collectstatic --noinput',
          'gunicorn server.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 120 --access-logfile - --error-logfile -',
        ].join(' && '),
      ],
      environment: {
        DB_HOST: dbInstance.attrEndpointAddress,
        DB_PORT: dbInstance.attrEndpointPort,
        DB_NAME: props.dbName,
        DB_USER: 'examuser',
        DEBUG: 'False',
        ALLOWED_HOSTS: '*',
        CORS_ALLOWED_ORIGINS: '*',
        CSRF_TRUSTED_ORIGINS: 'http://localhost',
        CSRF_EXEMPT_PATH_PREFIXES: '/api/',
        ENABLE_RATE_LIMIT: 'True',
        RATELIMIT_ENABLE: 'True',
        TRUST_PROXY_HEADERS: 'True',
        PYTHONUNBUFFERED: '1',
      },
      secrets: {
        DB_PASSWORD: ecs.Secret.fromSecretsManager(dbSecret, 'password'),
        SECRET_KEY: ecs.Secret.fromSecretsManager(appSecret),
      },
    });
    backendContainer.addPortMappings({ containerPort: 8000 });

    const frontendContainer = frontendTask.addContainer('FrontendContainer', {
      image: frontendImage,
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'frontend',
        logGroup,
      }),
    });
    frontendContainer.addPortMappings({ containerPort: 80 });

    const backendService = new ecs.FargateService(this, 'BackendService', {
      cluster,
      taskDefinition: backendTask,
      desiredCount: 2,
      assignPublicIp: true,
      securityGroups: [backendSecurityGroup],
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      healthCheckGracePeriod: Duration.seconds(120),
    });

    const frontendService = new ecs.FargateService(this, 'FrontendService', {
      cluster,
      taskDefinition: frontendTask,
      desiredCount: 2,
      assignPublicIp: true,
      securityGroups: [frontendSecurityGroup],
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      healthCheckGracePeriod: Duration.seconds(60),
    });

    const loadBalancer = new elbv2.ApplicationLoadBalancer(this, 'LoadBalancer', {
      vpc,
      internetFacing: true,
      securityGroup: albSecurityGroup,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
    });

    const frontendTargetGroup = new elbv2.ApplicationTargetGroup(this, 'FrontendTargetGroup', {
      vpc,
      port: 80,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      healthCheck: {
        enabled: true,
        path: '/',
        healthyHttpCodes: '200,301,302,404',
        interval: Duration.seconds(30),
      },
    });

    const backendTargetGroup = new elbv2.ApplicationTargetGroup(this, 'BackendTargetGroup', {
      vpc,
      port: 8000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      healthCheck: {
        enabled: true,
        path: '/api/health/simple/',
        healthyHttpCodes: '200',
        interval: Duration.seconds(30),
        timeout: Duration.seconds(10),
      },
    });

    frontendService.attachToApplicationTargetGroup(frontendTargetGroup);
    backendService.attachToApplicationTargetGroup(backendTargetGroup);

    const listener = loadBalancer.addListener('HttpListener', {
      port: 80,
      open: true,
      defaultTargetGroups: [frontendTargetGroup],
    });

    listener.addTargetGroups('ApiRule', {
      priority: 100,
      conditions: [elbv2.ListenerCondition.pathPatterns(['/api/*'])],
      targetGroups: [backendTargetGroup],
    });

    new CfnOutput(this, 'LoadBalancerDns', {
      value: loadBalancer.loadBalancerDnsName,
      description: 'Public ALB DNS name',
    });

    new CfnOutput(this, 'FrontendUrl', {
      value: `http://${loadBalancer.loadBalancerDnsName}`,
      description: 'Frontend entry URL',
    });

    new CfnOutput(this, 'BackendApiUrl', {
      value: `http://${loadBalancer.loadBalancerDnsName}/api/`,
      description: 'Backend API URL',
    });

    new CfnOutput(this, 'DatabaseEndpoint', {
      value: dbInstance.attrEndpointAddress,
      description: 'RDS endpoint',
    });

    new CfnOutput(this, 'DatabaseSecretArn', {
      value: dbSecret.secretArn,
      description: 'Secrets Manager ARN containing database credentials',
    });
  }
}