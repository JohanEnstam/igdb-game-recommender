# Next Steps: GCP Deployment Plan

## Overview

The IGDB Game Recommendation System is ready for GCP deployment. This document outlines the specific steps needed to move from local development to production deployment.

## Current State

### ✅ Completed
- Feature extraction optimization (text_weight=0.6, max_features=5000)
- Full-scale validation (328,924 games)
- Performance testing (43s extraction, 24s indexing)
- Quality validation (precision@10: 0.8-1.0 across categories)
- Technical implementation (TF-IDF + categorical features + Faiss)

### 📁 Key Files Ready for Deployment
- `ml-pipeline/feature_engineering/feature_extractor.py`
- `ml-pipeline/feature_engineering/similarity_search.py`
- `data/full_dataset/games.json` (328,924 games)
- `ml-pipeline/validate_recommendations_auto.py`

## GCP Deployment Strategy

### Phase 1: Infrastructure Setup (Week 1)

#### 1.1 Containerization
```dockerfile
# Dockerfile for feature extraction
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ml-pipeline/ /app/ml-pipeline/
COPY data/ /app/data/
WORKDIR /app
CMD ["python", "ml-pipeline/feature_extractor.py"]
```

#### 1.2 GCP Resources
- **Cloud Run**: For feature extraction jobs
- **Cloud Storage**: For features, indexes, and datasets
- **BigQuery**: For game data (already exists)
- **Cloud Build**: For container builds
- **Workflows**: For orchestration

#### 1.3 Terraform Configuration
```hcl
# Use existing terraform modules
module "cloud_run" {
  source = "./modules/cloud_run"
  # Configure for ML jobs
}

module "storage" {
  source = "./modules/storage"
  # Configure buckets for features/indexes
}
```

### Phase 2: Feature Extraction Pipeline (Week 2)

#### 2.1 Batch Processing
- **Input**: BigQuery game data
- **Processing**: Feature extraction with optimized parameters
- **Output**: Features and Faiss index to Cloud Storage
- **Orchestration**: Cloud Workflows

#### 2.2 Configuration
```yaml
# workflow.yaml
steps:
  - extract_features:
      input: bigquery://igdb-pipeline-v3.igdb_games_dev.games
      output: gs://igdb-v3-features/
      parameters:
        text_weight: 0.6
        max_features: 5000
        min_df: 5
        ngram_range: [1, 2]
```

### Phase 3: Serving Infrastructure (Week 3)

#### 3.1 Recommendation API
- **Cloud Run**: RESTful API for recommendations
- **Redis**: Caching for frequently accessed data
- **Load Balancing**: For high availability

#### 3.2 API Endpoints
```python
# FastAPI implementation
@app.get("/api/recommendations/{game_id}")
async def get_recommendations(game_id: str, limit: int = 10):
    # Load Faiss index from Cloud Storage
    # Return recommendations
    pass
```

### Phase 4: Monitoring and Optimization (Week 4)

#### 4.1 Monitoring
- **Cloud Monitoring**: Performance metrics
- **Cloud Logging**: Request/response logging
- **Alerting**: Error and performance alerts

#### 4.2 Optimization
- **Caching**: Redis for hot data
- **CDN**: For static assets
- **Auto-scaling**: Based on demand

## Technical Implementation Details

### Feature Extraction Job
```python
# cloud_run_job.py
def main():
    # Load data from BigQuery
    games_df = load_from_bigquery()
    
    # Extract features
    extractor = FeatureExtractor(
        text_weight=0.6,
        max_features=5000,
        min_df=5,
        ngram_range=(1, 2)
    )
    features = extractor.extract_features(games_df)
    
    # Save to Cloud Storage
    save_to_gcs(features, "gs://igdb-v3-features/")
```

### Recommendation Service
```python
# api_service.py
class RecommendationService:
    def __init__(self):
        self.index = load_faiss_index("gs://igdb-v3-features/")
        self.metadata = load_metadata("gs://igdb-v3-features/")
    
    def get_recommendations(self, game_id: str, limit: int = 10):
        # Implementation using existing similarity search
        pass
```

## Cost Estimation

### Monthly Costs (Estimated)
- **Cloud Run**: $50-100 (depending on usage)
- **Cloud Storage**: $20-50 (for features and indexes)
- **BigQuery**: $10-30 (for data access)
- **Redis**: $30-60 (for caching)
- **Total**: $110-240/month

### One-time Costs
- **Cloud Build**: $5-10 (for container builds)
- **Terraform**: $0 (infrastructure as code)

## Risk Mitigation

### Technical Risks
1. **Memory Limits**: Cloud Run has memory limits
   - **Mitigation**: Use batch processing, optimize memory usage
2. **Cold Starts**: API latency on first request
   - **Mitigation**: Keep-warm requests, minimum instances
3. **Data Consistency**: Features vs game data sync
   - **Mitigation**: Versioning, validation checks

### Operational Risks
1. **Cost Overrun**: Unexpected usage spikes
   - **Mitigation**: Budget alerts, usage monitoring
2. **Performance Degradation**: Under load
   - **Mitigation**: Load testing, auto-scaling
3. **Data Loss**: Feature/index corruption
   - **Mitigation**: Backups, versioning

## Success Metrics

### Performance Targets
- **API Response Time**: <200ms (95th percentile)
- **Feature Extraction**: <5 minutes for 328k games
- **Availability**: 99.9% uptime
- **Throughput**: 1000 requests/minute

### Quality Targets
- **Precision@10**: Maintain 0.8-1.0 across categories
- **Coverage**: 90% of popular games found
- **Consistency**: Stable results across time

## Timeline

### Week 1: Infrastructure
- [ ] Set up GCP project and billing
- [ ] Configure Terraform modules
- [ ] Create Cloud Storage buckets
- [ ] Set up Cloud Build

### Week 2: Feature Pipeline
- [ ] Containerize feature extraction
- [ ] Implement Cloud Run job
- [ ] Set up Workflows orchestration
- [ ] Test batch processing

### Week 3: API Service
- [ ] Implement recommendation API
- [ ] Set up Redis caching
- [ ] Configure load balancing
- [ ] Test end-to-end flow

### Week 4: Production
- [ ] Set up monitoring and alerting
- [ ] Performance testing
- [ ] Security review
- [ ] Go-live

## Next Actions

### Immediate (This Week)
1. **Review GCP Setup**: Ensure project and billing are configured
2. **Terraform Planning**: Review existing modules and plan updates
3. **Container Strategy**: Decide on base images and dependencies

### Short Term (Next 2 Weeks)
1. **Feature Pipeline**: Implement and test batch processing
2. **API Development**: Build and test recommendation service
3. **Integration Testing**: End-to-end validation

### Medium Term (Next Month)
1. **Production Deployment**: Go-live with monitoring
2. **Performance Optimization**: Tune for production load
3. **Feature Enhancements**: Implement backlog items

## Conclusion

The GCP deployment plan is well-defined and achievable. The system has been thoroughly tested locally and is ready for production deployment. The phased approach minimizes risk while ensuring a smooth transition to cloud infrastructure.

**Key Success Factors**:
- Leverage existing Terraform modules
- Maintain current performance characteristics
- Implement comprehensive monitoring
- Plan for future enhancements

**Ready to Proceed**: ✅
