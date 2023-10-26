import io
import os

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, A3, A2, A1, A0, B0, landscape
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus.tables import TableStyle
from reportlab.platypus import PageBreak
from reportlab.lib.units import inch
from reportlab.lib.units import mm

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from polls.models import Polls

fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

pdfmetrics.registerFont(TTFont('OpenSans', os.path.join(fonts_dir, 'OpenSansRegular.ttf')))
pdfmetrics.registerFont(TTFont('OpenSansB', os.path.join(fonts_dir, 'OpenSansBold.ttf')))

PAGE_SIZE = A4
RIGHT_MARGIN = 15
LEFT_MARGIN = 15
TOP_MARGIN = 35
BOTTOM_MARGIN = 55


def get_simple_doc_template(is_landscape=False, default_page_size=PAGE_SIZE):
    buffer = io.BytesIO()

    page_size = default_page_size

    if is_landscape:
        page_size = landscape(page_size)

    return buffer, SimpleDocTemplate(buffer,
                                     rightMargin=RIGHT_MARGIN,
                                     leftMargin=LEFT_MARGIN,
                                     topMargin=TOP_MARGIN,
                                     bottomMargin=BOTTOM_MARGIN,
                                     pagesize=page_size)


def get_sample_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PageHeader', fontName='OpenSansB', alignment=TA_CENTER, spaceAfter=15,
                              fontSize=14))
    styles.add(ParagraphStyle(name='EachPageHeader', fontName='OpenSans', alignment=TA_CENTER, spaceAfter=15,
                              fontSize=10))
    styles.add(ParagraphStyle(name='TableHeader', fontName='OpenSansB', alignment=TA_CENTER, spaceAfter=10,
                              spaceBefore=10))
    styles.add(ParagraphStyle(name='TableCell', alignment=TA_CENTER, fontSize=8))
    styles.add(ParagraphStyle(name='TableHeading', fontName='OpenSansB', alignment=TA_CENTER, fontSize=7))
    return styles


def get_table_styles():
    table_styles = TableStyle([('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                               ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                               ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
                               ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
                               # ('FONTNAME', (0, 0), (-1, -1), 'OpenSansB'),
                               # ('FONTNAME', (0, 1), (-1, -1), 'OpenSans')
                               ])
    table_styles.add('BACKGROUND', (0, 0), (-1, -1), '#ecf4fa')
    table_styles.add('BACKGROUND', (0, 1), (-1, -1), colors.white)
    return table_styles


class NumberedCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(205 * mm, 15 * mm + (0.2 * inch),
                             "Page %d of %d" % (self._pageNumber, page_count))


class MakePdf:

    @staticmethod
    def _header_footer(canvas_instance, doc):
        # Save the state of our canvas so we can draw on it
        canvas_instance.saveState()
        styles = get_sample_styles()

        # Header
        header = Paragraph('This is a multi-line header.  It goes on every page.', styles['EachPageHeader'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas_instance, doc.leftMargin, doc.height + doc.topMargin - h)

        # Footer
        footer = Paragraph('This is a multi-line footer.  It goes on every page.', styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas_instance, doc.leftMargin, h)

        # Release the canvas
        canvas_instance.restoreState()

    @staticmethod
    def print_pdf():
        buffer, doc = get_simple_doc_template()

        elements = []
        styles = get_sample_styles()

        polls = Polls.objects.all()
        elements.append(Paragraph('Polls', styles['PageHeader']))
        table_data = [[Paragraph('id', styles['TableHeading']),
                       Paragraph('name', styles['TableHeading']),
                       Paragraph('question', styles['TableHeading']),
                       Paragraph('choice', styles['TableHeading']),
                       Paragraph('votes', styles['TableHeading'])]]

        for poll in polls:
            table_data.append([Paragraph(str(poll.id), styles['TableCell']),
                               Paragraph(poll.name, styles['TableCell']),
                               Paragraph(poll.question, styles['TableCell']),
                               Paragraph(poll.choice, styles['TableCell']),
                               Paragraph(str(poll.votes), styles['TableCell'])])

        table = Table(table_data, colWidths=[doc.width / 5.0] * 5, repeatRows=1)

        tbl_style = get_table_styles()
        table.setStyle(tbl_style)

        elements.append(table)
        doc.build(elements, onFirstPage=MakePdf._header_footer, onLaterPages=MakePdf._header_footer,
                  canvasmaker=NumberedCanvas)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
