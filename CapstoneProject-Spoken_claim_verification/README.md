# Spoken Claim Verification System

A comprehensive end-to-end system for verifying spoken claims in short-form videos using Large Language Models (LLMs), Retrieval-Augmented Verification (RAV), and big data infrastructure.

## Overview

This system addresses the challenge of misinformation spread through short-form video platforms by providing:

- **Speech Recognition**: Converts video audio to text using Whisper large-v3
- **Claim Extraction**: Decomposes transcripts into atomic, verifiable claims using Gemini 2.5 Pro
- **Evidence Retrieval**: Searches the web for relevant evidence using Google Search API
- **Claim Verification**: Verifies claims against retrieved evidence using LLMs
- **Monitoring & Analytics**: Tracks system performance with MySQL, InfluxDB, and Grafana

## System Architecture

### Core Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Speech Recognition | Whisper large-v3 | Audio-to-text transcription |
| Claim Extraction | Gemini 2.5 Pro | Decompose transcripts into claims |
| Evidence Retrieval | Google Search API | Find web evidence for claims |
| Verification | Gemini 2.5 Pro | Verify claims with evidence |
| Data Storage | MySQL | Structured data (claims, verdicts) |
| Metrics Storage | InfluxDB | Time-series metrics (latency, throughput) |
| Visualization | Grafana | Real-time dashboards |

### Design Principles

1. **Modularity**: Each component can be developed, tested, and modified independently
2. **Observability**: All metrics and logs are tracked for transparency and debugging
3. **Reproducibility**: Dockerized infrastructure with version-pinned dependencies

## Performance Metrics

- **Claim-level F1-score**: 0.869
- **Average latency**: 2.4 seconds per claim
- **Total claims processed**: ~1,500 from 150 videos
- **API cost**: ~$10.50 for 1,500 claims

## Installation

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- 16GB RAM (minimum)
- GPU recommended for faster processing

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CapstoneProject-Spoken_claim_verification
   ```

2. **Run setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start services**
   ```bash
   docker-compose up -d
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Usage

### Basic Example

```python
from app import ClaimVerificationPipeline

# Initialize pipeline
pipeline = ClaimVerificationPipeline()

# Process a video
results = pipeline.process_video(
    video_path="path/to/video.mp4",
    video_id="video_001",
    save_to_db=True
)

# Print results
import json
print(json.dumps(results, indent=2))

# Cleanup
pipeline.cleanup()
```

### Processing Pipeline

1. **Audio Extraction**: Extract audio from video
2. **Transcription**: Convert audio to text using Whisper
3. **Claim Extraction**: Extract atomic claims from transcript
4. **Evidence Retrieval**: Search for evidence for each claim
5. **Evidence Ranking**: Rank evidence by relevance
6. **Verification**: Verify claims using evidence
7. **Storage**: Save results to MySQL and metrics to InfluxDB

## File Structure

```
CapstoneProject-Spoken_claim_verification/
├── whisper_service/           # Speech recognition service
│   ├── whisper_server.py
│   └── requirements.txt
├── components/                # Core components
│   ├── gemini_service.py      # LLM service for extraction & verification
│   ├── evidence_retriever.py  # Web evidence retrieval
│   ├── evidence_reranker.py   # Evidence ranking
│   └── baseline_model.py      # Baseline for comparison
├── utils/                     # Utility modules
│   ├── wer_integration.py     # Word error rate calculation
│   ├── data_fetcher.py        # Data management
│   └── database_manager.py    # Database operations
├── pages/                     # Streamlit pages (optional)
├── evaluation/                # Evaluation modules
├── docker/                    # Docker configurations
│   ├── mysql/
│   ├── influxdb/
│   └── grafana/
├── data/                      # Data directory
│   ├── videos/
│   ├── audio/
│   └── transcripts/
├── app.py                     # Main application
├── docker-compose.yml         # Container orchestration
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script
├── .env.example              # Environment template
└── README.md                 # This file
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

- `GOOGLE_API_KEY`: Google API key for Gemini
- `GOOGLE_SEARCH_API_KEY`: Google Custom Search API key
- `GOOGLE_SEARCH_ENGINE_ID`: Google Custom Search Engine ID
- `MYSQL_PASSWORD`: MySQL root password
- `INFLUXDB_TOKEN`: InfluxDB authentication token

### Model Configuration

Edit `config.yaml` to adjust:

- Whisper model size
- Gemini temperature and token limits
- Evidence retrieval parameters
- Verification confidence thresholds

## Monitoring

### Grafana Dashboards

Access Grafana at `http://localhost:3000` (default: admin/admin)

Available dashboards:
- **System Performance**: Latency, throughput, error rates
- **Claim Verification**: Verification results distribution
- **API Usage**: Token usage and costs
- **Error Analysis**: Error propagation and sources

### Database Queries

Access MySQL at `localhost:3306`:

```sql
-- Get all claims for a video
SELECT * FROM claims WHERE video_id = 'video_001';

-- Get verification results
SELECT c.claim_text, v.label, v.confidence 
FROM claims c 
JOIN verifications v ON c.id = v.claim_id 
WHERE c.video_id = 'video_001';

-- Calculate metrics
SELECT 
    COUNT(*) as total_claims,
    SUM(CASE WHEN v.label = 'true' THEN 1 ELSE 0 END) as true_count,
    SUM(CASE WHEN v.label = 'false' THEN 1 ELSE 0 END) as false_count,
    AVG(v.confidence) as avg_confidence
FROM verifications v;
```

## API Endpoints

### Whisper Service

- `POST /transcribe`: Transcribe audio file
- `GET /health`: Health check

### Main Application

- `POST /process-video`: Process a video
- `GET /claims/{video_id}`: Get claims for a video
- `GET /verification/{claim_id}`: Get verification result

## Evaluation

### Metrics

- **Precision**: Correctly verified claims / Total verified claims
- **Recall**: Correctly verified claims / Total claims
- **F1-Score**: Harmonic mean of precision and recall
- **Latency**: Time to process one claim
- **Throughput**: Claims processed per minute

### Baseline Comparison

The system includes a baseline model using keyword matching for comparison:

```python
from components import BaselineModel

baseline = BaselineModel()
results = baseline.batch_verify_claims(claims, evidence_list)
```

## Troubleshooting

### Common Issues

1. **Whisper model download fails**
   - Check internet connection
   - Ensure sufficient disk space (2GB+)
   - Try manual download: `python -c "import whisper; whisper.load_model('large-v3')"`

2. **MySQL connection error**
   - Check Docker services: `docker-compose ps`
   - Verify credentials in `.env`
   - Wait for MySQL to be ready: `docker-compose logs mysql`

3. **InfluxDB authentication fails**
   - Generate new token: `docker-compose exec influxdb influx auth create`
   - Update `.env` with new token

4. **API rate limits**
   - Implement exponential backoff
   - Use batch processing
   - Monitor token usage in InfluxDB

## Contributing

1. Create a feature branch
2. Make changes with clear commit messages
3. Add tests for new functionality
4. Submit pull request

## Citation

If you use this system in your research, please cite:

```bibtex
@thesis{capstone2024,
  title={Spoken Claim Verification in Short-Form Videos},
  author={Author Name},
  year={2024},
  school={University Name}
}
```

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- Supervisor: Dr. Reema Ahmed Abdalla Bin Thabit
- Program Supervisor: Prof. Dr. Noor Zaman Jhanjhi
- Examiner: Dr Nur Fatin Liyana Binti Mohd Rosely

## Contact

For questions or issues, please open an issue on the repository or contact the development team.

---

**Last Updated**: December 2024
**Version**: 1.0.0
