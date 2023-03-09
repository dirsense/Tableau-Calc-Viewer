from tableaudocumentapi import Workbook
from tableaudocumentapi.field import Field
import re

class TabDocument():
    blend_square_pettern = '\[[^\]]+\]\.\[[^\]]+\]'
    inner_square_pattern = '(?<=\[).+?(?=\])'

    def __init__(self, twbpath: str):
        self.twbx = Workbook(twbpath)
        self.pid_pcap = {}
        self.pcap_pid = {}
        self.dsid_dscap = {}
        self.dscap_dsid = {}
        self.fid_fcap = {}
        self.fcap_field: dict[str, dict[str, Field]] = {}

        self.create_field_dict()

    def create_field_dict(self):
        for datasource in self.twbx.datasources:
            if datasource.name == 'Parameters':
                for k, v in datasource.fields.items():
                    f: Field = v
                    pcap = '[' + str(f.caption) + ']'
                    self.pid_pcap[k] = pcap
                    self.pcap_pid[pcap] = k
                continue

            dsid = '[' + datasource.name + ']'
            dscap = '[' + datasource.caption + ']'
            dscap = dsid if dscap == '[]' else dscap
            self.dsid_dscap[dsid] = dscap
            self.dscap_dsid[dscap] = dsid
            fid_fcap = {}
            fcap_field = {}

            for field in datasource.fields.values():
                f: Field = field
                if str(f.id).startswith(('[パラメーター', '[Parameter', '[Parámetro', '[Paramètre', '[Parâmetro', '[参数', '[參數', '[매개 변수')):
                    continue

                if f.caption is None:
                    fcap = str(f.id)
                else:
                    fcap = '[' + str(f.caption) + ']'
                
                fid_fcap[f.id] = fcap
                fcap_field[fcap] = f

            self.fid_fcap[dsid] = fid_fcap
            self.fcap_field[dscap] = fcap_field

    def replace_calc_field_id_to_caption(self, formula: str, primary_dsid: str):
        square_ptn = '\[.+?\]'

        blend_tmp_names = []
        blend_target_ids = []
        blend_captions = []

        ### -------------------------------------------------------------------------
        # Blend or Parameter fields are replaced with a temporary string first.
        count = 0
        for rf in re.findall(self.blend_square_pettern, formula):
            if rf in blend_target_ids:
                continue

            ids = re.findall(square_ptn, rf)
            dsid = ids[0]
            fid = ids[1]
            caption = ''
            if dsid in self.dsid_dscap:
                dcap = self.dsid_dscap[dsid]
                if fid in self.fid_fcap[dsid]:
                    caption = dcap + '.' + self.fid_fcap[dsid][fid]
            elif dsid == '[Parameters]':
                if fid in self.pid_pcap:
                    caption = self.pid_pcap[fid]

            if caption != '':
                blend_target_ids.append(rf)
                blend_tmp_names.append('blend-replace-' + str(count))
                blend_captions.append(caption)
                count += 1

        for count, id in enumerate(blend_target_ids):
            formula = formula.replace(id, blend_tmp_names[count])
        ### -------------------------------------------------------------------------

        # Replace primary fields other than Blend or Parameter with ID -> Caption
        fml = formula
        for id in re.findall(square_ptn, fml):
            fdict = self.fid_fcap[primary_dsid]
            if id in fdict:
                formula = formula.replace(id, fdict[id])

        # Replace temporary string -> Caption only when there is a Blend or Parameter field
        for count, tmp in enumerate(blend_tmp_names):
            formula = formula.replace(tmp, blend_captions[count])

        return formula