from google_stt import upload_file
import kakao_knt
import naver_crs
import google_stt
import argparse
import time
import os
import traceback

def implicit():
    try:
        from google.cloud import storage

        # If you don't specify credentials when constructing the client, the
        # client library will look for credentials in the environment.
        storage_client = storage.Client()

        # Make an authenticated API request
        buckets = list(storage_client.list_buckets())
        print(buckets)
    except:
        print("can't authenticate to google cloud platform")
        traceback.print_exc()

def convert_same_bitrate(origin_dir, target_dir, bitrate):
    for audio_name in os.listdir(origin_dir):
        # ffmpeg -i heykakao.wav newfile.wav -ar 16000
        converting_command = "ffmpeg -i " + origin_dir + "/" + audio_name + " -y " \
                            + target_dir + "/" + audio_name + " -ar " + str(bitrate)
        print()
        print(converting_command)
        os.system(converting_command)
        print()
    
if __name__ == "__main__":
    # implicit()
    parser = argparse.ArgumentParser(description='Check wav file via STTs')

    parser.add_argument('-k', dest="knt", help="kakao stt (knt)", action='store_true')
    parser.add_argument('-n', dest="csr", help="naver stt (crs)", action='store_true')
    parser.add_argument('-g', dest="gstt",help="google stt", action='store_true')

    parser.set_defaults(knt=False)
    parser.set_defaults(crs=False)
    parser.set_defaults(gstt=False)

    args = parser.parse_args()

    print(args)

    origin_audio_dir = os.path.join("audio", "origin")
    converted_audio_dir = os.path.join("audio", "convert")

    if True:
        convert_same_bitrate(origin_audio_dir, converted_audio_dir, 16000)

    start_time = time.time()

    if args.knt:
        kakao_knt.knt(converted_audio_dir)
    if args.csr:
        pass
    if args.gstt:
        google_stt.gstt(converted_audio_dir, upload=True)

    end_time = time.time()

    