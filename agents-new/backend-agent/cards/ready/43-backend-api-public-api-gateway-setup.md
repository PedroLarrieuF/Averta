---
id: 43
title: "API Public: AWS API Gateway Setup (CDK)"
priority: critical
type: feature
agent: backend
sprint: 1
estimate: L
status: ready
created: 2026-11-04
reviewed_by: techlead
---

# Card 43: API Public - AWS API Gateway Setup (CDK)

## Contexto
Provisionar AWS API Gateway (REST API) via CDK com: stages (sandbox/prod), Lambda Authorizer, Usage Plans, Custom Domain, WAF, Request/Response Transform (VTL), Logging.

## Arquitetura CDK

```
infrastructure/
├── lib/
│   ├── stacks/
│   │   ├── api-gateway-stack.ts      # Main stack
│   │   ├── authorizer-stack.ts       # Lambda Authorizer
│   │   ├── usage-plans-stack.ts      # Usage Plans per tier
│   │   └── domain-stack.ts           # Custom Domain + ACM
│   └── constructs/
│       ├── api-resource.ts           # Resource factory
│       └── vtl-templates.ts          # VTL mappings
└── bin/
    └── deploy.ts
```

## Tasks

### 1. Main API Gateway Stack (`lib/stacks/api-gateway-stack.ts`)
```typescript
import * as cdk from 'aws-cdk-lib';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export class ApiGatewayStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: {
    authorizerFn: lambda.IFunction;
    backendUrl: string;  // VPC Link / HTTP endpoint
    domainName?: string;
  }) {
    super(scope, id, props);

    // REST API
    const api = new apigateway.RestApi(this, 'AvertaPublicApi', {
      restApiName: 'AvertaSaaS Public API',
      description: 'Public API for freight audit integration',
      endpointConfiguration: { types: [apigateway.EndpointType.REGIONAL] },
      defaultCorsPreflightOptions: {
        allowOrigins: ['*'],
        allowMethods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
        allowHeaders: ['Content-Type', 'Authorization', 'X-API-Key', 'Idempotency-Key'],
        maxAge: cdk.Duration.hours(1)
      },
      deployOptions: {
        stageName: 'prod',
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true,
        tracingEnabled: true
      }
    });

    // Lambda Authorizer
    const authorizer = new apigateway.TokenAuthorizer(this, 'ApiKeyAuthorizer', {
      handler: props.authorizerFn,
      authorizerName: 'AvertaApiKeyAuthorizer',
      identitySource: 'method.request.header.Authorization',
      resultsCacheTtl: cdk.Duration.minutes(5)
    });

    // Custom Domain (if provided)
    if (props.domainName) {
      // ACM Certificate validation handled in DomainStack
      const domain = new apigateway.DomainName(this, 'ApiDomain', {
        domainName: props.domainName,
        certificate: // from DomainStack
        endpointType: apigateway.EndpointType.REGIONAL,
        securityPolicy: apigateway.SecurityPolicy.TLS_1_2
      });
      domain.addBasePathMapping(api);
    }

    // Resources & Methods (from OpenAPI spec)
    this.createApiResources(api, authorizer, props.backendUrl);

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', { value: api.url });
    new cdk.CfnOutput(this, 'ApiId', { value: api.restApiId });
  }

  private createApiResources(api: apigateway.RestApi, authorizer: apigateway.TokenAuthorizer, backendUrl: string) {
    const v1 = api.root.addResource('v1');

    // Discrepancies
    const discrepancies = v1.addResource('discrepancies');
    discrepancies.addMethod('GET', this.createIntegration(backendUrl, '/discrepancies'), { authorizer });
    discrepancies.addMethod('POST', this.createIntegration(backendUrl, '/discrepancies'), { authorizer });
    const discrepancyId = discrepancies.addResource('{id}');
    discrepancyId.addMethod('GET', this.createIntegration(backendUrl, '/discrepancies/{id}'), { authorizer });
    const bulk = discrepancies.addResource('bulk');
    bulk.addMethod('PATCH', this.createIntegration(backendUrl, '/discrepancies/bulk'), { authorizer });
    const review = discrepancyId.addResource('review');
    review.addMethod('POST', this.createIntegration(backendUrl, '/discrepancies/{id}/review'), { authorizer });

    // Documents
    const documents = v1.addResource('documents');
    documents.addMethod('GET', this.createIntegration(backendUrl, '/documents'), { authorizer });
    const upload = documents.addResource('upload');
    upload.addMethod('POST', this.createIntegration(backendUrl, '/documents/upload'), { authorizer });
    const docId = documents.addResource('{id}');
    docId.addMethod('GET', this.createIntegration(backendUrl, '/documents/{id}'), { authorizer });
    docId.addResource('reprocess').addMethod('POST', this.createIntegration(backendUrl, '/documents/{id}/reprocess'), { authorizer });
    docId.addResource('download').addMethod('GET', this.createIntegration(backendUrl, '/documents/{id}/download'), { authorizer });

    // Contests, Reports, Settings, Webhooks - similar pattern
    // ...

    // Health check (no auth)
    v1.addResource('health').addMethod('GET', this.createIntegration(backendUrl, '/health'));
  }

  private createIntegration(backendUrl: string, path: string) {
    return new apigateway.HttpIntegration(`${backendUrl}${path}`, {
      httpMethod: 'ANY',
      options: {
        requestParameters: {
          'integration.request.header.X-Forwarded-For': 'context.identity.sourceIp',
          'integration.request.header.X-API-Key-ID': 'context.authorizer.api_key_id',
          'integration.request.header.X-Company-ID': 'context.authorizer.company_id',
          'integration.request.header.X-Tier': 'context.authorizer.tier',
          'integration.request.header.X-Scopes': 'context.authorizer.scopes'
        },
        integrationResponses: [
          { statusCode: '200', responseTemplates: { 'application/json': '' } },
          { statusCode: '400', selectionPattern: '4\\d{2}', responseTemplates: { 'application/json': '$input.json("$")' } },
          { statusCode: '401', selectionPattern: '401', responseTemplates: { 'application/json': '{"error": "Unauthorized"}' } },
          { statusCode: '403', selectionPattern: '403', responseTemplates: { 'application/json': '{"error": "Forbidden"}' } },
          { statusCode: '429', selectionPattern: '429', responseTemplates: { 'application/json': '{"error": "Rate Limited"}' } },
          { statusCode: '500', selectionPattern: '5\\d{2}', responseTemplates: { 'application/json': '{"error": "Internal Server Error"}' }
        ],
        passthroughBehavior: apigateway.PassthroughBehavior.WHEN_NO_TEMPLATES
      }
    });
  }
}
```

### 2. Usage Plans Stack (`lib/stacks/usage-plans-stack.ts`)
```typescript
export class UsagePlansStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: { api: apigateway.RestApi }) {
    super(scope, id, props);

    const api = props.api;

    // Free Tier
    const freePlan = new apigateway.UsagePlan(this, 'FreeTierPlan', {
      name: 'Free Tier',
      description: 'Sandbox only, 100 req/min',
      apiStages: [{ api, stage: api.deploymentStage }],
      throttle: { rateLimit: 100, burstLimit: 200 },
      quota: { limit: 10000, period: apigateway.Period.DAY }
    });

    // Pro Tier
    const proPlan = new apigateway.UsagePlan(this, 'ProTierPlan', {
      name: 'Pro Tier',
      description: 'Production access, 1000 req/min',
      apiStages: [{ api, stage: api.deploymentStage }],
      throttle: { rateLimit: 1000, burstLimit: 2000 },
      quota: { limit: 100000, period: apigateway.Period.DAY }
    });

    // Enterprise Tier
    const entPlan = new apigateway.UsagePlan(this, 'EnterpriseTierPlan', {
      name: 'Enterprise Tier',
      description: 'High volume, 10000 req/min',
      apiStages: [{ api, stage: api.deploymentStage }],
      throttle: { rateLimit: 10000, burstLimit: 20000 },
      quota: { limit: 1000000, period: apigateway.Period.DAY }
    });

    // Associate API Keys to plans via authorizer context (usageIdentifierKey)
    // Done automatically when authorizer returns usageIdentifierKey
  }
}
```

### 3. Sandbox Stage
```typescript
// Separate stage for sandbox with mock integration
const sandboxStage = new apigateway.Stage(this, 'SandboxStage', {
  deployment: api.deploymentStage.deployment,
  stageName: 'sandbox',
  variables: { 'backendUrl': 'https://sandbox-api.averta.com' }
});

// Mock integration for sandbox (returns static examples)
const mockIntegration = new apigateway.MockIntegration({
  integrationResponses: [{ statusCode: '200', responseTemplates: { 'application/json': sandboxMockResponse } }],
  requestTemplates: { 'application/json': '{ "statusCode": 200 }' }
});
```

### 4. WAF Integration
```typescript
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';

const webAcl = new wafv2.CfnWebACL(this, 'ApiWaf', {
  scope: 'REGIONAL',
  defaultAction: { allow: {} },
  rules: [
    { name: 'RateLimitRule', priority: 1, action: { block: {} }, statement: { rateBasedStatement: { limit: 2000, aggregateKeyType: 'IP' } } },
    { name: 'AWSManagedRules', priority: 2, overrideAction: { none: {} }, statement: { managedRuleGroupStatement: { vendorName: 'AWS', name: 'AWSManagedRulesCommonRuleSet' } } },
    { name: 'KnownBadInputs', priority: 3, action: { block: {} }, statement: { sqliMatchStatement: { fieldToMatch: { allQueryArguments: {} }, textTransformations: [{ priority: 0, type: 'URL_DECODE' }] } } }
  ],
  visibilityConfig: { sampledRequestsEnabled: true, cloudWatchMetricsEnabled: true, metricName: 'ApiWaf' }
});

new wafv2.CfnWebACLAssociation(this, 'WafAssociation', {
  resourceArn: `arn:aws:apigateway:${region}::/restapis/${api.restApiId}/stages/prod`,
  webAclArn: webAcl.attrArn
});
```

### 5. VTL Templates for Error Normalization (`lib/constructs/vtl-templates.ts`)
```typescript
export const ERROR_VTL = `
#set($inputRoot = $input.path('$'))
{
  "type": "https://tools.ietf.org/html/rfc9457",
  "title": "$inputRoot.error",
  "status": $context.responseOverride.status,
  "detail": "$inputRoot.message",
  "instance": "$context.requestId"
}
`;

export const SUCCESS_VTL = "$input.json('$')";
```

### 6. Sandbox Environment
- Stage `sandbox` com mock integration
- Dados de exemplo realistas
- Reset endpoint: `POST /v1/sandbox/reset` (apenas sandbox)
- Rate limit mais permissivo para testes

## Acceptance Criteria
- [ ] CDK deploya sem erro (prod + sandbox)
- [ ] Authorizer anexado a todos endpoints protegidos
- [ ] Usage plans funcionando (throttle + quota)
- [ ] Custom domain `api.averta.com` e `sandbox-api.averta.com`
- [ ] WAF ativo com regras básicas
- [ ] Logs CloudWatch estruturados
- [ ] VTL normaliza erros para RFC 9457
- [ ] Sandbox retorna mocks sem chamar backend
- [ ] Métricas: latency p99 < 200ms, error rate < 0.1%

## Referências
- Card 40 (OpenAPI Spec) - Paths e models
- Card 41 (API Key Model) - Tier config
- Card 42 (JWT Authorizer) - Lambda ARN
- `infrastructure/` - CDK project