import * as agentcore from '@aws-cdk/aws-bedrock-agentcore-alpha';
import * as bedrock from '@aws-cdk/aws-bedrock-alpha';
import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
import path from 'path';

export class BackendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const agentRuntimeArtifact = agentcore.AgentRuntimeArtifact.fromAsset(
      path.join(__dirname, "../assets/claude-agent")
    );

    const runtime = new agentcore.Runtime(this, "ClaudeAgentRuntime", {
      runtimeName: "ClaudeAgent",
      agentRuntimeArtifact: agentRuntimeArtifact,
    });

    const sonnetInferenceProfile = bedrock.CrossRegionInferenceProfile.fromConfig({
      geoRegion: bedrock.CrossRegionInferenceProfileRegion.GLOBAL,
      model: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_SONNET_4_5_V1_0
    });
    sonnetInferenceProfile.grantInvoke(runtime);

    const haikuInferenceProfile = bedrock.CrossRegionInferenceProfile.fromConfig({
      geoRegion: bedrock.CrossRegionInferenceProfileRegion.GLOBAL,
      model: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_HAIKU_4_5_V1_0
    });
    haikuInferenceProfile.grantInvoke(runtime);

    new cdk.CfnOutput(this, "AgentRuntimeArn", {
      value: runtime.agentRuntimeArn
    })

  }
}
