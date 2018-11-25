# -*- coding: utf-8 -*-
import sys
import os
import datetime
import xlwt
import xlrd
import math

settings = {"models_order": ["BR", "ETA", "BRAMS", "BAM", "GFS", "GEP01",
            "GEP02", "GEP03", "GEP04", "GEP06", "GEP07", "GEP08", "GEP09",
            "GEP10", "GEP11", "GEP12", "GEP13", "GEP14", "GEP15", "GEP16",
            " GEP17", "GEP18", "GEP19", "GEP20", "SSEOP01", "SSEOP02"],
            "ensemble_log_name": ["Ensemble_Relatorio_%Y%m%d%H.log"],
            "ensemble_log_directory": ["/dados/reverton/gera_ensemble_v2_new/logs/"],
            "ensemble_report_directory": ["/dados/reverton/gera_ensemble_v2_new/logs2/"],
            "ensemble_report_name": ["ensemble_%d_%m_%Y_%H_log.xls"]}


class WriteSheet():

    def __init__(self, file_name, settings):

        self.settings = settings

        self.file_name = file_name
        self.file = xlwt.Workbook()

        self.font_name = 'Times New Roman'
        self.font_color = 'black'
        self.font_bold = 'off'
        self.font_italic = 'off'

        self.font_wrap = 'off'
        self.font_vertical_alignment = 'centre'
        self.font_horizontal_alignment = 'left'

        self.cell_fill = 'pattern solid'
        self.cell_color = 'fore_colour cinza'

        # Options: '', thick, thin, double, dashed
        self.cell_top_border = 'top thin'
        self.cell_bottom_border = 'bottom thin'
        self.cell_left_border = 'left thin'
        self.cell_right_border = 'right thin'

        self.factor = 700

    def add_sheet(self, sheet="Planilha 1"):

        self.sheet = self.file.add_sheet(sheet)

    def new_colors(self):

        # Adiciona cor verde
        xlwt.add_palette_colour("verde", 0x21)
        self.file.set_colour_RGB(0x21, 0, 107, 84)

        # Adiciona cor cinza
        xlwt.add_palette_colour("cinza", 0x22)
        self.file.set_colour_RGB(0x22, 240, 240, 240)

        xlwt.add_palette_colour("cinza_escuro", 0x23)
        self.file.set_colour_RGB(0x23, 200, 200, 200)

        # Adiciona cor verde para vento
        xlwt.add_palette_colour("verde_vento", 0x24)
        self.file.set_colour_RGB(0x24, 0, 255, 0)

        # Adiciona cor amarelo para vento
        xlwt.add_palette_colour("amarelo_vento", 0x25)
        self.file.set_colour_RGB(0x25, 255, 255, 0)

        # Adiciona cor vermelho para vento
        xlwt.add_palette_colour("vermelho_vento", 0x26)
        self.file.set_colour_RGB(0x26, 255, 0, 0)

        self.default_style = xlwt.easyxf(
            'font: name %s, color-index %s, bold %s, italic %s; ' %
            (self.font_name,
             self.font_color,
             self.font_bold,
             self.font_italic) + 'align: wrap %s, vert %s, horiz %s;' %
            (self.font_wrap, self.font_vertical_alignment,
             self.font_horizontal_alignment) +
            'pattern: ' + self.cell_fill + ',' + self.cell_color + ';' +
            'borders: ' + self.cell_top_border + "," +
            self.cell_bottom_border + "," +
            self.cell_left_border + "," +
            self.cell_right_border + ';')

    def build_style(self):

        self.style = xlwt.easyxf(
            'font: name %s, color-index %s, bold %s, italic %s; ' %
            (self.font_name,
             self.font_color,
             self.font_bold,
             self.font_italic) + 'align: wrap %s, vert %s, horiz %s;' %
            (self.font_wrap, self.font_vertical_alignment,
             self.font_horizontal_alignment) +
            'pattern: ' + self.cell_fill + ',' + self.cell_color + ';' +
            'borders: ' + self.cell_top_border + "," +
            self.cell_bottom_border + "," +
            self.cell_left_border + "," +
            self.cell_right_border + ';')

    def write_log_v1(self, forecast_dates):

        dates = list(forecast_dates.keys())
        dates.sort()

        models = self.settings["models_order"]
        if self.settings["models_order"][0] == "--":
            models = self.settings["models"]

        line = 0
        for date in dates:

            runs = forecast_dates[date][2]
            runs.sort()

            self.sheet.write(line, 0, "Data", self.default_style)

            self.font_bold = 'on'
            self.font_horizontal_alignment = 'centre'
            self.build_style()

            self.sheet.write(line, 1, date.strftime("%d/%m/%Y %H"), self.style)
            self.sheet.write_merge(line,
                                   line,
                                   3,
                                   4,
                                   "Numero de membros", self.default_style)

            self.font_bold = 'on'
            self.font_horizontal_alignment = 'centre'
            self.build_style()

            self.sheet.write(line, 5, forecast_dates[date][1], self.style)

            self.font_bold = 'off'
            self.font_horizontal_alignment = 'centre'
            self.build_style()

            line = line + 1

            self.sheet.write_merge(line, line,
                                   0,
                                   len(runs),
                                   "Membros / Rodadas", self.style)

            line = line + 1

            self.font_bold = 'off'
            self.font_horizontal_alignment = 'centre'
            self.build_style()

            for model in models:

                self.sheet.write(line, 0, model, self.style)

                for run, c in zip(runs, range(1, len(runs) + 1)):

                    if model in forecast_dates[date][0].keys():
                        if run in forecast_dates[date][0][model]:
                            self.sheet.write(line,
                                             c,
                                             run.strftime("%d/%m/%Y %H"),
                                             self.style)
                        else:
                            self.sheet.write(line, c, "", self.style)
                    else:
                        self.sheet.write(line, c, "", self.style)

                line = line + 1

            line = line + 2

    def save_file(self):

        self.file.save(self.file_name)

    def fit_columns(self):

        original_sheet = xlrd.open_workbook(self.file_name).sheet_by_index(0)

        for column in range(original_sheet.ncols):

            self.sheet.col(column).width = 0

            for line in range(original_sheet.nrows):
                needed_width = (
                    len(str(original_sheet.cell(line, column).value)) *
                    int(math.ceil(2962 / 13)))
                if self.sheet.col(column).width < needed_width:
                    if len(str(original_sheet.cell(line, column).value)) > 10:
                        self.factor = -self.factor
                    self.sheet.col(column).width = needed_width + self.factor

        self.file.save(self.file_name)


def log_v1(sheet_name, settings, forecast_dates):

    sheet = WriteSheet(sheet_name, settings)
    sheet.new_colors()
    sheet.add_sheet()
    sheet.write_log_v1(forecast_dates)
    sheet.save_file()
    sheet.fit_columns()


def new_logs(main_run, settings, logs):

    forecast_dates = {}
    for l in logs:

        date = datetime.datetime.strptime(l.split()[1], "%Y%m%d%H")

        runs = []
        models = {}

        for el in l.split()[4:]:

            run = datetime.datetime.strptime(el[-10:], "%Y%m%d%H")
            model = el[:-11]
            if run not in runs:
                runs.append(run)

            if model in models.keys():
                models[model].append(run)
            else:
                models[model] = [run]

        forecast_dates[date] = [models, len(l.split()[4:]), runs]

    sheet_name = (settings["ensemble_report_directory"][0] +
                  main_run.strftime(settings["ensemble_report_name"][0]))
    log_v1(sheet_name, settings, forecast_dates)


def main(settings=settings):

    run = settings["run"][0]
    arq_name = run.strftime(settings["ensemble_log_directory"][0] +
                            settings["ensemble_log_name"][0])

    if os.path.exists(arq_name):
        arq = open(arq_name)
        logs = arq.readlines()
        arq.close()

        new_logs(run, settings, logs)

    else:
        print("Log file %s not founded" % arq_name)
        exit()

if __name__ == '__main__':
    run = datetime.strptime(sys.argrv[1], "%Y%m%d%H")
    settings["run"] = [run]
    main(settings)
