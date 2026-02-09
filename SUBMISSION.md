# Submission Guidelines

## Demo Submission Checklist

### Prerequisites
- [ ] All dependencies installed
- [ ] Docker environment configured
- [ ] Environment variables set up
- [ ] Demo data seeded

### Running the Demo
1. **Quick Start**
   ```bash
   cd infra/docker
   docker-compose -f docker-compose.demo.yml up --build
   ```

2. **Manual Setup**
   - Backend: `cd app/backend && pip install -r requirements.txt && python -m app.main`
   - Frontend: `cd app/frontend && npm install && npm run dev`

### Demo Flow
1. **Authentication**
   - Login with demo credentials
   - Explore role-based access

2. **Guardian Engine**
   - Real-time security monitoring
   - Threat detection demonstrations
   - Risk assessment workflows

3. **AI Assistant**
   - Interactive chat interface
   - Retail insights and analysis
   - Context-aware responses

4. **Dashboard**
   - Live security metrics
   - Risk analytics
   - Activity monitoring

### Key Features to Highlight
- **Security Scanning**: Comprehensive risk assessment
- **Real-time Monitoring**: Live threat detection
- **AI Integration**: Intelligent assistance and insights
- **User Experience**: Intuitive interface and navigation
- **Scalability**: Docker-based deployment

### Testing Scenarios
- Simulate security incidents
- Test different user roles
- Demonstrate AI assistant capabilities
- Show dashboard analytics
- Validate risk assessment workflows

### Performance Metrics
- Response times
- System throughput
- Resource utilization
- User interaction flows

### Documentation
- [README.md](README.md) - Setup and overview
- [SECURITY.md](SECURITY.md) - Security considerations
- [PRIVACY.md](PRIVACY.md) - Privacy policy
- Demo materials in `demo/` folder

### Submission Package
Include the following in your submission:
- Complete source code
- Docker configurations
- Demo presentation materials
- Setup and run instructions
- Test scenarios and results

### Support
- Backend API documentation: `http://localhost:8000/docs`
- Frontend interface: `http://localhost:3000`
- Demo script: `demo/pitch/demo_script.md`