#!/usr/bin/env python3
"""Generate the public EasyMath Academy user and operations manual."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "이지매쓰-학원관리-상세-운영매뉴얼.pdf"
REPOSITORY_URL = os.environ.get(
    "EASYMATH_REPOSITORY_URL",
    "https://github.com/cowboykys-tech/easymath-academy",
)
VERSION = "2026.10.17"
PAGE_W, PAGE_H = A4

INK = colors.HexColor("#173F35")
INK_2 = colors.HexColor("#2A5A4D")
MINT = colors.HexColor("#E5F1EB")
CREAM = colors.HexColor("#F7F3EA")
YELLOW = colors.HexColor("#F3CB69")
CORAL = colors.HexColor("#E97861")
LINE = colors.HexColor("#DCD8CD")
MUTED = colors.HexColor("#68766F")
WHITE = colors.white


class AccentRule(Flowable):
    def __init__(self, width=30 * mm, height=3 * mm, color=YELLOW):
        super().__init__()
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.roundRect(0, 0, self.width, self.height, self.height / 2, fill=1, stroke=0)


class ManualDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            if style_name == "H1":
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))
            elif style_name == "H2":
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page))


def register_fonts():
    font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    pdfmetrics.registerFont(TTFont("Korean", font_path))
    pdfmetrics.registerFont(TTFont("KoreanBold", font_path))
    pdfmetrics.registerFontFamily("Korean", normal="Korean", bold="KoreanBold")


register_fonts()

base = getSampleStyleSheet()
styles = {
    "cover_kicker": ParagraphStyle(
        "CoverKicker", fontName="KoreanBold", fontSize=10, leading=14,
        textColor=YELLOW, alignment=TA_LEFT, spaceAfter=7 * mm,
    ),
    "cover_title": ParagraphStyle(
        "CoverTitle", fontName="KoreanBold", fontSize=31, leading=42,
        textColor=WHITE, alignment=TA_LEFT, wordWrap="CJK", spaceAfter=8 * mm,
    ),
    "cover_sub": ParagraphStyle(
        "CoverSub", fontName="Korean", fontSize=13, leading=22,
        textColor=colors.HexColor("#D4E4DE"), wordWrap="CJK",
    ),
    "h1": ParagraphStyle(
        "H1", fontName="KoreanBold", fontSize=23, leading=31,
        textColor=INK, wordWrap="CJK", spaceBefore=3 * mm, spaceAfter=5 * mm,
        keepWithNext=True,
    ),
    "h2": ParagraphStyle(
        "H2", fontName="KoreanBold", fontSize=15, leading=22,
        textColor=INK_2, wordWrap="CJK", spaceBefore=5 * mm, spaceAfter=2.5 * mm,
        keepWithNext=True,
    ),
    "h3": ParagraphStyle(
        "H3", fontName="KoreanBold", fontSize=11.5, leading=18,
        textColor=INK, wordWrap="CJK", spaceBefore=3 * mm, spaceAfter=1.5 * mm,
        keepWithNext=True,
    ),
    "body": ParagraphStyle(
        "Body", fontName="Korean", fontSize=9.5, leading=16.5,
        textColor=colors.HexColor("#253B35"), wordWrap="CJK", spaceAfter=2.5 * mm,
    ),
    "small": ParagraphStyle(
        "Small", fontName="Korean", fontSize=8, leading=13,
        textColor=MUTED, wordWrap="CJK",
    ),
    "note": ParagraphStyle(
        "Note", fontName="Korean", fontSize=9, leading=15,
        textColor=INK, wordWrap="CJK",
    ),
    "table_head": ParagraphStyle(
        "TableHead", fontName="KoreanBold", fontSize=8.3, leading=12,
        textColor=WHITE, alignment=TA_CENTER, wordWrap="CJK",
    ),
    "table": ParagraphStyle(
        "Table", fontName="Korean", fontSize=8.1, leading=13,
        textColor=colors.HexColor("#253B35"), wordWrap="CJK",
    ),
    "table_bold": ParagraphStyle(
        "TableBold", fontName="KoreanBold", fontSize=8.1, leading=13,
        textColor=INK, wordWrap="CJK",
    ),
    "toc_title": ParagraphStyle(
        "TOCTitle", fontName="KoreanBold", fontSize=26, leading=34,
        textColor=INK, wordWrap="CJK", spaceAfter=8 * mm,
    ),
}


def P(text, style="body"):
    return Paragraph(text, styles[style])


def heading1(number, title):
    return [AccentRule(), Spacer(1, 4 * mm), P(f"{number}. {title}", "h1")]


def heading2(title):
    return P(title, "h2")


def bullets(items, level=0):
    return [ListFlowable(
        [ListItem(P(item, "body"), leftIndent=4 * mm) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=(7 + level * 4) * mm,
        bulletFontName="Korean",
        bulletFontSize=7,
        bulletColor=INK_2,
        spaceAfter=2 * mm,
    )]


def numbered(items):
    return [ListFlowable(
        [ListItem(P(item, "body"), leftIndent=5 * mm) for item in items],
        bulletType="1",
        leftIndent=9 * mm,
        bulletFontName="KoreanBold",
        bulletFontSize=8,
        bulletColor=INK,
        spaceAfter=3 * mm,
    )]


def callout(title, body, color=MINT, accent=INK_2):
    data = [[P(title, "table_bold")], [P(body, "note")]]
    table = Table(data, colWidths=[166 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("BOX", (0, 0), (-1, -1), 0.7, accent),
        ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ("TOPPADDING", (0, 1), (-1, 1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
    ]))
    return [table, Spacer(1, 4 * mm)]


def data_table(headers, rows, widths=None):
    data = [[P(value, "table_head") for value in headers]]
    for row in rows:
        data.append([P(value, "table_bold" if index == 0 else "table") for index, value in enumerate(row)])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, CREAM]),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return [table, Spacer(1, 4 * mm)]


def page_break():
    return PageBreak()


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(YELLOW)
    canvas.roundRect(22 * mm, PAGE_H - 48 * mm, 17 * mm, 17 * mm, 4 * mm, fill=1, stroke=0)
    canvas.setFont("KoreanBold", 24)
    canvas.setFillColor(INK)
    canvas.drawCentredString(30.5 * mm, PAGE_H - 42 * mm, "E")
    canvas.setFillColor(colors.HexColor("#2A5A4D"))
    canvas.circle(PAGE_W - 20 * mm, 22 * mm, 60 * mm, fill=1, stroke=0)
    canvas.restoreState()


def regular_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(22 * mm, PAGE_H - 15 * mm, PAGE_W - 22 * mm, PAGE_H - 15 * mm)
    canvas.setFont("Korean", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(22 * mm, PAGE_H - 11 * mm, "이지매쓰 학원관리 시스템")
    canvas.drawRightString(PAGE_W - 22 * mm, PAGE_H - 11 * mm, f"상세 운영 매뉴얼 · v{VERSION}")
    canvas.line(22 * mm, 14 * mm, PAGE_W - 22 * mm, 14 * mm)
    canvas.drawString(22 * mm, 9 * mm, "개인정보와 비밀키는 이 문서나 Git에 기록하지 않습니다.")
    canvas.drawRightString(PAGE_W - 22 * mm, 9 * mm, f"{doc.page}")
    canvas.restoreState()


def build_story():
    story = []
    icon = ROOT / "dist" / "owner-icon-512.png"
    if icon.exists():
        story += [Spacer(1, 45 * mm), Image(str(icon), width=34 * mm, height=34 * mm), Spacer(1, 13 * mm)]
    else:
        story += [Spacer(1, 80 * mm)]
    story += [
        P("EASYMATH ACADEMY", "cover_kicker"),
        P("이지매쓰 학원관리 시스템<br/>상세 사용자·설치·운영 매뉴얼", "cover_title"),
        P("원장님 앱 · 선생님 앱 · 학생 등원 앱 · 학부모 피드백 · 근태 · 상담 · 백업 · PWA 운영", "cover_sub"),
        Spacer(1, 18 * mm),
        P(f"문서 버전 {VERSION}<br/>{date.today().isoformat()} 기준", "cover_sub"),
        Spacer(1, 18 * mm),
        P("이 문서는 공개 가능한 프로그램 사용법만 다룹니다.<br/>실제 학생·학부모·선생님의 개인정보, 비밀번호, API 키와 카카오 세션은 포함하지 않습니다.", "cover_sub"),
        page_break(),
    ]

    story += [P("목차", "toc_title")]
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name="TOC1", fontName="KoreanBold", fontSize=10, leading=18, leftIndent=0, firstLineIndent=0, textColor=INK),
        ParagraphStyle(name="TOC2", fontName="Korean", fontSize=8.5, leading=15, leftIndent=7 * mm, firstLineIndent=0, textColor=MUTED),
    ]
    story += [toc, page_break()]

    story += heading1("1", "이 문서를 사용하는 방법")
    story += [
        P("이 매뉴얼은 개발 문서가 아니라 실제 학원 운영자가 설치와 업무 흐름을 이해할 수 있도록 만든 운영 안내서다. 처음 도입할 때는 1장부터 7장까지 순서대로 읽고, 운영 중에는 필요한 기능의 장과 문제 해결 장을 찾아본다."),
        heading2("세 가지 앱을 먼저 구분한다"),
    ]
    story += data_table(
        ["앱", "주 사용자", "핵심 목적", "기본 주소"],
        [
            ["원장님 앱", "원장·관리자", "학생·직원 등록, 전체 시간표, 승인, 상담, 피드백, 리포트", "/"],
            ["선생님 앱", "강사·직원", "본인 수업, 학생평가, 출퇴근·조퇴·추가근무 요청", "/teacher.html"],
            ["학생 등원 앱", "학생·안내 데스크", "전화번호 뒤 4자리 등원, 중복 이름 선택, 알림 기록", "/kiosk.html"],
        ],
        [28 * mm, 31 * mm, 75 * mm, 32 * mm],
    )
    story += callout(
        "온라인 전용 PWA",
        "세 앱은 홈 화면에 설치할 수 있지만 운영 데이터는 하나의 서버와 데이터베이스에 저장된다. 인터넷이 끊기면 오래된 학생·근태 정보를 보여주지 않고 연결 필요 화면을 표시한다. 외부 운영에는 도메인과 HTTPS가 필요하다.",
    )
    story += [heading2("현재 구현 상태를 정확히 이해한다")]
    story += bullets([
        "학생·선생님·시간표·수업기록·평가·근태·상담·등원·메시지 이력은 SQLite 데이터베이스에 누적된다.",
        "사진 원본은 전용 사진 폴더에 저장되고 데이터베이스 기록과 연결된다.",
        "카카오 로그인, AI 작성기, 카카오 송수신기는 설치 장소의 계정·키·장치가 연결되기 전까지 준비 상태다.",
        "옵시디언은 사용법과 정책 문서용이다. 실제 개인정보와 운영 데이터의 원본 저장소가 아니다.",
        "수납·미납·급여 자동 계산은 규칙이 확정된 뒤 추가할 범위이며 현재 핵심 기능에 포함되지 않는다.",
    ])
    story.append(page_break())

    story += heading1("2", "전체 구조와 데이터 흐름")
    story += [P("사용자가 세 화면에서 입력한 정보는 브라우저에 따로 흩어지는 것이 아니라 학원 서버 API를 통해 하나의 운영 데이터베이스로 모인다. 이 구조 때문에 원장·선생님·등원 기기가 같은 내용을 함께 볼 수 있다."), heading2("핵심 흐름")]
    story += data_table(
        ["입력", "저장", "다음 동작"],
        [
            ["원장님이 학생·선생님 등록", "학생·직원 기본정보", "시간표 배정 목록과 개인 이력에 사용"],
            ["원장님이 시간표 배정", "수업·요일·시간·담당자·학생", "선생님 앱의 본인 달력에 표시"],
            ["선생님이 평가 작성", "출결·체크리스트·관찰 메모", "원장님 피드백 초안과 학생 누적 기록에 사용"],
            ["학생이 등원번호 입력", "등원 시각·기기·알림 결과", "원장님 현황, 주간·월간 리포트에 사용"],
            ["선생님이 근태 요청", "요청 상태와 시간", "원장 승인 뒤 확정 근무기록으로 누적"],
            ["원장님이 상담 기록", "상담 내용·후속 연락일", "학생 이력과 오늘 할 일에 표시"],
        ],
        [43 * mm, 55 * mm, 68 * mm],
    )
    story += [heading2("기준 자료")]
    story += bullets([
        "프로그램 동작의 기준: Git에 저장된 소스코드와 버전 기록",
        "운영 정보의 기준: 애플리케이션 SQLite 데이터베이스와 사진 폴더",
        "설명과 정책의 기준: README, 프로젝트 문서, 필요하면 Obsidian",
        "비밀값의 기준: 운영체제 비밀 저장소 또는 환경 변수. Git·PDF·Obsidian에는 저장하지 않는다.",
    ])
    story += callout("중복 입력 금지", "학생 기본정보는 학생 등록에서 한 번 관리하고, 시간표에서는 등록된 학생을 선택한다. 선생님도 같은 원칙이다. 반 배정은 학생 기본정보가 아니라 실제 수업 시간표에서 정한다.", CREAM, CORAL)
    story.append(page_break())

    story += heading1("3", "설치 전 결정해야 할 것")
    story += [P("프로그램은 Mac, Windows PC, 저렴한 서버용 PC 또는 클라우드에 설치할 수 있다. 다만 운영 형태마다 전원, 외부 접속, 카카오 장치와 백업 방법이 달라진다."), heading2("설치 형태 선택")]
    story += data_table(
        ["형태", "장점", "주의점", "추천 상황"],
        [
            ["원장님 노트북", "가장 단순하고 비용이 적음", "노트북이 꺼지면 외부 접속 불가", "학원 안에서만 먼저 시험"],
            ["학원 서버용 PC", "상시 실행과 카카오 장치 연결에 유리", "전원·인터넷·원격관리 필요", "개인 카카오 장치 기반 송수신"],
            ["클라우드 서버", "외부 접속과 HTTPS 운영에 유리", "월 비용, 보안 설정, 카카오 장치는 별도", "여러 장소·기기에서 상시 접속"],
            ["혼합형", "앱은 클라우드, 카카오는 학원 PC", "서버와 카카오 장치 사이 사설 연결 필요", "외부 접속과 개인 카카오를 함께 사용"],
        ],
        [30 * mm, 45 * mm, 50 * mm, 41 * mm],
    )
    story += [heading2("준비물 체크")]
    story += bullets([
        "학원 또는 원장님 소유의 GitHub 계정과 공개 저장소 주소",
        "실행할 컴퓨터 또는 클라우드 서버와 관리자 권한",
        "외부 접속 시 학원 소유 도메인, DNS 설정 권한, HTTPS 인증서",
        "선생님 카카오 로그인용 Kakao Developers 앱과 Redirect URI",
        "학부모 개인 카톡 발송을 사용할 경우 카카오톡이 로그인된 송수신 장치",
        "데이터와 사진을 별도 위치에 보관할 백업 디스크 또는 백업 저장소",
        "실제 운영 전 사용할 가상 학생·선생님 시험 데이터",
    ])
    story += callout("RAM 8GB도 가능", "이 프로그램 자체는 가벼운 Python·SQLite 웹앱이므로 8GB RAM에서도 운영할 수 있다. 같은 컴퓨터에서 Codex, 카카오톡, 브라우저 탭과 다른 업무 프로그램을 많이 동시에 실행하면 16GB가 더 편하다.")
    story.append(page_break())

    story += heading1("4", "GitHub에서 다운로드하고 시작하기")
    story += [
        P(f"공개 저장소: <b>{REPOSITORY_URL}</b>"),
        heading2("가장 쉬운 방법: Codex에게 설치를 맡기기"),
        P("새 컴퓨터의 Codex에서 이 저장소 주소와 이 문서 마지막 장의 인계 프롬프트를 입력한다. Codex는 운영체제를 확인하고 저장소 다운로드, 필수 환경 설치, 테스트, 원장 비밀번호 등록과 실행 준비를 진행한다."),
        heading2("직접 내려받는 방법"),
    ]
    story += numbered([
        "GitHub 저장소 페이지에서 Code를 누른다.",
        "Download ZIP을 눌러 내려받거나 Git이 설치된 경우 저장소를 clone한다.",
        "ZIP을 사용했다면 영문·숫자 위주의 고정 폴더에 압축을 푼다.",
        "README와 AGENTS.md를 먼저 읽는다. 실제 데이터 폴더를 Git에 올리지 않는다.",
        "테스트를 실행하고 모두 통과한 뒤 시험 서버를 시작한다.",
    ])
    story += [heading2("Windows 설치본")]
    story += numbered([
        "저장소를 내려받은 뒤 프로젝트 폴더의 INSTALL-EASYMATH.cmd를 실행한다.",
        "설치 창이 요구하면 원장 로그인 비밀번호를 직접 두 번 입력한다. 비밀번호를 채팅이나 문서에 적지 않는다.",
        "설치 완료 후 바탕화면의 이지매쓰 학원관리 바로가기를 실행한다.",
        "Windows 로그인 시 서버 자동 시작과 매일 22시 30분 자동 백업이 등록되었는지 확인한다.",
        "시험 데이터를 입력하고 백업 생성·검증·복원까지 시험한다.",
    ])
    story += callout("중요", "현재 공개 소스에는 실제 학원 데이터, 사진, 비밀번호, API 키, 카카오 세션과 백업 파일이 포함되지 않는다. 새 설치는 빈 운영 저장소 또는 프로그램의 가상 시연 데이터로 시작해야 한다.", CREAM, CORAL)
    story.append(page_break())

    story += heading1("5", "첫 실행과 원장님 보안 설정")
    story += [heading2("원장 비밀번호")]
    story += bullets([
        "운영 전 반드시 원장 비밀번호를 등록한다. 서버에는 비밀번호 원문이 아니라 해시만 저장된다.",
        "4자리처럼 짧은 번호는 외부 HTTPS 운영에 적합하지 않다. 실제 운영에서는 충분히 긴 고유 비밀번호를 사용한다.",
        "비밀번호를 PDF, 카카오톡, Git, Obsidian, 소스코드에 기록하지 않는다.",
        "운영 서버는 ACADEMY_REQUIRE_OWNER_LOGIN=1로 원장 로그인을 강제한다.",
    ])
    story += [heading2("첫 실행 확인 순서")]
    story += numbered([
        "원장님 앱 주소를 열어 로그인 화면이 나오는지 확인한다.",
        "로그인 후 원장 현황판과 주간 수업 시간표가 표시되는지 확인한다.",
        "학생·직원 등록 화면에서 시험용 학생 1명과 시험용 선생님 1명을 등록한다.",
        "주간 시간표에 시험 수업을 만들고 두 사람을 배정한다.",
        "선생님 앱에서 본인 수업이 보이는지 확인한다.",
        "등원 앱을 원장님 화면의 1회용 코드로 연결하고 시험 등원을 기록한다.",
        "백업을 만들고 검증한다. 실제 운영 데이터는 검증이 끝난 뒤 입력한다.",
    ])
    story.append(page_break())

    story += heading1("6", "학생 등록과 누적 관리")
    story += [heading2("학생 등록 항목")]
    story += data_table(
        ["항목", "용도", "운영 주의"],
        [
            ["학생 이름", "시간표·출결·평가·상담 식별", "동명이인은 학교·학년으로 구분"],
            ["학생 전화번호", "필수 입력, 뒤 4자리를 등원번호로 사용", "번호 변경 즉시 수정"],
            ["학교·학년", "수업 배정과 상담 참고", "학년 진급 시 갱신"],
            ["보호자·연락처", "피드백·등원 알림 대상", "전송 전 정확한 보호자 확인"],
            ["주소", "필요할 때만 입력", "민감정보이므로 불필요하면 비움"],
            ["재원 상태", "재원·휴원·퇴원 이력", "기록 보존을 위해 삭제보다 상태 변경"],
            ["지도 메모", "수업 운영에 필요한 요약", "과도한 민감정보 기록 금지"],
        ],
        [33 * mm, 74 * mm, 59 * mm],
    )
    story += callout("반은 학생 등록에서 정하지 않는다", "학생 등록은 사람의 기본정보다. 어떤 반의 어떤 수업에 들어가는지는 주간 시간표에서 수업을 만들 때 등록 학생 목록 중 선택한다.")
    story += [heading2("학생 누적 화면에서 확인할 것")]
    story += bullets([
        "수업별 출석·지각·결석·인정결석·보강 기록과 출석률",
        "수업태도·집중도·이해도·진도·참여도·과제 수행 변화",
        "선생님 관찰 메모와 원장님이 보낸 학부모 피드백",
        "상담 내용과 후속 연락 예정일",
        "등원 기록과 주간·월간 리포트",
        "재원·휴원·퇴원 상태 변경 이력",
    ])
    story.append(page_break())

    story += heading1("7", "선생님 등록과 직원 이력")
    story += [heading2("직원 등록 항목")]
    story += bullets([
        "이름, 전화번호, 주소, 이메일 등 기본 연락정보",
        "출신 학교·학과·전공, 경력과 자격 등 이력",
        "고용 형태, 급여 유형·참고 정보",
        "입사일, 퇴사일, 재직 상태",
        "담당 가능 과목과 운영 메모",
    ])
    story += callout("급여 자동 계산 범위", "현재는 승인된 근태와 직원 정보를 급여 계산의 근거로 누적한다. 월급·시급·수업당 급여, 휴게시간, 조퇴·추가근무의 실제 계산 규칙이 확정되기 전에는 자동 급여액을 확정하지 않는다.", CREAM, CORAL)
    story += [heading2("퇴사 처리")]
    story += numbered([
        "선생님 기록을 삭제하지 않고 퇴사일과 재직 상태를 변경한다.",
        "미래 시간표 배정을 확인하고 담당자를 변경한다.",
        "대기 중 근태 요청을 처리한다.",
        "근무 이력과 수업 평가 기록이 그대로 보존되는지 확인한다.",
        "카카오 로그인과 원격 접근 권한을 해제한다.",
    ])
    story.append(page_break())

    story += heading1("8", "주간 수업 시간표")
    story += [P("주간 수업표가 원장님 첫 화면의 중심이다. 월요일부터 일요일까지 모두 표시하며 일요일 보충수업도 등록할 수 있다."), heading2("수업 등록")]
    story += numbered([
        "주간 수업 시간표에서 빈 영역 또는 수업 등록 버튼을 누른다.",
        "요일, 시작·종료 시간, 반 이름, 과목과 수업명을 입력한다.",
        "미리 등록한 선생님을 담당자로 선택한다.",
        "미리 등록한 학생 중 이 수업에 참여할 여러 명을 선택한다.",
        "저장 후 전체 수업표와 해당 선생님·학생 수업표에서 같은 수업이 보이는지 확인한다.",
    ])
    story += [heading2("조회 방식")]
    story += data_table(
        ["보기", "사용 상황", "확인 내용"],
        [
            ["전체 수업표", "원장님이 전체 운영을 조망", "요일별 모든 반과 담당자"],
            ["선생님별", "업무 배정·공강 확인", "선택한 선생님의 수업과 학생"],
            ["학생별", "보호자 문의·시간 조정", "선택한 학생의 주간 수업"],
            ["선생님 앱 주간", "선생님 본인 일정", "로그인한 본인 수업만 표시"],
            ["선생님 앱 월간", "보충·휴일 포함 월 계획", "이전 달·다음 달 이동"],
        ],
        [33 * mm, 57 * mm, 76 * mm],
    )
    story += callout("변경 뒤 확인", "시간표에서 선생님이나 학생을 바꾸면 원장님 전체표만 보지 말고 선생님 앱의 본인 달력과 학생별 수업표까지 확인한다.")
    story.append(page_break())

    story += heading1("9", "선생님 앱과 카카오 로그인")
    story += [P("선생님 앱은 모바일 사용을 우선한 별도 화면이다. 실제 운영에서는 Kakao Developers 앱을 학원 명의로 등록하고, 선생님 카카오 계정을 등록된 직원 기록과 연결해야 한다."), heading2("카카오 로그인 준비")]
    story += numbered([
        "학원 소유 Kakao Developers 계정에서 애플리케이션을 만든다.",
        "웹 플랫폼 도메인과 Redirect URI를 운영 HTTPS 주소로 등록한다.",
        "REST API 키와 필요한 경우 Client Secret을 운영 서버의 비밀 저장소에 넣는다.",
        "서버 환경의 KAKAO_REDIRECT_URI를 등록한 값과 정확히 맞춘다.",
        "시험 선생님 계정으로 로그인하고 등록된 직원 기록과 연결되는지 확인한다.",
        "로그아웃, 세션 만료, 퇴직자 접근 차단을 시험한다.",
    ])
    story += callout("키 보관", "KAKAO_REST_API_KEY, KAKAO_CLIENT_SECRET, 로그인 세션과 쿠키는 GitHub·README·PDF·Obsidian·채팅에 올리지 않는다. Windows 설치본은 제공된 비밀값 등록 스크립트와 운영체제 암호화를 사용한다.", CREAM, CORAL)
    story += [heading2("로그인 후 화면")]
    story += bullets([
        "상단 출퇴근 기록 버튼과 오늘 예정 근무",
        "본인에게 배정된 주간 수업 달력",
        "선택한 수업의 참여 학생 목록",
        "주간 달력 아래 월간 전체 수업 달력",
        "학생별 평가와 출결 입력",
        "근무시간 변경·조퇴·추가근무 요청 상태",
    ])
    story.append(page_break())

    story += heading1("10", "강사 근태와 승인")
    story += [heading2("원장님이 먼저 할 일")]
    story += numbered([
        "선생님별 근무 요일, 예정 출근·퇴근과 휴게시간을 주간 근무계획에 등록한다.",
        "변경된 계약이나 고정 스케줄이 있으면 계획을 갱신한다.",
        "입사일·퇴사일과 재직 상태가 실제 직원 정보와 맞는지 확인한다.",
    ])
    story += [heading2("선생님 요청 종류")]
    story += data_table(
        ["요청", "선생님이 입력", "원장 처리"],
        [
            ["출근", "실제 출근 시각", "예정 시간과 비교 후 승인·반려"],
            ["퇴근", "실제 퇴근 시각", "당일 출근·업무와 함께 확인"],
            ["조퇴", "조퇴 시각과 사유", "급여 규칙과 사실관계 확인"],
            ["추가근무", "추가 시작·종료와 사유", "사전·사후 근거 확인"],
            ["근무시간 변경", "날짜·변경 시간·사유", "횟수 제한 없이 요청별 판단"],
            ["결근", "선생님 요청 항목 아님", "원장님이 직접 확정 기록"],
        ],
        [31 * mm, 64 * mm, 71 * mm],
    )
    story += callout("승인되어야 확정", "선생님이 버튼을 누른 즉시 급여 근거가 되는 것이 아니다. 원장님이 승인한 요청만 확정 근무 이력에 저장된다. 같은 날짜의 승인 대기 요청은 중복 등록을 막지만, 승인 후에는 다시 변경 요청할 수 있다.")
    story += [heading2("매일 원장 확인")]
    story += bullets([
        "오늘 확인할 일의 강사 근태 대기 건수",
        "예정과 실제 시간의 큰 차이",
        "조퇴·추가근무·시간 변경 사유",
        "승인·반려 누락",
        "원장 직접 기록이 필요한 결근",
    ])
    story.append(page_break())

    story += heading1("11", "수업 출결·평가·사진 기록")
    story += [heading2("선생님이 수업 직후 기록")]
    story += numbered([
        "본인 수업 달력에서 수업을 선택하고 학생 명단을 확인한다.",
        "학생별 출석, 지각, 결석, 인정결석, 보강 중 하나를 기록한다.",
        "출석 학생은 수업태도·집중도·이해도·진도·참여도·과제 수행 항목을 빠르게 선택한다.",
        "관찰한 사실과 다음 수업에서 확인할 내용을 몇 문장으로 적는다.",
        "공통 수업 내용과 필요한 사진을 수업 기록에 첨부한다.",
        "저장 후 해당 학생의 평가와 원장님 피드백함에 반영되었는지 확인한다.",
    ])
    story += [heading2("좋은 관찰 메모")]
    story += data_table(
        ["피해야 할 표현", "권장 표현"],
        [
            ["집중을 못함", "연산 10문제 중 6번 이후 주변을 자주 확인해 두 차례 다시 안내함"],
            ["잘했음", "통분 과정을 스스로 설명했고 응용 3문제를 모두 해결함"],
            ["숙제 안 함", "지난 과제 12문제 중 5문제가 미완료라 다음 수업 전 보완하기로 함"],
            ["이해가 느림", "분모가 다른 덧셈에서 공통분모 선택을 어려워해 그림으로 다시 설명함"],
        ],
        [72 * mm, 94 * mm],
    )
    story += callout("결석 처리", "결석·인정결석 학생은 평가 체크리스트를 억지로 작성하지 않고 출결만 저장할 수 있다. 사실이 아닌 평가를 채우지 않는다.", CREAM, CORAL)
    story.append(page_break())

    story += heading1("12", "AI 학부모 피드백 작성")
    story += [P("AI는 선생님 체크리스트와 관찰 메모를 읽기 쉬운 학부모 문안으로 정리한다. AI가 판단하거나 자동 발송하는 구조가 아니라 원장님 검토를 돕는 초안 도구다."), heading2("세 가지 작성 방식")]
    story += data_table(
        ["방식", "설명", "비용·연결"],
        [
            ["template", "외부 AI 없이 정해진 규칙으로 기본 문안 생성", "기본값, 별도 비용 없음"],
            ["codex", "설치 장치에 로그인된 Codex를 비대화형·임시·읽기 전용으로 사용", "장치와 계정 상태에 의존"],
            ["openai", "OpenAI API 모델로 문안 생성", "API 키와 사용량 비용 필요"],
            ["auto", "Codex, API, 기본 문안 순으로 가능한 방식을 시도", "운영 환경 검증 필요"],
        ],
        [28 * mm, 88 * mm, 50 * mm],
    )
    story += [heading2("안전한 작성 순서")]
    story += numbered([
        "선생님 평가와 관찰 메모가 사실에 맞는지 먼저 확인한다.",
        "원장님 화면에서 초안 만들기를 누른다.",
        "학생 이름·수업일·수업 내용·강점·보완점을 확인한다.",
        "과장, 진단, 확정적 표현과 다른 학생 정보가 섞이지 않았는지 확인한다.",
        "원장님이 직접 수정하고 최종 문안을 확정한다.",
        "정확한 학부모 채팅방을 다시 확인한 뒤 전송한다.",
        "발송 결과를 기록한다. 결과가 불명확하면 자동 재전송하지 않는다.",
    ])
    story += callout("개인정보 최소화", "AI 요청에는 학생 이름, 전화번호, 주소를 보내지 않고 수업·평가에 필요한 비식별 내용만 전달하도록 설계되어 있다. 운영자가 프롬프트에 개인정보를 직접 추가하지 않는다.", CREAM, CORAL)
    story.append(page_break())

    story += heading1("13", "카카오톡 연결과 발송")
    story += [P("카카오톡 기능은 두 가지를 구분해야 한다. 선생님 앱의 카카오 로그인은 사용자 인증이고, 학부모에게 개인 카톡을 보내는 송수신기는 별도 연결이다."), heading2("구성 요소")]
    story += data_table(
        ["구성", "목적", "필요한 준비"],
        [
            ["Kakao Developers 로그인", "선생님 본인 인증", "학원 앱, REST 키, Redirect URI"],
            ["메시지 연결기", "채팅방 목록·최근 메시지·발송", "카카오톡 로그인 장치와 호환 드라이버"],
            ["학원 서버 연결 설정", "앱과 연결기 통신", "Connector URL 또는 CLI, 공통 토큰"],
            ["학생별 채팅방 연결", "정확한 수신자 지정", "원장님이 채팅방 제목·보호자를 대조"],
        ],
        [38 * mm, 56 * mm, 72 * mm],
    )
    story += [heading2("개인 카카오톡 송수신기 연결 순서")]
    story += numbered([
        "카카오톡이 로그인된 학원 소유 또는 원장님 관리 장치를 정한다.",
        "같은 장치에 호환 송수신기 드라이버를 설치하거나, 클라우드와 분리된 경우 참조 브리지를 실행한다.",
        "같은 컴퓨터라면 ACADEMY_MESSAGING_CONNECTOR_CLI, 분리된 장치라면 ACADEMY_MESSAGING_CONNECTOR_URL을 설정한다.",
        "분리 연결은 공개 인터넷에 그대로 노출하지 말고 HTTPS 또는 Tailscale 사설망을 사용한다.",
        "원장님 앱의 카톡 연결 관리에서 연결 상태와 채팅방 목록을 확인한다.",
        "학생별로 정확한 학부모 채팅방을 한 번 연결한다. 동명이인과 가족 단체방을 특히 확인한다.",
        "가상 학생·시험 채팅방으로 문안 전송과 최근 메시지 조회를 시험한다.",
        "실제 발송은 원장님 최종 확인 버튼을 거치게 유지한다.",
    ])
    story += callout("현재 공개 소스의 경계", "프로그램에는 메시지 연결 규격과 참조 브리지가 들어 있지만 특정 개인 카카오 계정·컴퓨터·드라이버는 연결되어 있지 않다. 설치 장소가 정해진 뒤 실제 장치용 드라이버를 선택하고 연결해야 한다.", CREAM, CORAL)
    story += [heading2("발송 오류 원칙")]
    story += bullets([
        "status=sent만 명확한 성공으로 기록한다.",
        "status=unknown 또는 네트워크 오류면 자동 재전송하지 않는다.",
        "카카오톡 실제 채팅방에서 발송 여부를 확인한 뒤 수동으로 상태를 정리한다.",
        "같은 문안의 중복 발송을 막기 위해 시간과 결과를 기록한다.",
        "카카오 운영정책과 계정 보호 정책을 확인하고 비정상적인 대량 자동화를 피한다.",
    ])
    story.append(page_break())

    story += heading1("14", "학생 등원 앱")
    story += [P("학생 등원 앱은 태블릿 또는 사용하지 않는 휴대폰에 PWA로 설치해 안내 데스크에 둔다. 기기는 원장님이 만든 10분 유효·1회용 코드로만 연결한다."), heading2("기기 연결")]
    story += numbered([
        "원장님 앱의 학생 등원·리포트 화면에서 새 연결코드를 만든다.",
        "등원 기기에서 /kiosk.html을 열고 코드를 입력한다.",
        "연결된 기기 이름이 원장님 화면에 표시되는지 확인한다.",
        "브라우저의 앱 설치 또는 홈 화면에 추가를 실행한다.",
        "기기를 잃어버리거나 교체하면 원장님 화면에서 즉시 권한을 해제한다.",
    ])
    story += [heading2("학생 등원")]
    story += numbered([
        "학생이 등록 때 입력한 본인 전화번호의 뒤 4자리를 누른다.",
        "한 명만 일치하면 학생 이름을 확인하고 등원한다.",
        "같은 뒤 4자리가 여러 명이면 이름 목록에서 본인을 선택한다.",
        "등원 기록이 먼저 저장되고, 연결된 경우 학부모 카톡 알림을 별도로 시도한다.",
        "2시간 이내 같은 학생의 중복 입력은 한 번만 저장된다.",
    ])
    story += callout("전화번호는 필수", "등원번호는 별도로 만드는 번호가 아니라 학생 등록 때 받은 학생 전화번호의 뒤 4자리다. 번호가 바뀌면 학생 기본정보를 수정한다.")
    story += [heading2("알림이 실패해도 기록은 보존")]
    story += [P("등원 기록 저장과 학부모 알림 전송은 분리되어 있다. 카카오 연결이 잠시 실패해도 학생의 등원 사실은 데이터베이스에 남고, 알림 결과는 성공·실패 상태로 따로 누적된다.")]
    story.append(page_break())

    story += heading1("15", "주간·월간 등원 리포트")
    story += [heading2("원장님 확인 항목")]
    story += bullets([
        "기간 안의 실제 등원일과 예정 수업일",
        "출석 횟수, 미등원 또는 확인이 필요한 날짜",
        "중복 입력 차단 여부와 알림 전송 결과",
        "학생별 생성 문안과 학부모 채팅방 연결 상태",
    ])
    story += [heading2("발행 순서")]
    story += numbered([
        "학생 등원·리포트 화면에서 주간 또는 월간을 선택한다.",
        "기준 날짜를 선택하고 학생별 통계를 확인한다.",
        "예정 수업일과 실제 등원일이 다르면 수업 변경·보강·결석 기록을 함께 확인한다.",
        "자동 생성된 문안을 원장님이 읽고 필요한 설명을 수정한다.",
        "수동 복사 또는 연결된 카카오 채팅방으로 확인 후 전송한다.",
        "발송 결과를 기록하고 학생 누적 화면에서 이력을 확인한다.",
    ])
    story += callout("리포트는 출석부를 대체하지 않는다", "등원기기 입력은 학원 도착 기록이다. 수업별 출석·지각·결석·보강 기록은 선생님 수업 평가 화면에서 별도로 관리한다.", CREAM, CORAL)
    story.append(page_break())

    story += heading1("16", "학부모 상담 기록")
    story += [heading2("기록할 내용")]
    story += bullets([
        "상담 날짜와 상담한 보호자",
        "문의 또는 논의한 핵심 내용",
        "학원에서 확인·조치하기로 한 사항",
        "다시 연락할 날짜와 담당자",
        "후속 연락 완료 여부",
    ])
    story += [heading2("운영 순서")]
    story += numbered([
        "상담 직후 학생을 선택하고 사실 중심으로 요약한다.",
        "약속한 조치와 후속 연락일을 구체적으로 입력한다.",
        "원장 현황판의 상담 후속 건수에서 오늘까지 연락할 대상을 확인한다.",
        "후속 연락을 마치면 결과를 추가하고 완료 처리한다.",
        "민감한 가족사·건강정보는 교육 운영에 꼭 필요한 범위만 기록한다.",
    ])
    story.append(page_break())

    story += heading1("17", "사진 저장과 관리")
    story += [P("수업 사진은 데이터베이스 자체가 아니라 전용 사진 폴더에 원본 파일로 저장되고, 데이터베이스에는 어떤 수업 기록과 연결되는지 저장된다."), heading2("사진 운영 원칙")]
    story += bullets([
        "학부모 동의와 학원 개인정보 처리 기준 안에서만 촬영·보관한다.",
        "학생 이름·전화번호가 파일명에 드러나지 않게 시스템이 만든 저장명을 사용한다.",
        "한 번에 최대 10장, 사진 한 장 15MB 이하, 전체 요청 60MB 이하 기준을 지킨다.",
        "사진 폴더와 데이터베이스는 같은 시점의 백업으로 함께 보존한다.",
        "보관 기간과 삭제 정책을 학원에서 확정하고 정기적으로 점검한다.",
        "사진 URL을 공개하거나 공개 GitHub 저장소에 올리지 않는다.",
    ])
    story += callout("복구 시 주의", "데이터베이스만 복원하고 사진 폴더를 복원하지 않으면 기록에는 사진이 있다고 표시되지만 원본을 열 수 없다. 백업 manifest와 무결성 검증을 함께 사용한다.", CREAM, CORAL)
    story.append(page_break())

    story += heading1("18", "PWA 설치와 온라인 사용")
    story += [heading2("설치 조건")]
    story += bullets([
        "개발 시험: localhost 주소에서도 설치 가능",
        "실제 휴대폰·태블릿·외부 PC: 공개 또는 사설 도메인의 HTTPS 주소 필요",
        "원장·선생님·등원 앱은 같은 서버를 쓰지만 manifest ID와 아이콘이 달라 별도 설치",
        "운영 API와 사진은 서비스 워커 캐시에서 제외",
    ])
    story += [heading2("Android·Windows·Mac")]
    story += numbered([
        "설치할 앱 주소를 Chrome 또는 PWA 설치를 지원하는 브라우저에서 연다.",
        "화면의 앱 설치 버튼이나 브라우저 주소창의 설치 아이콘을 누른다.",
        "앱 이름과 아이콘을 확인하고 설치한다.",
        "설치된 앱을 실행해 로그인·수업·등원 데이터가 서버와 동기화되는지 확인한다.",
    ])
    story += [heading2("iPhone·iPad")]
    story += numbered([
        "Safari에서 원하는 앱 주소를 연다.",
        "공유 버튼을 누르고 홈 화면에 추가를 선택한다.",
        "앱 이름을 확인하고 추가한다.",
        "홈 화면 아이콘으로 실행하고 온라인 상태를 확인한다.",
    ])
    story += callout("인터넷이 끊긴 경우", "화면이 열려 있어도 새 저장·조회는 실패할 수 있다. 인터넷 연결 필요 화면이 보이면 Wi-Fi 또는 모바일 데이터를 복구한 뒤 다시 연결하기를 누른다. 오래된 화면을 근거로 출결·근태를 확정하지 않는다.")
    story.append(page_break())

    story += heading1("19", "외부 HTTPS와 클라우드 배포")
    story += [heading2("클라우드로 해결되는 것")]
    story += bullets([
        "원장·선생님·등원 기기가 어디서든 같은 서버에 접속",
        "도메인·HTTPS를 통한 PWA 설치와 안전한 세션 쿠키",
        "노트북 전원이 꺼져도 앱 서버 상시 운영",
        "서버 데이터와 백업의 중앙 관리",
    ])
    story += [heading2("클라우드가 자동으로 해결하지 않는 것")]
    story += bullets([
        "개인 카카오톡 PC 프로그램을 일반 Linux 클라우드에서 그대로 실행하는 문제",
        "카카오 운영 앱 심사·정책과 실제 로그인 계정 연결",
        "도메인 소유·DNS 설정과 백업 저장소 비용",
        "학원 개인정보 보호 책임과 사진 보관 정책",
    ])
    story += [heading2("권장 혼합 구조")]
    story += numbered([
        "클라우드 서버에 이지매쓰 앱·SQLite 또는 향후 운영 DB를 둔다.",
        "학원 소유 도메인과 Caddy 등 HTTPS 역방향 프록시를 연결한다.",
        "카카오톡이 로그인된 학원 PC에 메시지 브리지와 실제 드라이버를 둔다.",
        "클라우드와 카카오 PC는 HTTPS 또는 Tailscale 사설망으로 연결한다.",
        "백업은 클라우드 서버와 별도 위치에 보관하고 복원 시험을 한다.",
    ])
    story.append(page_break())

    story += heading1("20", "백업과 복구")
    story += [heading2("백업 대상")]
    story += data_table(
        ["대상", "내용", "주의"],
        [
            ["SQLite DB", "학생·직원·시간표·평가·근태·상담·등원·메시지 이력", "온라인 백업 기능 사용"],
            ["사진 폴더", "수업 사진 원본", "DB와 같은 백업 세트로 보관"],
            ["manifest", "파일 목록·크기·해시", "verify 명령으로 무결성 확인"],
            ["환경설정", "비밀이 아닌 운영 설정", "비밀키와 분리"],
            ["소스코드", "GitHub 버전 기록", "운영 데이터는 포함하지 않음"],
        ],
        [32 * mm, 78 * mm, 56 * mm],
    )
    story += [heading2("백업 절차")]
    story += numbered([
        "자동 백업 작업이 예정 시간에 실행되었는지 확인한다.",
        "새 백업 폴더에 DB·사진·manifest가 함께 있는지 확인한다.",
        "backup.py verify로 해시와 파일 누락을 검사한다.",
        "월 1회 이상 시험 위치에 복원해 앱이 실제로 열리는지 확인한다.",
        "보존 기간을 넘긴 백업은 정책에 따라 안전하게 정리한다.",
        "같은 컴퓨터 고장에 대비해 별도 디스크나 다른 서버에도 복사한다.",
    ])
    story += callout("백업 성공과 복구 성공은 다르다", "백업 파일이 만들어졌다는 표시만으로 완료하지 않는다. 시험 복원 후 학생·시간표·사진을 실제로 열 수 있어야 백업 체계가 검증된 것이다.", CREAM, CORAL)
    story.append(page_break())

    story += heading1("21", "개인정보와 보안")
    story += [heading2("절대 공개하지 않을 것")]
    story += bullets([
        "실제 학생·학부모·선생님의 이름, 전화번호, 주소, 급여, 평가와 상담",
        "SQLite 운영 DB, 사진 폴더, 백업 파일",
        "원장 비밀번호와 비밀번호 해시 원본 파일",
        "Kakao REST 키·Client Secret·세션·쿠키",
        "OpenAI API 키, 메시지 연결 토큰, Tailscale 인증키",
        "SSH 개인키와 원격 접속 정보",
    ])
    story += [heading2("운영 보안 체크")]
    story += bullets([
        "공개 GitHub 업로드 전 git status와 비밀 패턴 검사를 수행한다.",
        "외부 운영은 HTTPS와 원장 로그인을 강제한다.",
        "교사·등원 기기는 필요한 권한만 부여하고 퇴직·분실 시 즉시 해제한다.",
        "카카오 연결기는 공개 포트보다 HTTPS 또는 Tailscale 사설망을 사용한다.",
        "사진과 백업 폴더의 운영체제 접근 권한을 제한한다.",
        "운영 로그에 비밀번호·토큰·전체 개인정보가 찍히지 않게 한다.",
    ])
    story.append(page_break())

    story += heading1("22", "원장님 일일·주간·월간 업무")
    story += [heading2("매일")]
    story += bullets([
        "첫 화면에서 미작성 수업, 오늘 피드백, 근태 승인, 상담 후속, 등원 현황을 확인한다.",
        "선생님 수업 평가와 출결이 사실에 맞게 입력되었는지 확인한다.",
        "AI 학부모 문안을 만들고 원장님이 직접 수정·확정한다.",
        "카카오 수신자와 문안을 확인한 뒤 전송하고 결과를 기록한다.",
        "근태 요청을 승인 또는 반려하고 누락된 결근은 원장이 기록한다.",
        "당일 백업 오류나 카카오 연결 오류를 확인한다.",
    ])
    story += [heading2("매주")]
    story += bullets([
        "학생별 주간 수업·평가·출결을 모아 학부모 피드백을 검토한다.",
        "주간 등원 리포트와 예정 수업 대비 누락을 확인한다.",
        "다음 주 시간표와 선생님 근무계획을 확인한다.",
        "상담 후속 연락과 미완료 업무를 정리한다.",
        "백업 검증 결과를 확인한다.",
    ])
    story += [heading2("매월")]
    story += bullets([
        "학생별 월간 등원·출석·평가 흐름을 검토한다.",
        "선생님별 승인 근무·조퇴·추가근무·결근 이력을 확인한다.",
        "휴원·퇴원·입사·퇴사 상태를 갱신한다.",
        "사진·백업 보관 용량과 복원 시험을 점검한다.",
        "프로그램 업데이트와 보안 설정 변경을 Git 기록과 문서에 남긴다.",
    ])
    story.append(page_break())

    story += heading1("23", "문제 해결")
    story += data_table(
        ["증상", "먼저 확인", "다음 조치"],
        [
            ["127.0.0.1 연결 실패", "서버가 해당 컴퓨터에서 실행 중인지", "Start 스크립트·포트 49321·로그 확인"],
            ["다른 기기에서 접속 안 됨", "localhost 주소를 사용했는지", "서버 주소·방화벽·도메인·HTTPS 확인"],
            ["PWA 설치 버튼 없음", "HTTPS 또는 localhost, 지원 브라우저", "iOS는 Safari 공유 > 홈 화면에 추가"],
            ["선생님 카카오 로그인 실패", "키·Redirect URI·HTTPS", "Kakao Developers 등록값과 정확히 비교"],
            ["본인 수업이 안 보임", "시간표 담당 선생님 배정", "등록 직원과 로그인 계정 연결 확인"],
            ["등원번호가 안 맞음", "학생 전화번호 필수값", "전화번호 수정 후 뒤 4자리 재확인"],
            ["동일 뒤 4자리", "이름 목록 표시 여부", "학생이 본인 이름 선택"],
            ["카톡 전송 상태 불명", "실제 채팅방 발송 여부", "자동 재전송 금지, 직접 확인"],
            ["사진이 안 열림", "사진 폴더와 DB 연결", "같은 백업 세트로 복원"],
            ["AI 초안 실패", "Provider·Codex 로그인·API 키", "template 기본 문안으로 안전 대체"],
            ["근태가 확정되지 않음", "원장 승인 여부", "대기 요청 승인·반려 처리"],
            ["업데이트 후 오류", "테스트 결과와 Git diff", "운영 데이터 보존 후 이전 버전 복구"],
        ],
        [42 * mm, 58 * mm, 66 * mm],
    )
    story.append(page_break())

    story += heading1("24", "Codex로 수정하고 업데이트하기")
    story += [P("Codex는 프로젝트 루트의 AGENTS.md를 먼저 읽고 그 규칙에 따라 작업한다. 요청은 코딩 용어보다 학원 업무와 기대 결과로 설명하는 것이 좋다."), heading2("좋은 요청 예시")]
    story += callout("기능 변경", "학생 평가 화면에 숙제 완료 여부를 추가해줘. 기존 학생 기록과 운영 데이터는 보존하고, 시험 데이터로 주요 흐름을 검증한 뒤 변경 파일과 결과를 설명해줘.")
    story += callout("오류 진단", "선생님 앱에서 오늘 수업이 보이지 않아. 원인을 먼저 확인하고 설명해줘. 운영 데이터는 수정하지 말고 재현과 읽기 전용 점검부터 해줘.", CREAM, CORAL)
    story += [heading2("안전한 수정 순서")]
    story += numbered([
        "Codex에서 정확한 프로젝트 폴더를 연다.",
        "AGENTS.md, PROJECT_CONTEXT.md, README와 관련 코드를 읽게 한다.",
        "운영 데이터가 아니라 시험 데이터와 별도 작업 브랜치에서 변경한다.",
        "자동 테스트와 실제 핵심 화면 흐름을 함께 확인한다.",
        "원장님이 사용 시나리오로 검토한다.",
        "Git commit을 남기고 공개 저장소에 push한다.",
        "운영 환경에서 백업 후 git pull 또는 검증된 배포본으로 갱신한다.",
        "변경된 사용법과 알려진 문제를 문서에 기록한다.",
    ])
    story += callout("Codex 계정과 앱 AI는 별개", "개발용 Codex 로그인은 소스 수정과 설치 지원에 사용할 수 있다. 프로그램 안에서 자동으로 학부모 문안을 만들 때 Codex 방식 또는 OpenAI API 방식을 별도로 선택한다. 공개 저장소에 인증 파일을 넣지 않는다.", CREAM, CORAL)
    story.append(page_break())

    story += heading1("25", "환경 변수 참고표")
    story += data_table(
        ["이름", "역할", "비밀 여부"],
        [
            ["ACADEMY_HOST", "서버가 수신할 주소", "아님"],
            ["ACADEMY_PORT", "기본 49321", "아님"],
            ["ACADEMY_DB_PATH", "SQLite DB 경로", "경로 보호"],
            ["ACADEMY_PHOTO_PATH", "사진 폴더", "경로 보호"],
            ["ACADEMY_BACKUP_PATH", "백업 폴더", "경로 보호"],
            ["ACADEMY_REQUIRE_OWNER_LOGIN", "원장 로그인 강제", "아님"],
            ["ACADEMY_HTTPS", "Secure 쿠키 등 HTTPS 운영", "아님"],
            ["KAKAO_REST_API_KEY", "선생님 카카오 로그인", "비밀"],
            ["KAKAO_CLIENT_SECRET", "카카오 앱 추가 보호", "비밀"],
            ["KAKAO_REDIRECT_URI", "카카오 로그인 반환 주소", "아님"],
            ["ACADEMY_FEEDBACK_AI_PROVIDER", "template·codex·openai·auto", "아님"],
            ["OPENAI_API_KEY", "OpenAI API 방식 인증", "비밀"],
            ["OPENAI_FEEDBACK_MODEL", "피드백 API 모델", "아님"],
            ["ACADEMY_MESSAGING_CONNECTOR_URL", "분리된 메시지 브리지 주소", "주소 보호"],
            ["ACADEMY_MESSAGING_CONNECTOR_CLI", "같은 장치의 송수신기 CLI", "경로 보호"],
            ["ACADEMY_MESSAGING_CONNECTOR_TOKEN", "메시지 브리지 인증", "비밀"],
        ],
        [58 * mm, 76 * mm, 32 * mm],
    )
    story += callout("환경 변수 원칙", ".env.example에는 항목 이름과 예시만 둔다. 실제 비밀값은 운영체제 비밀 저장소·보안 프롬프트·배포 플랫폼 Secrets에서 주입한다.", CREAM, CORAL)
    story.append(page_break())

    story += heading1("26", "실제 운영 전 최종 점검표")
    story += [heading2("설치·접속")]
    story += bullets([
        "[ ] 운영 서버와 자동 시작이 재부팅 후에도 정상이다.",
        "[ ] 학원 도메인과 HTTPS 인증서가 정상이다.",
        "[ ] 원장·선생님·등원 앱을 각 기기에 PWA로 설치했다.",
        "[ ] 원장 로그인과 세션 만료를 확인했다.",
    ])
    story += [heading2("업무 흐름")]
    story += bullets([
        "[ ] 학생·선생님 등록부터 시간표 배정까지 시험했다.",
        "[ ] 선생님 로그인 후 본인 주간·월간 수업을 확인했다.",
        "[ ] 출결·평가·사진 기록과 학생 누적 화면을 확인했다.",
        "[ ] 출근·퇴근·조퇴·추가근무·근무변경 승인과 결근 직접 기록을 확인했다.",
        "[ ] 등원번호 중복 선택과 2시간 중복 방지를 확인했다.",
        "[ ] 주간·월간 등원 리포트와 상담 후속을 확인했다.",
    ])
    story += [heading2("카카오·AI")]
    story += bullets([
        "[ ] Kakao Developers의 도메인·Redirect URI·키를 운영 서버와 맞췄다.",
        "[ ] 메시지 송수신기 상태와 시험 채팅방 전송을 확인했다.",
        "[ ] 학생별 학부모 채팅방을 정확히 연결했다.",
        "[ ] AI 초안 실패 시 template 대체가 되는지 확인했다.",
        "[ ] 모든 실제 발송은 원장 최종 확인 뒤 이루어진다.",
    ])
    story += [heading2("백업·보안")]
    story += bullets([
        "[ ] 실제 데이터·사진·비밀값이 공개 GitHub에 없음을 확인했다.",
        "[ ] DB와 사진 자동 백업·무결성 검증을 확인했다.",
        "[ ] 시험 위치에서 복원 후 실제 화면을 열었다.",
        "[ ] 퇴직자·분실 기기의 권한 해제 절차를 확인했다.",
        "[ ] 개인정보·사진 보관 기간과 학부모 동의 절차를 확정했다.",
    ])
    story.append(page_break())

    story += heading1("27", "지원·변경 이력 기록 방법")
    story += [P("오류나 개선 요청을 남길 때는 실제 개인정보를 제외하고 재현 가능한 정보만 기록한다."), heading2("Codex 또는 개발자에게 전달할 정보")]
    story += bullets([
        "어느 앱인지: 원장·선생님·등원",
        "어느 화면과 어떤 버튼인지",
        "기대한 결과와 실제 결과",
        "오류가 발생한 대략적인 시간",
        "재현에 필요한 가상 데이터와 단계",
        "브라우저·운영체제·배포 버전",
        "비밀값과 개인정보를 가린 로그",
    ])
    story += callout("남기지 않을 것", "실제 카카오 대화, 전체 전화번호, 주소, 급여, 학생 평가, 비밀번호, 쿠키, 토큰, API 키와 운영 DB 파일은 공개 이슈나 Codex 프롬프트에 첨부하지 않는다.", CREAM, CORAL)
    story += [heading2("버전 기록")]
    story += bullets([
        "기능 변경은 Git commit으로 복구 가능한 지점을 만든다.",
        "README의 현재 기능과 설치 조건을 함께 갱신한다.",
        "DB 구조가 바뀌면 백업과 마이그레이션 시험 결과를 기록한다.",
        "운영 반영 날짜와 담당자, 검증 결과를 별도 운영 기록에 남긴다.",
    ])
    story.append(page_break())

    story += heading1("28", "빠른 참조")
    story += data_table(
        ["하려는 일", "어디에서", "핵심 주의"],
        [
            ["학생·선생님 등록", "원장님 앱 > 학생·직원 등록", "반 배정은 시간표에서"],
            ["수업 배정", "원장님 앱 > 주간 수업 시간표", "등록 명단에서 선택"],
            ["학생 평가", "선생님 앱 > 본인 수업", "사실 중심 관찰"],
            ["학부모 문안", "원장님 앱 > 오늘/주간 피드백", "AI 초안 후 직접 수정"],
            ["카톡 발송", "원장님 앱 > 연결된 학생 카드", "수신자 확인, 자동 재전송 금지"],
            ["근태 요청", "선생님 앱 상단 출퇴근", "원장 승인 전 대기"],
            ["근태 확정", "원장님 앱 > 강사 출퇴근", "승인·반려, 결근은 원장 기록"],
            ["등원", "학생 등원 앱", "학생 번호 뒤 4자리"],
            ["등원 리포트", "원장님 앱 > 학생 등원·리포트", "예정 수업과 함께 확인"],
            ["상담 후속", "원장님 앱 > 학부모 상담", "날짜·담당·결과 기록"],
            ["백업 확인", "서버 백업 폴더·backup.py", "검증과 복원까지"],
            ["기능 수정", "Codex에서 프로젝트 열기", "AGENTS.md와 테스트 우선"],
        ],
        [46 * mm, 67 * mm, 53 * mm],
    )
    story += [
        Spacer(1, 8 * mm),
        callout("마지막 원칙", "이 시스템의 목적은 입력을 늘리는 것이 아니라, 학생·선생님·수업·근태·상담 정보를 한 번 정확히 기록하고 필요한 사람에게 안전하게 연결하는 것이다. 자동 생성과 자동 연결보다 원장님의 최종 확인을 우선한다.")[0],
    ]
    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = ManualDocTemplate(
        str(OUTPUT), pagesize=A4,
        rightMargin=22 * mm, leftMargin=22 * mm,
        topMargin=22 * mm, bottomMargin=21 * mm,
        title="이지매쓰 학원관리 시스템 상세 사용자·설치·운영 매뉴얼",
        author="EasyMath Academy",
        subject="설치, 기능, 카카오 연결, PWA, 백업 및 운영 안내",
    )
    story = build_story()

    def first_page(canvas, doc):
        cover(canvas, doc)

    doc.multiBuild(story, onFirstPage=first_page, onLaterPages=regular_page)
    print(OUTPUT)


if __name__ == "__main__":
    main()
