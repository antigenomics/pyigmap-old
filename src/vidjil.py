from collections import namedtuple
from sys import platform
from shutil import which

if platform == 'linux' or platform == 'linux2':
    zcat_cmd = 'zcat'
elif platform == 'darwin':
    zcat_cmd = 'gzcat'
elif platform == 'win32':
    raise 'Cannot run pipe on Windows'
if not which('parallel'):
    raise 'Requires GNU Parallel to work'


PipelineCmd = namedtuple('PipelineCmd', 'input output cmd')


class VidjilTask:
    def __init__(self,
                 species: str = 'homo-sapiens',
                 cores: int = 4,
                 vidjil_path: str = '~/vidjil',
                 germline_path: str = None,
                 first_reads: int = -1) -> None:
        self.vidjil_cmd = vidjil_path + '/vidjil-algo'
        if not germline_path:
            germline_path = vidjil_path + '/germline'
        self.germline_path = germline_path + '/' + species + '.g'
        self.cores = cores
        self.first_reads = first_reads

    def vidjil_pre_cmd(self,
                       output_path,
                       chunk_id: str = '{#}') -> str:
        return f'{self.vidjil_cmd} -c detect -g {self.germline_path} ' + \
            f'-U -o {output_path} -b c{chunk_id} -'

    def vidjil_post_cmd(self,
                        output_path: str,
                        sample_name: str = 'clonotypes') -> str:
        return f'{self.vidjil_cmd} -c clones -g {self.germline_path} ' + \
            f'--all -U -o {output_path} -b {sample_name} -'

    def fastq_cmd(self,
                  input_path: str | list[str]) -> str:
        if input_path.endswith('gz'):
            cat_cmd = zcat_cmd
        else:
            cat_cmd = 'cat'
        if isinstance(input_path, list):
            input_path = " ".join(input_path)
        cmd = f'{cat_cmd} {input_path}'
        if self.first_reads > 0:
            cmd = f'{cmd} | head -n {self.first_reads}'
        return cmd

    def parallel_cmd(self,
                     input_path: str,
                     output_path: str) -> str:
        input_cmd = self.fastq_cmd(input_path=input_path)
        process_cmd = self.vidjil_pre_cmd(result_path=output_path)
        return f'{input_cmd} | parallel -j {self.cores} --pipe -L 4 --round-robin "{process_cmd}"'

    def pipeline_pre_cmd(self,
                         input_path: str | list[str],
                         output_path: str) -> PipelineCmd:
        if not isinstance(input_path, list):
            input_path = [input_path]
        return PipelineCmd(input=input_path,
                           output=[
                               f'{output_path}/{c}.detected.vdj.fa' for c in range(1, self.cores + 1)],
                           cmd=self.parallel_cmd(input_path=input_path,
                                                 output_path=output_path))

    def pipeline_post_cmd(self,
                          input_path: str | list[str],
                          output_path: str,
                          sample_name: str = 'clonotypes') -> PipelineCmd:
        if not input_path:
            input_path = output_path + '/*.fa'
            input_path_0 = [input_path]
        if isinstance(input_path, list):
            input_path_0 = input_path
            input_path = ' '.join(input_path)
        return PipelineCmd(input=input_path_0,
                           output=output_path + '/' + sample_name + '.tsv',
                           cmd=f'cat {input_path} | ' +
                           f'{self.vidjil_post_cmd(output_path=output_path, sample_name=sample_name)}')
    
    def pipeline_cmd(self,
                     input_path: str | list[str],
                     output_path: str,
                     sample_name: str = 'clonotypes') -> PipelineCmd:
        cmd1 = self.pipeline_pre_cmd(input_path=input_path,
                                     output_path=output_path)
        cmd2 = self.pipeline_post_cmd(input_path=cmd1.output,
                                      output_path=output_path, 
                                      sample_name=sample_name)
        return PipelineCmd(input=cmd1.input,
                           output=cmd2.output,
                           cmd=cmd1.cmd + ' && ' + cmd2.cmd)


VidjilRead = namedtuple('VidjilRead', 'id flags seq')


_EXAMPLE = '''>A019:398:HLJSX5:43:26 + VJ 	1 98 132 150	 seed IGL SEG_+ 1.00e-01 9.71e-02/2.95e-03
GATCTCCATCCTCTTGGTCACGCTCCCTAAGAGCCTTCGGCTTCTTTCTCCCAGTTCTGGTCTCTGGGGCTGGC
CGCCGGTGGGCGGGAACAGCATCGA
CTCTCCTTCCCAC'''


def parse_vidjil_read(lines: str | list[str]) -> VidjilRead:
    if not isinstance(lines, list):
        lines = lines.split('\n')
    header = lines[0].split(' ')
    read_id = header[0][1:]
    vidjil_flags = [_.strip() for _ in ' '.join(header[1:]).split('\t')]
    sequence = ''.join(lines[1:])
    return VidjilRead(read_id, vidjil_flags, sequence)


# print(process_vidjil_read(_EXAMPLE))
# print(process_vidjil_read(_EXAMPLE.split('\n')))

# def read_vidjil(files : str | list[str] = ['./result/c1.detected.vdj.fa']):


# print(pipeline_cmd())
