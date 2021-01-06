from google.cloud import speech
from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os

def create_new_bucket(bucket_name):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = "COLDLINE"
    new_bucket = storage_client.create_bucket(bucket)

    print(
        "Created bucket {} in {} with storage class {}".format(
            new_bucket.name, new_bucket.location, new_bucket.storage_class
        )
    )

def upload_file(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

def gstt(audio_dir, upload=False):    
    if False:
        create_new_bucket("audio-test-certify")

    bucket_name = "audio-test-certify"
        
    src_dir = audio_dir
    

    if upload:
        # upload all wav file in audio_dir to bucket
        for audio_name in os.listdir(src_dir):
            print("audio_name=", audio_name)
            print("extension=", audio_name[-3:])

            if audio_name[-3:] != "wav":
                continue
            
            source_file_name = os.path.join(src_dir, audio_name)

            destination_blob_name = audio_name
            print(bucket_name)
            print(source_file_name)
            print(destination_blob_name)
            upload_file(bucket_name, source_file_name, destination_blob_name)

    # gstt for each audio file
    for audio_name in os.listdir(src_dir):
        if audio_name[-3:] != "wav":
            continue
    
        gs_path = "gs://" + bucket_name + "/" + audio_name
        response = transcribe_gcs(gs_path)

        with open("gstt.txt", "w") as script:
            script.write(audio_name + "\n")
            for result in response.results:
                script.write(u'{}'.format(result.alternatives[0].transcript)+"\n")

    print("completed")

def transcribe_gcs(gcs_uri):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        # sample_rate_hertz=16000,
        language_code='ko-KR'
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result()

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))

    return response


