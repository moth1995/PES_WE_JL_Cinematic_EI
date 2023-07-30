import io
import struct
import zlib
import csv
from typing import BinaryIO
import pathlib
import sys

class Camera():
    values = []
    def __init__(self, idx:int):
        self.idx = idx

    @property
    def full_data(self):
        return [self.idx] + self.values

class Cinematic():
    def __init__(self, idx: int, cameras: list, last_camera_idx:int, size_of_camera_data:int):
        self.idx = idx
        self.cameras = cameras
        self.last_camera_idx = last_camera_idx
        self.size_of_camera_data = size_of_camera_data

def import_csv_Values(bin_file_path: str, values:list, part_id:int):
    with open(bin_file_path, "r+b") as f:
        magic_number = f.read(4)
        if magic_number != magic_numbers[0]:
            raise Exception("Not a camera file")
        compress_size, uncompress_size = struct.unpack("<II", f.read(8))
        f.seek(32,0)
        uncompress_bin_file = io.BytesIO(zlib.decompress(f.read()))
        total_files, offset_files_table = struct.unpack("<II", uncompress_bin_file.read(8))
        uncompress_bin_file.seek(offset_files_table, 0)
        if part_id>=total_files:
            raise Exception("part id out of range")
        i = 0
        files_offset = []
        while i < total_files:
            file_offset = struct.unpack("<I", uncompress_bin_file.read(4))[0]
            files_offset.append(file_offset)
            i+=1
        uncompress_bin_file.seek(files_offset[part_id])
        uncompress_bin_file.seek(14,1)
        size_of_camera_data, offset_number_of_camera_view=  struct.unpack("<HI", uncompress_bin_file.read(6))
        uncompress_bin_file.seek(files_offset[part_id],0)
        uncompress_bin_file.seek(offset_number_of_camera_view,1)
        number_of_camera_view = struct.unpack("<I", uncompress_bin_file.read(4))[0] - 1
        uncompress_bin_file.read(number_of_camera_view * 4)
        # skip zeros
        uncompress_bin_file.read(4)
        for value in values:
            if len(value) != int(size_of_camera_data/2):
                raise Exception("Quantity of values to be insert doesn't match")
            # print(value)
            # print(struct.pack("<%dH" % int(size_of_camera_data/2), *value))
            # print(len(struct.pack("<%dH" % int(size_of_camera_data/2), *value)))
            uncompress_bin_file.write(struct.pack("<%dH" % int(size_of_camera_data/2), *value))
        uncompress_bin_file.seek(0,2)
        uncompress_file_size = uncompress_bin_file.tell()
        uncompress_bin_file.seek(0,0)
        compress_bin_file = zlib.compress(uncompress_bin_file.read(),level=9)
        compress_file_size = len(compress_bin_file)
    with open(bin_file_path, "wb") as f:
        f.write(magic_numbers[0])
        f.write(struct.pack("<2I",compress_file_size,uncompress_file_size))
        f.write(bytearray(20))
        f.write(compress_bin_file)

def read_cinematics_ids(f:BinaryIO):
    total_cinematics, cinematics_ids_offset = struct.unpack("<II",f.read(8))
    f.seek(cinematics_ids_offset,0)
    return [cinematic_idx for cinematic_idx in struct.unpack("<%dH" % total_cinematics, f.read(total_cinematics * 2))]
    
def read_cinematic(f:BinaryIO, idx: int):
    magic_number = f.read(8)
    if magic_number != magic_numbers[1]:
        raise Exception("Not a cinematic file")
    last_camera_idx = struct.unpack("<I", f.read(4))[0]
    f.read(2)
    size_of_camera_data = struct.unpack("<H", f.read(2))[0]
    offset_number_of_camera_view = struct.unpack("<I", f.read(4))[0]
    f.seek(offset_number_of_camera_view,0)
    number_of_camera_view = struct.unpack("<I", f.read(4))[0] - 1
    cameras = [Camera(struct.unpack("<I", f.read(4))[0]) for i in range(number_of_camera_view)]
    # skip zeros
    f.read(4)
    i = 0
    while i < number_of_camera_view:
        cameras[i].values = [value for value in struct.unpack("<%dH" % int(size_of_camera_data/2), f.read(size_of_camera_data))]
        i+=1
    return Cinematic(idx, cameras, last_camera_idx, size_of_camera_data)

if __name__ == "__main__":
    #file_path = "unknow_00315.str"
    #file_path = "unknow_00315.str_001.csv"

    total_arg = len(sys.argv)
    if total_arg != 2:
        raise Exception("Invalid quantity of arguments")
        exit()
    file_path = str(sys.argv[1])

    full_path = str(pathlib.Path(file_path).resolve())
    magic_numbers = [
        bytearray([0x00, 0x06, 0x01, 0x00]), 
        bytearray([0x07, 0x12, 0x01, 0x20, 0x02, 0x00, 0x00, 0x00]), 
        bytearray([0x00, 0x06, 0x01, 0x00]),
    ]
    if full_path.endswith("csv"):
        file_id = (int(full_path[-7:-4]))
        bin_file =full_path[:-8]
        with open(full_path, 'r') as f:
            csv_reader = csv.reader(f, delimiter=',')
            values = []
            for i, line in enumerate( csv_reader):
                if i == 0:
                    heading_index = [line.index(row) for row in line if "VALUE" in row]
                else:
                    val =[int(line[index]) for index in heading_index]
                    values.append(val)
            # print(values)
            try:
                import_csv_Values(bin_file, values, file_id)
            except Exception as e:
                print(e)
        exit()
    csv_headers = ["Cinematic ID", "Last Camera ID", "Size Of Camera Data", "Camera ID"]
    letters = [
        'a', 
        'b', 
        'c', 
        'd', 
        'e', 
        'f', 
        'g', 
        'h', 
        'i', 
        'j', 
        'k', 
        'l', 
        'm', 
        'n', 
        'o', 
        'p', 
        'q', 
        'r', 
        's', 
        't', 
        'u', 
        'v', 
        'w', 
        'x', 
        'y', 
        'z',
    ]
    csv_headers_letters = [
        "VALUE " + letter.upper()
        for letter in letters
    ]
    with open(file_path, "r+b") as f:
        magic_number = f.read(4)
        if magic_number != magic_numbers[0]:
            raise Exception("Not a camera file")
        compress_size, uncompress_size = struct.unpack("<II", f.read(8))
        f.seek(32,0)
        uncompress_bin_file = io.BytesIO(zlib.decompress(f.read()))
        total_files, offset_files_table = struct.unpack("<II", uncompress_bin_file.read(8))
        i = 0
        files = []
        previous_offset = uncompress_bin_file.tell()
        while i < total_files:
            uncompress_bin_file.seek(previous_offset, 0)
            file_offset = struct.unpack("<I", uncompress_bin_file.read(4))[0]
            previous_offset = uncompress_bin_file.tell()
            if i == total_files - 1:
                file_size = uncompress_size - file_offset
            else:
                next_file_offset = struct.unpack("<I", uncompress_bin_file.read(4))[0]
                file_size = next_file_offset - file_offset
            
            uncompress_bin_file.seek(file_offset, 0)
            #print(file_size)
            files.append(io.BytesIO(uncompress_bin_file.read(file_size)))
            i+=1
        cinematics_id_file = files[0]
        cinematics_files = files[1:]
        cinematics_ids = read_cinematics_ids(cinematics_id_file)
        cinematics_id_file.seek(0,0)
        cinematics = []
        
        for i, cinematic_file in enumerate(cinematics_files):
            with open("%s_%03d.bin" % (file_path, i+1), "wb") as f:
                #"%(num)03d" % {"num":5}
                try:
                    cinematics.append(read_cinematic(cinematic_file,cinematics_ids[i]))
                    cinematic_file.seek(0,0)
                    f.write(cinematic_file.read())
                except Exception as e:
                    print(e)
        for i, cinematic in enumerate(cinematics):
            with open("%s_%03d.csv" % (file_path,i+1), "w", encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(csv_headers + csv_headers_letters[:len(cinematic.cameras[0].values)])
                for camera in cinematic.cameras:
                    writer.writerow([cinematic.idx, cinematic.last_camera_idx, cinematic.size_of_camera_data] + camera.full_data )




