# Quick Start Guide for Administrators

This quick start guide provides essential information for administrators to deploy, configure, and manage the Aideon AI Lite platform. For detailed instructions, refer to the comprehensive Administrator Training Guide.

## Deployment Essentials

### Prerequisites
- Kubernetes v1.25+
- Helm v3.8+
- Docker v20.10+
- Terraform v1.3+ (for cloud deployments)

### Minimum Hardware Requirements
- CPU: 32 cores
- Memory: 128GB RAM
- Storage: 2TB SSD
- Network: 10Gbps internal, 1Gbps external

### Basic Deployment Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/AllienNova/ApexAgent.git
   cd ApexAgent
   ```

2. **Add Helm repository**
   ```bash
   helm repo add aideon https://charts.aideon.ai
   helm repo update
   ```

3. **Create namespaces**
   ```bash
   kubectl apply -f kubernetes/base/namespaces/
   ```

4. **Deploy the platform**
   ```bash
   helm install aideon-ai-lite aideon/aideon-ai-lite \
     --namespace aideon-system \
     --create-namespace \
     --set environment=production \
     --values production-values.yaml
   ```

5. **Verify deployment**
   ```bash
   kubectl get deployments --all-namespaces -l app.kubernetes.io/part-of=aideon-ai-lite
   ./scripts/health-check.sh
   ```

## Essential Administration Tasks

### Access Administrative Console
- URL: `https://admin.aideon.ai`
- Default credentials: Provided during installation
- First login requires password change

### User Management
- Add user: Navigate to "Users" > "Add User"
- Assign roles: Navigate to "Users" > select user > "Edit" > modify roles
- Reset password: Navigate to "Users" > select user > "Reset Password"

### Monitoring
- Access Grafana: `https://grafana.aideon.ai`
- Access Kibana: `https://kibana.aideon.ai`
- Access Jaeger: `https://jaeger.aideon.ai`

### Scaling
- Manual scaling:
  ```bash
  kubectl scale deployment/api-gateway --replicas=5 -n aideon-backend
  ```
- Configure HPA:
  ```bash
  kubectl apply -f kubernetes/autoscaling/hpa.yaml
  ```

### Backup and Recovery
- Create backup:
  ```bash
  kubectl apply -f kubernetes/backup/backup-job.yaml
  ```
- Restore from backup:
  ```bash
  kubectl apply -f kubernetes/backup/recovery-job.yaml
  ```

## Common Troubleshooting

### Check Component Status
```bash
kubectl get pods --all-namespaces -l app.kubernetes.io/part-of=aideon-ai-lite
```

### View Logs
```bash
kubectl logs -l app=api-gateway -n aideon-backend
kubectl logs -l app=vector-db -n aideon-knowledge
kubectl logs -l app=dr-tardis -n aideon-backend
```

### Restart Component
```bash
kubectl rollout restart deployment/api-gateway -n aideon-backend
```

### Check Resource Usage
```bash
kubectl top pods -n aideon-backend
```

## Security Best Practices

- Rotate API keys regularly
- Enable multi-factor authentication for all admin accounts
- Apply security updates promptly
- Review audit logs weekly
- Conduct regular security assessments

## Support Resources

- Documentation: `https://docs.aideon.ai`
- Support Portal: `https://support.aideon.ai`
- Emergency Support: +1-800-AIDEON-911

For detailed instructions on all administrative tasks, refer to the comprehensive Administrator Training Guide.
