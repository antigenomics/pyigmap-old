import os
from .globals import CAT_CMD, VIDJIL_CMD, VIDJIL_DATA_PATH, CORES


class VidjilWrapper:
    def __init__(self,
                 germline='homo-sapiens',
                 rnaseq=True,
                 cores=CORES,
                 n=-1):
        if os.path.isfile(germline):
            self.germline_path = germline
        else:
            self.germline_path = f'{VIDJIL_DATA_PATH}/{germline}.g'
        self.vidjil_cmd = f'{VIDJIL_CMD} -g {self.germline_path}'
        if rnaseq:
            self.vidjil_cmd = self.vidjil_cmd + ' -U'
        self.cores = cores
        self.n = n

    def detect_cmd(self,
                   input,
                   output):
        input_cmd = CAT_CMD(input)
        if self.n > 0:
            input_cmd = f'{input_cmd} | head -n {self.n * 4}'
        chunk_placeholder = '_p{#}'
        process_cmd = f'{self.vidjil_cmd} -c detect -o {output} -b {chunk_placeholder} -'
        return f'{input_cmd} | parallel -j {self.cores} --pipe -L 4 --round-robin "{process_cmd}"'

    def clones_cmd(self,
                   input,
                   output):
        input_cmd = CAT_CMD(input)
        return f'{input_cmd} | {self.vidjil_cmd} -c clones --all -o {output} -b result -'

    def run_cmd(self,
                input,
                output):
        return f'{self.detect_cmd(input, output)} && ' + \
            f'{self.clones_cmd(output + "/_p*.fa", output)} && ' + \
            f'rm -r {output}/_p*'