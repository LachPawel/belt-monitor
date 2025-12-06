"""Tests for Belt Analyzer"""
import pytest
import numpy as np
import cv2
from app.belt_analyzer import BeltAnalyzer, SegmentMeasurement, AnalysisResult


class TestSegmentMeasurement:
    def test_empty_segment(self):
        seg = SegmentMeasurement(segment_id=1, frame_start=0, frame_end=0)
        assert seg.min_width == 0.0
        assert seg.max_width == 0.0
        assert seg.avg_width == 0.0
    
    def test_segment_stats(self):
        seg = SegmentMeasurement(
            segment_id=1,
            frame_start=0,
            frame_end=100,
            widths=[100.0, 150.0, 200.0]
        )
        assert seg.min_width == 100.0
        assert seg.max_width == 200.0
        assert seg.avg_width == 150.0


class TestBeltAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return BeltAnalyzer(
            min_width_threshold=50,
            max_width_threshold=500
        )
    
    @pytest.fixture
    def test_frame(self):
        # Create synthetic belt image
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw white belt in center
        cv2.rectangle(frame, (150, 0), (490, 480), (255, 255, 255), -1)
        return frame
    
    def test_preprocess_frame(self, analyzer, test_frame):
        binary = analyzer.preprocess_frame(test_frame)
        assert binary.shape[:2] == test_frame.shape[:2]
        assert binary.dtype == np.uint8
    
    def test_measure_width(self, analyzer, test_frame):
        width = analyzer.measure_width(test_frame)
        assert width is not None
        assert 50 < width < 500
    
    def test_detect_edges(self, analyzer, test_frame):
        binary = analyzer.preprocess_frame(test_frame)
        left, right = analyzer.detect_belt_edges(binary)
        assert left is not None
        assert right is not None
        assert left < right
    
    def test_visualization(self, analyzer, test_frame):
        vis = analyzer.get_visualization(test_frame)
        assert vis.shape == test_frame.shape


class TestAnalysisResult:
    def test_to_dict(self):
        seg = SegmentMeasurement(
            segment_id=1,
            frame_start=0,
            frame_end=100,
            widths=[100.0, 200.0]
        )
        result = AnalysisResult(
            source_file="test.mp4",
            total_frames=100,
            fps=30.0,
            segments=[seg],
            alerts=[]
        )
        d = result.to_dict()
        assert d["source_file"] == "test.mp4"
        assert d["total_segments"] == 1
        assert len(d["segments"]) == 1
