import os
from fastapi import APIRouter

router = APIRouter(prefix="/hpc")


@router.get("/")
def index():
    return "HPC APIs Index"


@router.get("/job_output/{jobID}")
async def getJobOutput(jobID, filepath: str):
    output = f"#######OUTPUT OF JOB {jobID}#######\n"
    try:
        with open(filepath, "r", encoding='utf-8', errors='ignore') as f:
            output += f.read()
    except Exception as error:
        print(f"failed to open file: {filepath}:")
        print(error)

    # print(output)
    return output


def get_size(file_path, unit='bytes'):
    file_size = os.path.getsize(file_path)
    exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
    if unit not in exponents_map:
        raise ValueError("Must select from \
        ['bytes', 'kb', 'mb', 'gb']")
    else:
        size = file_size / 1024 ** exponents_map[unit]
        return f"{round(size, 3)}{unit}"


@router.get("/filelist")
async def getJobOutput(output_dir: str):
    output = []
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} |
                          set(range(0x20, 0x100)) - {0x7f})

    def is_binary_string(bytes): return bool(bytes.translate(None, textchars))
    # is_binary_string(open('/usr/bin/python3', 'rb').read(1024))  # return True
    file_size_unit = 'kb'
    try:
        for dir_path, _, file_names in os.walk(output_dir):
            for file in file_names:
                file_path = os.path.join(dir_path, file)
                output.append({
                    'file_name': file,
                    'file_path': file_path,
                    'file_size': get_size(file_path, file_size_unit),
                    'is_binary': is_binary_string(open(file_path, 'rb').read(1024))
                    })
    except Exception as error:
        print(f"failed to list files from dir: {output_dir}:")
        print(error)
    if output == []:
        print(f"no files are found in the dir: {output_dir}")
    return output
