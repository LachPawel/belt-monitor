"""
Belt Analyzer - Computer Vision module for conveyor belt monitoring
Detects belt edges, measures width, identifies segments (seams)
"""
import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SegmentMeasurement:
    """Single segment measurement data"""
    segment_id: int
    frame_start: int
    frame_end: int
    widths: List[float] = field(default_factory=list)
    
    @property
    def min_width(self) -> float:
        return min(self.widths) if self.widths else 0.0
    
    @property
    def max_width(self) -> float:
        return max(self.widths) if self.widths else 0.0
    
    @property
    def avg_width(self) -> float:
        return sum(self.widths) / len(self.widths) if self.widths else 0.0
    
    @property
    def width_variance(self) -> float:
        if len(self.widths) < 2:
            return 0.0
        avg = self.avg_width
        return sum((w - avg) ** 2 for w in self.widths) / len(self.widths)


@dataclass
class AnalysisResult:
    """Complete analysis result for a video/image"""
    source_file: str
    total_frames: int
    fps: float
    segments: List[SegmentMeasurement]
    alerts: List[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "source_file": self.source_file,
            "total_frames": self.total_frames,
            "fps": self.fps,
            "total_segments": len(self.segments),
            "segments": [
                {
                    "segment_id": s.segment_id,
                    "frame_start": s.frame_start,
                    "frame_end": s.frame_end,
                    "min_width_px": round(s.min_width, 2),
                    "max_width_px": round(s.max_width, 2),
                    "avg_width_px": round(s.avg_width, 2),
                    "measurement_count": len(s.widths)
                }
                for s in self.segments
            ],
            "alerts": self.alerts
        }


class BeltAnalyzer:
    """
    Conveyor belt width analyzer using computer vision.
    Detects belt edges and seams to measure width per segment.
    """
    
    def __init__(
        self,
        min_width_threshold: float = 100.0,
        max_width_threshold: float = 2000.0,
        seam_detection_threshold: float = 0.3,
        calibration_px_per_mm: float = 1.0,
        roi: Optional[Tuple[int, int, int, int]] = None
    ):
        self.min_width_threshold = min_width_threshold
        self.max_width_threshold = max_width_threshold
        self.seam_detection_threshold = seam_detection_threshold
        self.calibration = calibration_px_per_mm
        self.roi = roi  # (x, y, width, height)
        
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for belt detection"""
        if self.roi:
            x, y, w, h = self.roi
            frame = frame[y:y+h, x:x+w]
        
        # Convert to grayscale
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
            
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive thresholding for belt edge detection
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary
    
    def detect_belt_edges(self, binary: np.ndarray) -> Tuple[Optional[int], Optional[int]]:
        """
        Detect left and right edges of the belt.
        Returns (left_edge, right_edge) in pixels.
        """
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, None
        
        # Find the largest contour (assumed to be the belt)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Edge detection using horizontal projection
        height = binary.shape[0]
        projection = np.sum(binary, axis=0) / 255
        
        # Find edges where projection drops
        threshold = height * 0.3
        left_edge = None
        right_edge = None
        
        for i in range(len(projection)):
            if projection[i] > threshold and left_edge is None:
                left_edge = i
            if projection[len(projection) - 1 - i] > threshold and right_edge is None:
                right_edge = len(projection) - 1 - i
            if left_edge is not None and right_edge is not None:
                break
        
        return left_edge, right_edge
    
    def measure_width(self, frame: np.ndarray) -> Optional[float]:
        """Measure belt width in a single frame"""
        binary = self.preprocess_frame(frame)
        left, right = self.detect_belt_edges(binary)
        
        if left is None or right is None:
            return None
            
        width = abs(right - left)
        
        # Validate width
        if width < self.min_width_threshold or width > self.max_width_threshold:
            return None
            
        return width
    
    def detect_seam(self, frame: np.ndarray, prev_frame: Optional[np.ndarray]) -> bool:
        """
        Detect if there's a seam (segment boundary) between frames.
        Uses intensity change detection and horizontal line detection.
        """
        if prev_frame is None:
            return False
            
        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        else:
            gray_curr = frame
            gray_prev = prev_frame
        
        # Calculate frame difference
        diff = cv2.absdiff(gray_curr, gray_prev)
        
        # Check for horizontal line (seam indicator)
        edges = cv2.Canny(gray_curr, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                minLineLength=frame.shape[1]*0.5, maxLineGap=10)
        
        # Check for significant horizontal lines
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = abs(np.arctan2(y2-y1, x2-x1))
                if angle < 0.1:  # Nearly horizontal
                    return True
        
        # Alternative: Check intensity change
        mean_diff = np.mean(diff)
        if mean_diff > self.seam_detection_threshold * 255:
            return True
            
        return False
    
    def analyze_video(self, video_path: str, sample_rate: int = 1) -> AnalysisResult:
        """
        Analyze video file for belt width and segments.
        
        Args:
            video_path: Path to video file
            sample_rate: Process every Nth frame
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Analyzing video: {video_path}")
        logger.info(f"Total frames: {total_frames}, FPS: {fps}")
        
        segments: List[SegmentMeasurement] = []
        current_segment = SegmentMeasurement(segment_id=1, frame_start=0, frame_end=0)
        alerts: List[dict] = []
        
        prev_frame = None
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            if frame_count % sample_rate != 0:
                continue
            
            # Apply ROI if set
            if self.roi:
                x, y, w, h = self.roi
                roi_frame = frame[y:y+h, x:x+w]
            else:
                roi_frame = frame
            
            # Measure width
            width = self.measure_width(roi_frame)
            
            if width is not None:
                current_segment.widths.append(width)
                current_segment.frame_end = frame_count
                
                # Check for anomalies
                if width < self.min_width_threshold * 1.1:
                    alerts.append({
                        "type": "width_warning",
                        "frame": frame_count,
                        "message": f"Belt width below threshold: {width:.2f}px",
                        "severity": "warning"
                    })
            
            # Check for seam
            if self.detect_seam(roi_frame, prev_frame):
                # Save current segment
                if current_segment.widths:
                    segments.append(current_segment)
                
                # Start new segment
                current_segment = SegmentMeasurement(
                    segment_id=len(segments) + 1,
                    frame_start=frame_count,
                    frame_end=frame_count
                )
                logger.info(f"Seam detected at frame {frame_count}")
            
            prev_frame = roi_frame.copy()
        
        # Don't forget the last segment
        if current_segment.widths:
            segments.append(current_segment)
        
        cap.release()
        
        # If no seams detected, treat entire video as one segment
        if not segments:
            segments = [current_segment] if current_segment.widths else []
        
        logger.info(f"Analysis complete. Found {len(segments)} segments")
        
        return AnalysisResult(
            source_file=video_path,
            total_frames=total_frames,
            fps=fps,
            segments=segments,
            alerts=alerts
        )
    
    def analyze_image(self, image_path: str) -> AnalysisResult:
        """Analyze single image for belt width"""
        frame = cv2.imread(image_path)
        
        if frame is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        width = self.measure_width(frame)
        
        segment = SegmentMeasurement(
            segment_id=1,
            frame_start=0,
            frame_end=0,
            widths=[width] if width else []
        )
        
        alerts = []
        if width and width < self.min_width_threshold * 1.1:
            alerts.append({
                "type": "width_warning",
                "message": f"Belt width below threshold: {width:.2f}px",
                "severity": "warning"
            })
        
        return AnalysisResult(
            source_file=image_path,
            total_frames=1,
            fps=0,
            segments=[segment] if segment.widths else [],
            alerts=alerts
        )
    
    def get_visualization(self, frame: np.ndarray) -> np.ndarray:
        """Generate visualization with detected edges"""
        vis = frame.copy()
        binary = self.preprocess_frame(frame)
        left, right = self.detect_belt_edges(binary)
        
        if left is not None and right is not None:
            height = frame.shape[0]
            # Draw edge lines
            cv2.line(vis, (left, 0), (left, height), (0, 255, 0), 2)
            cv2.line(vis, (right, 0), (right, height), (0, 255, 0), 2)
            
            # Draw width measurement
            mid_y = height // 2
            cv2.line(vis, (left, mid_y), (right, mid_y), (255, 0, 0), 2)
            
            width = right - left
            cv2.putText(vis, f"Width: {width}px", (left, mid_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        return vis
