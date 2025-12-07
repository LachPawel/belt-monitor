"""
Belt Monitor REST API
FastAPI-based API for conveyor belt monitoring system
"""
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import logging

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.belt_analyzer import BeltAnalyzer, AnalysisResult
from app.report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Belt Monitor API",
    description="System monitorowania szerokości taśmy przenośnika - API REST",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for analysis results
UPLOAD_DIR = Path("data/uploads")
REPORTS_DIR = Path("reports")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for frontend
STATIC_DIR = Path("static")
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
    logger.info(f"Mounted static files from {STATIC_DIR}")
else:
    logger.warning(f"Static directory not found at {STATIC_DIR}")

# In-memory storage for results (in production, use a database)
analysis_results = {}



# Pydantic models
class AnalysisConfig(BaseModel):
    """Configuration for belt analysis"""
    min_width_threshold: float = Field(default=100.0, description="Minimum expected belt width in pixels")
    max_width_threshold: float = Field(default=2000.0, description="Maximum expected belt width in pixels")
    seam_detection_threshold: float = Field(default=0.3, description="Sensitivity for seam detection (0-1)")
    sample_rate: int = Field(default=1, description="Process every Nth frame")
    roi_x: Optional[int] = Field(default=None, description="ROI x coordinate")
    roi_y: Optional[int] = Field(default=None, description="ROI y coordinate")
    roi_width: Optional[int] = Field(default=None, description="ROI width")
    roi_height: Optional[int] = Field(default=None, description="ROI height")


class SegmentResponse(BaseModel):
    """Segment measurement response"""
    segment_id: int
    frame_start: int
    frame_end: int
    min_width_px: float
    max_width_px: float
    avg_width_px: float
    measurement_count: int


class AlertResponse(BaseModel):
    """Alert response"""
    type: str
    frame: Optional[int]
    message: str
    severity: str


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    analysis_id: str
    source_file: str
    total_frames: int
    fps: float
    total_segments: int
    segments: List[SegmentResponse]
    alerts: List[AlertResponse]
    created_at: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str


# API Endpoints

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Belt Monitor API",
        "version": "1.0.0",
        "description": "System monitorowania szerokości taśmy przenośnika",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "analyze": "/api/v1/analyze",
            "results": "/api/v1/results",
            "reports": "/api/v1/reports"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_media(
    file: UploadFile = File(..., description="Video or image file to analyze"),
    min_width_threshold: float = Query(100.0, description="Min expected belt width (px)"),
    max_width_threshold: float = Query(2000.0, description="Max expected belt width (px)"),
    seam_threshold: float = Query(0.3, description="Seam detection sensitivity"),
    sample_rate: int = Query(1, description="Process every Nth frame"),
    roi_x: Optional[int] = Query(None, description="ROI x coordinate"),
    roi_y: Optional[int] = Query(None, description="ROI y coordinate"),
    roi_w: Optional[int] = Query(None, description="ROI width"),
    roi_h: Optional[int] = Query(None, description="ROI height")
):
    """
    Analyze video or image for belt width measurements.
    
    Accepts video files (mp4, avi, mov) or images (jpg, png).
    Returns segment-wise width measurements and alerts.
    """
    # Validate file type
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.jpg', '.jpeg', '.png', '.bmp'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    # Save uploaded file
    analysis_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_path = UPLOAD_DIR / f"{analysis_id}{file_ext}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Configure analyzer
        roi = None
        if all([roi_x is not None, roi_y is not None, roi_w is not None, roi_h is not None]):
            roi = (roi_x, roi_y, roi_w, roi_h)
        
        analyzer = BeltAnalyzer(
            min_width_threshold=min_width_threshold,
            max_width_threshold=max_width_threshold,
            seam_detection_threshold=seam_threshold,
            roi=roi
        )
        
        # Run analysis
        if file_ext in {'.jpg', '.jpeg', '.png', '.bmp'}:
            result = analyzer.analyze_image(str(file_path))
        else:
            result = analyzer.analyze_video(str(file_path), sample_rate=sample_rate)
        
        # Store result
        analysis_results[analysis_id] = result
        
        # Build response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            source_file=file.filename,
            total_frames=result.total_frames,
            fps=result.fps,
            total_segments=len(result.segments),
            segments=[
                SegmentResponse(
                    segment_id=s.segment_id,
                    frame_start=s.frame_start,
                    frame_end=s.frame_end,
                    min_width_px=round(s.min_width, 2),
                    max_width_px=round(s.max_width, 2),
                    avg_width_px=round(s.avg_width, 2),
                    measurement_count=len(s.widths)
                )
                for s in result.segments
            ],
            alerts=[
                AlertResponse(
                    type=a.get("type", "unknown"),
                    frame=a.get("frame"),
                    message=a.get("message", ""),
                    severity=a.get("severity", "info")
                )
                for a in result.alerts
            ],
            created_at=datetime.now().isoformat()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup uploaded file
        if file_path.exists():
            file_path.unlink()


@app.get("/api/v1/results/{analysis_id}", response_model=AnalysisResponse)
async def get_result(analysis_id: str):
    """Get analysis result by ID"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id]
    return AnalysisResponse(
        analysis_id=analysis_id,
        source_file=result.source_file,
        total_frames=result.total_frames,
        fps=result.fps,
        total_segments=len(result.segments),
        segments=[
            SegmentResponse(
                segment_id=s.segment_id,
                frame_start=s.frame_start,
                frame_end=s.frame_end,
                min_width_px=round(s.min_width, 2),
                max_width_px=round(s.max_width, 2),
                avg_width_px=round(s.avg_width, 2),
                measurement_count=len(s.widths)
            )
            for s in result.segments
        ],
        alerts=[
            AlertResponse(
                type=a.get("type", "unknown"),
                frame=a.get("frame"),
                message=a.get("message", ""),
                severity=a.get("severity", "info")
            )
            for a in result.alerts
        ],
        created_at=datetime.now().isoformat()
    )


@app.get("/api/v1/results")
async def list_results():
    """List all analysis results with metadata"""
    results_list = []
    for aid, result in analysis_results.items():
        results_list.append({
            "analysis_id": aid,
            "source_file": getattr(result, "source_file", "unknown"),
            "created_at": getattr(result, "created_at", datetime.now().isoformat()), # Fallback if not stored
            "total_segments": len(result.segments),
            "fps": result.fps
        })
    
    return {
        "count": len(results_list),
        "analyses": sorted(results_list, key=lambda x: x["created_at"], reverse=True)
    }


@app.get("/api/v1/reports/{analysis_id}/excel")
async def get_excel_report(analysis_id: str):
    """Generate and download Excel report"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id]
    generator = ReportGenerator(str(REPORTS_DIR))
    
    filepath = generator.generate_excel(result, f"report_{analysis_id}.xlsx")
    
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"belt_report_{analysis_id}.xlsx"
    )


@app.get("/api/v1/reports/{analysis_id}/csv")
async def get_csv_report(analysis_id: str):
    """Generate and download CSV report"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id]
    generator = ReportGenerator(str(REPORTS_DIR))
    
    filepath = generator.generate_csv(result, f"report_{analysis_id}.csv")
    
    return FileResponse(
        filepath,
        media_type="text/csv",
        filename=f"belt_report_{analysis_id}.csv"
    )


@app.get("/api/v1/reports/{analysis_id}/json")
async def get_json_report(analysis_id: str):
    """Generate and return JSON report"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id]
    return result.to_dict()


@app.delete("/api/v1/results/{analysis_id}")
async def delete_result(analysis_id: str):
    """Delete analysis result"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analysis_results[analysis_id]
    return {"message": f"Analysis {analysis_id} deleted"}


# Run with: uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
