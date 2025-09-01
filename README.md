# OpenFlux Streamlit App

A web-based implementation of OpenFlux's AI development assistant capabilities, built with Streamlit and integrated with AWS Bedrock for AI model access.

## Features

- **AI Model Integration**: Support for Claude Sonnet 3.5 v2 and Amazon Nova Pro via AWS Bedrock
- **Codebase Analysis**: Upload and analyze entire project folders
- **Spec Generation**: Create requirements, design documents, and implementation tasks
- **JIRA Integration**: Automatically create JIRA tickets from generated tasks
- **Diagram Generation**: Create ER diagrams and data flow diagrams from code
- **OpenFlux-Style UI**: Familiar interface matching OpenFlux's look and feel
- **Security**: Comprehensive input validation and security measures
- **Monitoring**: Built-in logging and CloudWatch integration

## Quick Start

### Prerequisites

- AWS Account with Bedrock access
- EC2 instance with appropriate IAM role
- Docker and Docker Compose installed

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd openflux-streamlit-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Open http://localhost:8501 in your browser

### AWS EC2 Deployment

1. **Use CloudFormation template**
   ```bash
   aws cloudformation create-stack \
     --stack-name openflux-app \
     --template-body file://deploy/cloudformation-template.yaml \
     --parameters ParameterKey=KeyPairName,ParameterValue=your-key-pair \
                  ParameterKey=VpcId,ParameterValue=vpc-xxxxxxxx \
                  ParameterKey=SubnetId,ParameterValue=subnet-xxxxxxxx \
     --capabilities CAPABILITY_IAM
   ```

2. **Or use the setup script**
   ```bash
   # On your EC2 instance
   chmod +x deploy/ec2-setup.sh
   ./deploy/ec2-setup.sh
   ```

## Configuration

### Environment Variables

- `AWS_DEFAULT_REGION`: AWS region for Bedrock access
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `STREAMLIT_SERVER_PORT`: Port for Streamlit server (default: 8501)

### AWS IAM Permissions

The EC2 instance needs the following permissions:
- `bedrock:InvokeModel` for Claude and Nova models
- `logs:*` for CloudWatch logging
- `cloudwatch:PutMetricData` for metrics
- `s3:*` for file storage (optional)

See `deploy/iam-policy.json` for the complete policy.

## Usage

### 1. Model Selection
- Choose between Claude Sonnet 3.5 v2 or Amazon Nova Pro
- The app will test connectivity and show status

### 2. Folder Analysis
- Select a folder containing your codebase
- The app will read and analyze all text files
- View file statistics and structure

### 3. Spec Generation
- Provide a feature description (with optional codebase context)
- Generate requirements in EARS format with user stories
- Create comprehensive design documents with architecture details
- Generate implementation tasks with requirement references
- Interactive approval workflow with editing capabilities
- Export all documents as Markdown files

### 4. JIRA Integration
- Configure JIRA connection settings
- Automatically create tickets from generated tasks
- Track progress and updates

### 5. Spec Generation Workflow
- **Requirements Generation**: Create EARS-format requirements from feature descriptions
- **Design Documents**: Generate comprehensive technical design documents
- **Implementation Tasks**: Create actionable task lists with requirement references
- **Interactive Workflow**: Step-by-step approval process with editing capabilities
- **Document Export**: Download requirements, design, and tasks as Markdown files

### 6. Diagram Generation
- Generate ER diagrams from data models
- Create data flow diagrams from code analysis
- Export diagrams in various formats

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   AI Service    │    │  AWS Bedrock    │
│                 │◄──►│                 │◄──►│                 │
│  - File Upload  │    │  - Claude 3.5   │    │  - Claude Model │
│  - Chat Interface│    │  - Nova Pro     │    │  - Nova Model   │
│  - Spec Display │    │  - Prompt Mgmt  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  File Service   │    │  Spec Engine    │
│                 │    │                 │
│  - File Reading │    │  - Requirements │
│  - Code Analysis│    │  - Design Docs  │
│  - Validation   │    │  - Task Lists   │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ JIRA Integration│    │ Diagram Generator│
│                 │    │                 │
│  - Ticket Mgmt  │    │  - ER Diagrams  │
│  - Status Track │    │  - Data Flow    │
│  - Bulk Create  │    │  - Mermaid      │
└─────────────────┘    └─────────────────┘
```

## Security

- Input validation and sanitization
- File type and size restrictions
- Rate limiting for uploads
- Secure session management
- AWS IAM role-based authentication
- Security event logging

## Monitoring

- Application logs in `/logs` directory
- CloudWatch metrics integration
- Performance monitoring
- Health checks
- Error tracking and alerting

## Testing

Run the test suite:

```bash
# Unit tests
python -m pytest tests/test_*.py -v

# Integration tests
python -m pytest tests/test_integration.py -v

# All tests
python -m pytest tests/ -v
```

## Troubleshooting

### Common Issues

1. **AWS Bedrock Connection Error: 'BedrockRuntime' object has no attribute 'list_foundation_models'**
   - This error occurs when using the wrong AWS client
   - **Solution**: The app now uses separate clients for control plane (bedrock) and runtime (bedrock-runtime)
   - **Test**: Run `python test_bedrock_connection.py` to verify your setup
   - **IAM Permissions needed**:
     - `bedrock:ListFoundationModels` (for listing available models)
     - `bedrock-runtime:InvokeModel` (for using models)

2. **AWS Bedrock Access Denied**
   - Check IAM role permissions (see deploy/iam-policy.json)
   - Verify Bedrock is available in your region (us-east-1 recommended)
   - Ensure model access is granted for specific model IDs
   - Run the connection test: `python test_bedrock_connection.py`

3. **File Upload Issues**
   - Check file size limits (10MB per file)
   - Verify file types are allowed
   - Check disk space on server

4. **JIRA Integration Fails**
   - Verify JIRA URL and credentials
   - Check network connectivity
   - Validate project permissions

### Logs

- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Security logs: `logs/security.log`

### Health Check

Access the health check endpoint:
```
GET /health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review application logs
- Open an issue in the repository