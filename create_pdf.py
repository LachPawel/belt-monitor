"""Generate PDF presentation for Belt Monitor hackathon"""
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

WIDTH, HEIGHT = landscape(A4)
BG_COLOR = HexColor("#1a1a1a")
GOLD = HexColor("#D4AF37")
WHITE = HexColor("#f5f5f5")
GRAY = HexColor("#888888")
DARK_GRAY = HexColor("#2d2d2d")

def draw_background(c):
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)

def draw_gold_bar(c, x, y, w=80, h=6):
    c.setFillColor(GOLD)
    c.rect(x, y, w, h, fill=1, stroke=0)

def slide_title(c):
    draw_background(c)
    cy = HEIGHT / 2
    draw_gold_bar(c, WIDTH/2 - 40, cy + 80)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(WIDTH/2, cy + 30, "BELT MONITOR")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(WIDTH/2, cy - 10, "SYSTEM MONITOROWANIA TAŚMY")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 14)
    c.drawCentredString(WIDTH/2, cy - 40, "Computer Vision • AI • REST API")
    draw_gold_bar(c, WIDTH/2 - 40, cy - 90)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 11)
    c.drawString(30, 30, "JSW IT Systems Hackathon 2025")

def slide_problem(c):
    draw_background(c)
    # Title
    c.setFillColor(GOLD)
    c.rect(30, HEIGHT - 70, 6, 32, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(50, HEIGHT - 60, "PROBLEM")
    
    # Current state box
    c.setFillColor(DARK_GRAY)
    c.roundRect(30, HEIGHT - 320, 380, 220, 8, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(30, HEIGHT - 320, 4, 220, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(50, HEIGHT - 130, "OBECNY STAN")
    c.setFillColor(HexColor("#cccccc"))
    c.setFont("Helvetica", 12)
    c.drawString(50, HEIGHT - 160, "Manualna weryfikacja taśm")
    c.drawString(50, HEIGHT - 180, "przez pracowników JSW S.A.")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 11)
    c.drawString(50, HEIGHT - 220, "⏱️ Czasochłonne")
    c.drawString(50, HEIGHT - 240, "⚠️ Ryzyko niedopatrzeń")
    c.drawString(50, HEIGHT - 260, "💰 Kosztowne przestoje")
    
    # Challenge box
    c.setFillColor(DARK_GRAY)
    c.roundRect(430, HEIGHT - 320, 380, 220, 8, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(430, HEIGHT - 320, 4, 220, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(450, HEIGHT - 130, "WYZWANIE")
    c.setFillColor(HexColor("#cccccc"))
    c.setFont("Helvetica", 12)
    c.drawString(450, HEIGHT - 160, "Automatyczny monitoring")
    c.drawString(450, HEIGHT - 180, "szerokości i segmentów taśmy")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 11)
    c.drawString(450, HEIGHT - 220, "🎯 Praca 24/7")
    c.drawString(450, HEIGHT - 240, "📊 Raporty automatyczne")
    c.drawString(450, HEIGHT - 260, "🚨 Alerty anomalii")

def slide_solution(c):
    draw_background(c)
    c.setFillColor(GOLD)
    c.rect(30, HEIGHT - 70, 6, 32, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(50, HEIGHT - 60, "ROZWIĄZANIE")
    
    boxes = [
        ("01", "ANALIZA OBRAZU", "OpenCV + CV", True),
        ("02", "DETEKCJA SEGMENTÓW", "Wykrywanie szwów", False),
        ("03", "POMIAR SZEROKOŚCI", "Min/Max/Avg", False),
        ("04", "REST API", "FastAPI + Swagger", False),
        ("05", "RAPORTY", "Excel/CSV/JSON", False),
        ("06", "DOCKER", "Konteneryzacja", False),
    ]
    
    for i, (num, title, desc, highlight) in enumerate(boxes):
        row, col = divmod(i, 3)
        x = 30 + col * 270
        y = HEIGHT - 200 - row * 140
        
        if highlight:
            c.setFillColor(GOLD)
        else:
            c.setFillColor(DARK_GRAY)
        c.roundRect(x, y, 250, 110, 8, fill=1, stroke=0)
        
        if not highlight:
            c.setStrokeColor(GOLD)
            c.roundRect(x, y, 250, 110, 8, fill=0, stroke=1)
        
        text_color = BG_COLOR if highlight else GOLD
        c.setFillColor(text_color)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(x + 15, y + 70, num)
        
        c.setFillColor(BG_COLOR if highlight else WHITE)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(x + 15, y + 40, title)
        
        c.setFillColor(HexColor("#333") if highlight else GRAY)
        c.setFont("Helvetica", 10)
        c.drawString(x + 15, y + 20, desc)

def slide_api(c):
    draw_background(c)
    c.setFillColor(GOLD)
    c.rect(30, HEIGHT - 70, 6, 32, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(50, HEIGHT - 60, "REST API")
    
    endpoints = [
        ("POST", "/api/v1/analyze", "Analiza pliku", "#4CAF50"),
        ("GET", "/api/v1/results/{id}", "Szczegóły analizy", "#2196F3"),
        ("GET", "/api/v1/reports/{id}/excel", "Raport Excel", "#2196F3"),
        ("GET", "/api/v1/reports/{id}/csv", "Raport CSV", "#2196F3"),
    ]
    
    for i, (method, path, desc, color) in enumerate(endpoints):
        y = HEIGHT - 140 - i * 60
        c.setFillColor(DARK_GRAY)
        c.roundRect(30, y - 30, 400, 50, 6, fill=1, stroke=0)
        c.setFillColor(HexColor(color))
        c.rect(30, y - 30, 3, 50, fill=1, stroke=0)
        
        c.setFillColor(HexColor(color))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(45, y, method)
        
        c.setFillColor(GOLD)
        c.setFont("Courier", 11)
        c.drawString(95, y, path)
        
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 10)
        c.drawString(45, y - 18, desc)
    
    # Response example
    c.setFillColor(HexColor("#1e1e1e"))
    c.roundRect(450, HEIGHT - 350, 350, 240, 8, fill=1, stroke=0)
    c.setFillColor(GRAY)
    c.setFont("Courier", 9)
    response = [
        "// Response example",
        "{",
        '  "analysis_id": "20251206",',
        '  "total_segments": 5,',
        '  "segments": [{',
        '    "min_width_px": 485.5,',
        '    "max_width_px": 502.3',
        "  }],",
        '  "alerts": [...]',
        "}",
    ]
    for i, line in enumerate(response):
        c.drawString(465, HEIGHT - 130 - i * 20, line)

def slide_tech(c):
    draw_background(c)
    c.setFillColor(GOLD)
    c.rect(30, HEIGHT - 70, 6, 32, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(50, HEIGHT - 60, "TECHNOLOGIE")
    
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(30, HEIGHT - 110, "100% OPEN SOURCE")
    
    techs = ["Python 3.11", "OpenCV", "FastAPI", "NumPy", "Docker", "openpyxl"]
    for i, tech in enumerate(techs):
        row, col = divmod(i, 3)
        x = 30 + col * 140
        y = HEIGHT - 170 - row * 50
        c.setFillColor(DARK_GRAY)
        c.roundRect(x, y, 130, 40, 6, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + 65, y + 14, tech)
    
    # Requirements checklist
    c.setFillColor(DARK_GRAY)
    c.roundRect(460, HEIGHT - 350, 340, 240, 8, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(480, HEIGHT - 130, "✅ ZGODNOŚĆ Z WYMAGANIAMI")
    
    checks = [
        "Licencja open source (MIT)",
        "Konteneryzacja Docker", 
        "REST API z dokumentacją",
        "Wdrożenie on-premise",
        "Raporty Excel/CSV/JSON",
        "Testy jednostkowe (pytest)",
    ]
    c.setFillColor(HexColor("#cccccc"))
    c.setFont("Helvetica", 11)
    for i, check in enumerate(checks):
        c.drawString(480, HEIGHT - 165 - i * 28, f"✓ {check}")

def slide_benefits(c):
    draw_background(c)
    c.setFillColor(GOLD)
    c.rect(30, HEIGHT - 70, 6, 32, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(50, HEIGHT - 60, "KORZYŚCI")
    
    metrics = [
        ("24/7", "CIĄGŁY MONITORING", "Bez przerw", True),
        ("-80%", "CZASU INSPEKCJI", "Automatyzacja", False),
        ("↑", "PREDYKCJA AWARII", "Analiza trendów", False),
    ]
    
    for i, (value, title, desc, highlight) in enumerate(metrics):
        x = 30 + i * 270
        y = HEIGHT - 320
        
        if highlight:
            c.setFillColor(GOLD)
        else:
            c.setFillColor(DARK_GRAY)
        c.roundRect(x, y, 250, 200, 12, fill=1, stroke=0)
        
        if not highlight:
            c.setStrokeColor(GOLD)
            c.setLineWidth(2)
            c.roundRect(x, y, 250, 200, 12, fill=0, stroke=1)
        
        c.setFillColor(BG_COLOR if highlight else GOLD)
        c.setFont("Helvetica-Bold", 48)
        c.drawCentredString(x + 125, y + 130, value)
        
        c.setFillColor(HexColor("#333") if highlight else WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(x + 125, y + 80, title)
        
        c.setFillColor(HexColor("#444") if highlight else GRAY)
        c.setFont("Helvetica", 11)
        c.drawCentredString(x + 125, y + 55, desc)

def slide_end(c):
    draw_background(c)
    cy = HEIGHT / 2
    draw_gold_bar(c, WIDTH/2 - 40, cy + 70)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(WIDTH/2, cy + 20, "BELT MONITOR")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 16)
    c.drawCentredString(WIDTH/2, cy - 15, "Zobacz to, czego nie widać")
    
    techs = [("PYTHON", "OpenCV"), ("API", "FastAPI"), ("DEPLOY", "Docker")]
    for i, (label, tech) in enumerate(techs):
        x = WIDTH/2 - 180 + i * 130
        y = cy - 90
        c.setFillColor(DARK_GRAY)
        c.roundRect(x, y, 110, 55, 8, fill=1, stroke=0)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 10)
        c.drawCentredString(x + 55, y + 35, label)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(x + 55, y + 15, tech)
    
    draw_gold_bar(c, WIDTH/2 - 40, cy - 170)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(WIDTH - 30, 30, "DZIĘKUJEMY!")

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=landscape(A4))
    
    slides = [slide_title, slide_problem, slide_solution, slide_api, slide_tech, slide_benefits, slide_end]
    
    for i, slide_fn in enumerate(slides):
        slide_fn(c)
        if i < len(slides) - 1:
            c.showPage()
    
    c.save()
    print(f"PDF created: {filename}")

if __name__ == "__main__":
    create_pdf("Belt_Monitor_Presentation.pdf")
